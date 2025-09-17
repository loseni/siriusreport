from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def home(request):
    context = {"data": "data"}
    return render(request, "reportingKYC/accueil.html", context)

@login_required
def etatTraitement(request):
    context = {"data": "data"}
    return render(request, "reportingKYC/etatTraitement.html")