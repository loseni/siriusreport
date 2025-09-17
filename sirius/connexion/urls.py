from django.urls import path
from . import views

app_name ="connexion"

urlpatterns = [
    #path("connexion/",views.connexion, name= "connexion"),
    path('', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]