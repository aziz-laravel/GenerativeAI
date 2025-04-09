from django.shortcuts import render
#from django.http import HttpResponse
# Create your views here.

#def index(request):
 #   return HttpResponse('Hello Azuz <3')

import requests
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import re
import subprocess

def index(request):
    return render(request, 'pages/index.html')

"""
CODE DE GEMINIIII ----------------------------------------------
@csrf_exempt
def generate_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')

        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        # Get Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({'error': 'Gemini API key not configured'}, status=500)

        try:
            # Configure the Gemini client
            genai.configure(api_key=api_key)

            # Load the Gemini model
            model = genai.GenerativeModel(model_name = 'gemini-1.5-flash')

            # Format prompt
            full_prompt = f"""
#Écris du code Python pour résoudre le problème suivant :
#{prompt}

#Assure-toi que le code soit fonctionnel, bien commenté et efficace.
"""

            # Generate the code
            response = model.generate_content(full_prompt)

            if response and response.text:
                # Optional: clean response if needed
                code_pattern = r"```python\s*(.*?)\s*```"
                code_match = re.search(code_pattern, response.text, re.DOTALL)
                clean_code = code_match.group(1) if code_match else response.text

                return JsonResponse({"response": clean_code})
            else:
                return JsonResponse({'error': 'No response from Gemini'}, status=500)

        except Exception as e:
            return JsonResponse({'error': 'Gemini request failed', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
"""


@csrf_exempt
def generate_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')

        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        try:
            full_prompt = f"""
Écris du code Python pour résoudre le problème suivant :
{prompt}

Assure-toi que le code soit fonctionnel, bien commenté et efficace.
"""

            result = subprocess.run(
                ['ollama', 'run', 'codellama', full_prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',  # 🔥 C'est ça qui corrige l'erreur !
                timeout=240
            )

            if result.returncode != 0:
                return JsonResponse({'error': 'Ollama execution failed', 'details': result.stderr}, status=500)

            response_text = result.stdout.strip()

            # Facultatif : extraire le code entre balises ```python ... ```
            code_pattern = r"```python\s*(.*?)\s*```"
            code_match = re.search(code_pattern, response_text, re.DOTALL)
            clean_code = code_match.group(1) if code_match else response_text

            return JsonResponse({'response': clean_code})

        except Exception as e:
            return JsonResponse({'error': 'Ollama request failed', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)