# services/outlook.py
import os
import pythoncom
import win32com.client as win32
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)


def search_outlook_mails(
    folder_name,
    senders=None,
    subjects=None,
    date_after=None,
    date_before=None,
    attachments_subdir="attachments",
):
    pythoncom.CoInitialize()
    results = []

    try:
        outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
        folders = find_folders(outlook, folder_name)

        if not folders:
            logger.warning(f"Aucun dossier Outlook nommé '{folder_name}' trouvé.")
            return []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        attachments_dir = os.path.join(base_dir, attachments_subdir)
        os.makedirs(attachments_dir, exist_ok=True)

        for folder in folders:
            items = folder.Items
            items.Sort("[ReceivedTime]", True)

            restriction = []
            if date_after:
                restriction.append(
                    f"[ReceivedTime] >= '{date_after.strftime('%m/%d/%Y %I:%M %p')}'"
                )
            if date_before:
                restriction.append(
                    f"[ReceivedTime] <= '{date_before.strftime('%m/%d/%Y %I:%M %p')}'"
                )

            if restriction:
                query = " AND ".join(restriction)
                items = items.Restrict(query)

            for item in items:
                if item.Class != 43:
                    continue

                sender = (item.SenderEmailAddress or "").lower()
                subject = (item.Subject or "").lower()

                if senders and not any(s.lower() in sender for s in senders):
                    continue
                if subjects and not any(sub.lower() in subject for sub in subjects):
                    continue

                for attachment in item.Attachments:
                    try:
                        path = os.path.join(attachments_dir, attachment.FileName)
                        attachment.SaveAsFile(path)
                        logger.info(f"Fichier recçue : {attachment.FileName} ")
                    except Exception as e:
                        logger.warning(f"Erreur en sauvegardant une PJ : {e}")

                results.append(
                    {
                        "Sender": item.SenderName,
                        "Email": item.SenderEmailAddress,
                        "Subject": item.Subject,
                        "Date": item.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
                        "Folder": folder.FolderPath,
                    }
                )

        return results

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des mails : {e}")
        return []
    finally:
        pythoncom.CoUninitialize()


def find_folders(outlook, folder_name):
    found = []

    def search(folder):
        if folder.Name.lower() == folder_name.lower():
            found.append(folder)
        for sub in folder.Folders:
            search(sub)

    for root in outlook.Folders:
        search(root)

    return found
