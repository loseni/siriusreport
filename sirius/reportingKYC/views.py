from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Base
from datetime import date
from .forms import EtattraitementForm


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
    if request.method == 'POST':
        form = EtattraitementForm(request.POST)
        if form.is_valid():
            print("Extractions OK")
            

    else:
        form = EtattraitementForm()
        
    #context = {'form' :  form}
    return render(request, "reportingKYC/extractions.html", {'form' : form})

def recupererExtraction(request, dateDebut, dateFin, base):
    print(f"Date debut : {dateDebut} | Date Fin : {dateFin} | Base : {base}")