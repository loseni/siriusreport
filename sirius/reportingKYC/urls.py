from django.urls import path
from . import views

app_name ="reportingKYC"

urlpatterns = [
    path('', views.home, name='home'),
    path("etatTraitement/",views.etatTraitement, name="etatTraitement"),
    path('extractions/',views.extractions, name= 'extractions'),
] 