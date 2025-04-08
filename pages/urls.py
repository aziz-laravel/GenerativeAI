from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name ='index'),
    path('', views.index, name='home'),
    path('generate/', views.generate_code, name ='llama')
]