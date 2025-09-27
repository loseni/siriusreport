# services/extractions.py
import os
import shutil
import pandas as pd
from datetime import datetime, time
import pytz
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings
from reportingKYC.models import Base
from .outlook import search_outlook_mails

logger = logging.getLogger(__name__)


def nettoyer_repertoire(repertoire):
    if os.path.exists(repertoire):
        for nom in os.listdir(repertoire):
            chemin = os.path.join(repertoire, nom)
            if os.path.isfile(chemin) or os.path.islink(chemin):
                os.unlink(chemin)
            elif os.path.isdir(chemin):
                shutil.rmtree(chemin)
        logger.info(f"Répertoire vidé : {repertoire}")
    else:
        logger.warning(f"Répertoire inexistant : {repertoire}")


def est_vide(repertoire):
    return not os.path.exists(repertoire) or len(os.listdir(repertoire)) == 0


def recuperer_extraction(date_debut, date_fin, base):
    logger.info("|----------------------Debut de recuperation des extractions --------------------------")
    tz = pytz.timezone("UTC")
    date_after = tz.localize(datetime.combine(date_debut, datetime.min.time()))
    date_before = tz.localize(datetime.combine(date_fin, time(23, 59, 59)))

    dossier = settings.DOSSIER_EXTRACTIONS
    dossier_mail = settings.DOSSIER_COMPLIANCE_EXTRACTIONS_OUTLOOK
    expediteurs = settings.EXPEDITEURS_EXTRACTIONS
    objets = settings.OBJETS_EXTRACTIONS

    mails = search_outlook_mails(
        folder_name=dossier_mail,
        senders=expediteurs,
        subjects=objets,
        date_after=date_after,
        date_before=date_before,
        attachments_subdir=dossier,
    )
    logger.info("|----------------------Fin de recuperation des extractions --------------------------")
    logger.info(f"{len(mails)} mails traités pour extraction")


def generer_liste_extractions(repertoire):
    if est_vide(repertoire):
        fichiers_df = pd.DataFrame(
            columns=["Base", "Activite", "Extraction", "Date", "Fichier"]
        )
        manquantes_df = pd.DataFrame(columns=["Base", "Extraction"])
    else:
        fichiers = [
            
            f for f in os.listdir(repertoire)
            if os.path.isfile(os.path.join(repertoire, f))
        ]
        fichiers_df = pd.DataFrame(fichiers, columns=["Fichier"])
        fichiers_df[["Alert", "Activite", "Extraction", "Base", "Date"]] = fichiers_df[
            "Fichier"
        ].str.split("_", expand=True)
        fichiers_df["Date"] = fichiers_df["Date"].str.slice(0, 10)

        bases = pd.DataFrame(
            {"Base": list(Base.objects.values_list("codeIsoBase", flat=True))}
        )
        extractions = pd.DataFrame({"Extraction": ["generation", "stock"]})
        attendues_df = bases.merge(extractions, how="cross")
        recues_df = fichiers_df[["Base", "Extraction"]].drop_duplicates()

        manquantes_df = (
            attendues_df.merge(recues_df, how="outer", indicator=True)
            .query('_merge == "left_only"')
            .drop("_merge", axis=1)
        )

        fichiers_df.drop(["Alert"], axis=1, inplace=True)
        fichiers_df = fichiers_df[["Base", "Activite", "Extraction", "Date", "Fichier"]]
        fichiers_df = fichiers_df.sort_values(
            by=["Base", "Extraction", "Fichier", "Date"]
        )

    return {
        "fichiers": _df_to_html(fichiers_df),
        "extractionsManquantes": _df_to_html(manquantes_df),
    }


def _df_to_html(df):
    if df.empty:
        return "<p>Aucune donnée</p>"

    html = df.to_html(classes="table table-sm table-hover", index=False)
    html = html.replace("<thead>", '<thead class="table-light">')
    html = html.replace("<th>", '<th scope="col">')
    return html
