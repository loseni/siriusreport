from django.db import models

# Create your models here.
class utilisateur(models.Model):
    idUtilisateur = models.AutoField(primary_key= True)
    cuidUtilisateur = models.CharField(max_length=10,unique=True,blank=False)
    nomUtilisateur = models.CharField(max_length=255)
    prenomUtilisateur = models.CharField(max_length=255)
    passwordUtilisateur = models.CharField(max_length=255)