import logging
import pandas as pd
from .models import Agent, Base
from django.shortcuts import render
from datetime import date, datetime, time
from django.contrib.auth.decorators import login_required
from .forms import EtattraitementForm
from .services.extractions import (
    nettoyer_repertoire,
    recuperer_extraction,
    generer_liste_extractions,
)
from django.conf import settings

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
def home(request):
    bases = pd.DataFrame(
        {"bases": list(Base.objects.values_list("codeIsoBase", flat=True))}
    )
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
    logger.info("Chargement de la vue extractions")
    nettoyer_repertoire(settings.DOSSIER_EXTRACTIONS)

    if request.method == "POST":
        form = EtattraitementForm(request.POST)
        if form.is_valid():
            logger.info("Formulaire de traitement validé")
            date_debut = form.cleaned_data["dateDebut"]
            date_fin = form.cleaned_data["dateFin"]
            base = form.cleaned_data["base"]

            try:
                recuperer_extraction(date_debut, date_fin, base)
                logger.info(f"Extraction récupérée pour base {base}")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération : {e}")
        else:
            logger.warning("Formulaire invalide : %s", form.errors)
            return render(request, "reportingKYC/extractions.html", {"form": form})

    else:
        form = EtattraitementForm()

    resultats = generer_liste_extractions(settings.DOSSIER_EXTRACTIONS)
    context = {
        "form": form,
        "listeExtractionsRecues": resultats["fichiers"],
        "extractionsManquantes": resultats["extractionsManquantes"],
    }
    return render(request, "reportingKYC/extractions.html", context)
