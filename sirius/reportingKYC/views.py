from django.shortcuts import render


# Create your views here.
def index(request):
    context = {"data": "data"}
    return render(request, "reportingKYC/accueil.html", context)

def etatTraitement(request):
    context = {"data": "data"}
    return render(request, "reportingKYC/etatTraitement.html")