from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Base
from datetime import date


# Create your views here.
@login_required
def home(request):
    context = {"data": "data"}
    return render(request, "reportingKYC/accueil.html", context)


@login_required
def etatTraitement(request):
    bases = Base.objects.all()
    aujourdhui = date.today().isoformat()
    context = {"bases": bases, "aujourdhui": aujourdhui}
    return render(request, "reportingKYC/etatTraitement.html", context)

@login_required
def extractions(request):
    bases = Base.objects.all()
    aujourdhui = date.today().isoformat()
    context = {"bases": bases, "aujourdhui": aujourdhui}
    return render(request, "reportingKYC/extractions.html", context)
