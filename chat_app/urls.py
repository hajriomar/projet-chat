from django.urls import path
from . import views

urlpatterns = [
    # Quand on va sur /chat/, on appelle la vue 'index'
    path('', views.index, name='index'),
]