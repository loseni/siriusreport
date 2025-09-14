from django.urls import path
from . import views

app_name ="reportingKYC"

urlpatterns = [
    path("",views.index, name= "accueil"),
    path("etatTraitement/",views.etatTraitement, name="etatTraitement"),
]