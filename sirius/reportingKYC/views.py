from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Base, Agent
from datetime import date, datetime, time
from .forms import EtattraitementForm
from django.http import HttpResponse
import shutil
import win32com.client as win32
import pytz
import os
import pythoncom
from django.conf import settings
import pandas as pd
import re


# Create your views here.
@login_required
def home(request):
    chargerExtractions(settings.DOSSIER_EXTRACTIONS)
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
            dateDebut = form.cleaned_data['dateDebut']
            dateFin = form.cleaned_data['dateFin']
            base = form.cleaned_data['base']
            recupererExtraction(dateDebut, dateFin, base)
        else:
            print("Erreurs du formulaire:", form.errors)
            return render(request, "reportingKYC/extractions.html", {'form' : form})

    else:
        form = EtattraitementForm()

    extractionsRecues = listeExtractions(settings.DOSSIER_EXTRACTIONS)
    
    context = {'form' :  form, 'listeExtractionsRecues' : extractionsRecues}
    return render(request, "reportingKYC/extractions.html", context)

def recupererExtraction(dateDebut, dateFin, base):
    print(f"Date debut : {dateDebut} | Date Fin : {dateFin} | Base : {base}")
    

    # Initialisation de COM
    pythoncom.CoInitialize()

    try:
        tz = pytz.timezone("UTC")
        date_after = tz.localize(datetime.combine(dateDebut, datetime.min.time()))
        date_before = tz.localize(datetime.combine(dateFin, time(23,59,59)))
        
        dossierExtractions = settings.DOSSIER_EXTRACTIONS
        dossierExtractionsMail = settings.DOSSIER_COMPLIANCE_EXTRACTIONS_OUTLOOK
        expediteurExtractions = settings.EXPEDITEURS_EXTRACTIONS
        objetExtractions = settings.OBJETS_EXTRACTIONS
        
        supprimerExtractions(dossierExtractions)
        # Appel à la fonction de recherche des mails
        mails = search_outlook_mails(
            folder_name=dossierExtractionsMail,
            senders=expediteurExtractions,
            subjects=objetExtractions,
            date_after=date_after,
            date_before=date_before,
            attachments_subdir=dossierExtractions  # 🔹 sous-dossier relatif
        )
        
        
    
    except Exception as e:
        print(f"Erreur dans l'extraction : {e}")

    finally:
        # Désinitialisation de COM après usage
        pythoncom.CoUninitialize()


def find_folders(outlook, folder_name):
    """Recherche récursive d'un dossier Outlook (par nom) dans toutes les boîtes."""
    found_folders = []

    def search(folder, level=0):
        indent = "    " * level
        #print(f"{indent}📂 {folder.Name}")

        if folder.Name.lower() == folder_name.lower():
            #print(f"{indent}✅ Dossier trouvé : {folder.FolderPath}")
            found_folders.append(folder)

        for subfolder in folder.Folders:
            search(subfolder, level + 1)

    for store in outlook.Folders:
        #print(f"\n=== Boîte : {store.Name} ===")
        search(store)

    return found_folders

def supprimerExtractions(repertoire):
    if os.path.exists(repertoire):
        for nom in os.listdir(repertoire):
            chemin = os.path.join(repertoire, nom)
            if os.path.isfile(chemin) or os.path.islink(chemin):
                os.unlink(chemin)  # supprime fichier ou lien symbolique
            elif os.path.isdir(chemin):
                shutil.rmtree(chemin)  # supprime dossier et son contenu
        print(f"Contenu supprimé dans le répertoire : {repertoire}")
    else:
        print("Le répertoire spécifié n'existe pas.")


def listeExtractions(repertoire):

    if est_vide(repertoire):
        fichiers = pd.DataFrame(columns=['Base', 'Activite', 'Extraction','Date','Fichier'])
    else:  
        # Liste tous les éléments (fichiers et dossiers) dans le répertoire
        fichiers = os.listdir(repertoire)
        # Filtrer pour n'afficher que les fichiers
        fichiers = [fichier for fichier in fichiers if os.path.isfile(os.path.join(repertoire, fichier))]
        fichiers = pd.DataFrame(fichiers, columns =['Fichier'])
        fichiers[['Alert','Activite', 'Extraction','Base','Date']] = fichiers['Fichier'].str.split('_',expand=True)
        fichiers['Date'] = fichiers['Date'].str.slice(0,10)
        fichiers.drop(['Alert'], axis=1,inplace=True)
        fichiers = fichiers[['Base', 'Activite', 'Extraction','Date','Fichier']]
        fichiers = fichiers.sort_values(by=['Base','Extraction','Fichier', 'Date'])
    fichiers = fichiers.to_html(classes='table table-sm table-hover',index=False)
    fichiers = fichiers.replace('<thead>', '<thead class="table-light">')
    fichiers = fichiers.replace('<th>', '<th scope="col">')
    return fichiers

def search_outlook_mails(folder_name, senders=None, subjects=None, date_after=None, date_before=None, attachments_subdir="attachments"):
    # Initialisation de COM dans cette fonction aussi si nécessaire
    pythoncom.CoInitialize()

    try:
        outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
        results = []
        # Recherche de dossiers
        target_folders = find_folders(outlook, folder_name)
        if not target_folders:
            print(f"⚠️ Aucun dossier nommé '{folder_name}' trouvé.")
            return []
         
        base_dir = os.path.dirname(os.path.abspath(__file__))  # si script .py
        

        attachments_dir = os.path.join(base_dir, attachments_subdir)
        os.makedirs(attachments_dir, exist_ok=True)
        
        for folder in target_folders:
            print(f"\n📌 Analyse du dossier : {folder.FolderPath}")

            items = folder.Items
            items.Sort("[ReceivedTime]", True)

            # Restrict uniquement sur la période
            restriction = []
            if date_after:
                restriction.append(f"[ReceivedTime] >= '{date_after.strftime('%m/%d/%Y %I:%M %p')}'")
            if date_before:
                restriction.append(f"[ReceivedTime] <= '{date_before.strftime('%m/%d/%Y %I:%M %p')}'")

            if restriction:
                query = " AND ".join(restriction)
                print(f"🔎 Restrict appliqué : {query}")
                items = items.Restrict(query)

            count = 0
            for item in items:
                if item.Class != 43:  # pas un MailItem
                    continue

                match = True

                # 🔹 Vérification expéditeur
                if senders:
                    sender_email = (item.SenderEmailAddress or "").lower()
                    if not any(s.lower() in sender_email for s in senders):
                        match = False

                # 🔹 Vérification objet
                if subjects:
                    subject_text = (item.Subject or "").lower()
                    if not any(sub.lower() in subject_text for sub in subjects):
                        match = False

                if match:
                    count += 1
                    mail_info = {
                        "Sender": item.SenderName,
                        "Email": item.SenderEmailAddress,
                        "Subject": item.Subject,
                        "Date": item.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
                        "Folder": folder.FolderPath
                    }

                    for attachment in item.Attachments:
                        try:
                            save_path = os.path.join(attachments_dir, attachment.FileName)
                            attachment.SaveAsFile(save_path)
                            #print(f"📎 Pièce jointe sauvegardée : {save_path}")
                        except Exception as e:
                            print(f"⚠️ Erreur sauvegarde PJ : {e}")

                    results.append(mail_info)

            print(f"✅ {count} mails trouvés dans {folder.FolderPath}")
        return results

    except Exception as e:
        print(f"Erreur lors de la récupération des mails : {e}")
        return []
    finally:
        # Désinitialisation de COM après usage
        pythoncom.CoUninitialize()


def est_vide(repertoire):
    if os.path.exists(repertoire):
        return len(os.listdir(repertoire)) == 0
    else:
        print("Le répertoire spécifié n'existe pas.")
        return False

def chargerAgent():
    fichier_Agent = settings.FICHIER_AGENT
    agents = pd.read_csv(fichier_Agent,delimiter=';')
    agents_data = agents.to_dict(orient='records')
    agents = [Agent(**agent) for agent in agents_data]
    Agent.objects.bulk_create(agents)


def chargerExtractions(repertoire):
    if not est_vide(repertoire):
        fichiers = os.listdir(repertoire)
        fichiers = [fichier for fichier in fichiers if os.path.isfile(os.path.join(repertoire, fichier))]
        for fichier in fichiers:
            infosExtraction = re.split('[._]',fichier)
            extraction = infosExtraction[2]
            base = infosExtraction[3]
            dateDonnee = infosExtraction[4][0:10]
            print(f"Base : {base} | Extraction : {extraction} | Date : {dateDonnee}")
            alertes =  pd.read_csv(os.path.join(repertoire,fichier), sep='|',nrows=0)
           # if extraction == "generation"
            print(alertes)
                