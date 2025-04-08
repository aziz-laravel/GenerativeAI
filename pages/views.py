from django.shortcuts import render
#from django.http import HttpResponse
# Create your views here.

#def index(request):
 #   return HttpResponse('Hello Azuz <3')

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import re

def index(request):
    return render(request, 'pages/index.html')

@csrf_exempt
def generate_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')

        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        # Utilisation de l'API Hugging Face
        api_key = os.getenv("HF_API_KEY")
        if not api_key:
            return JsonResponse({'error': 'API key not configured'}, status=500)
            
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Formatage du prompt pour CodeLlama
        formatted_prompt = f"""
        Écris du code Python pour résoudre le problème suivant:
        {prompt}
        
        Assure-toi que le code soit fonctionnel, bien commenté et efficace.
        
        ```python
        """

        # Configuration pour CodeLlama
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "temperature": 0.2,  # Valeur plus basse pour du code plus précis
                "max_new_tokens": 500,  # Plus de tokens pour avoir un code complet
                "do_sample": True,
                "top_p": 0.95,
                "return_full_text": False  # Pour ne pas renvoyer le prompt
            }
        }

        # URL pour CodeLlama
        model_url = "https://api-inference.huggingface.co/models/Salesforce/codegen-350M-mono"
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # Extraction du code Python généré
                generated_text = result[0].get("generated_text", "")
                
                # Nettoyage du résultat pour extraire uniquement le code
                code_pattern = r"```python\s*(.*?)\s*```"
                code_match = re.search(code_pattern, generated_text, re.DOTALL)
                
                if code_match:
                    clean_code = code_match.group(1)
                else:
                    # Si le modèle n'a pas utilisé les délimiteurs de code
                    clean_code = generated_text
                
                return JsonResponse({"response": clean_code})
            else:
                error_message = f"Erreur {response.status_code}: {response.text}"
                print(error_message)  # Pour le débogage
                return JsonResponse({'error': 'LLM API error', 'details': error_message}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': 'Request failed', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)