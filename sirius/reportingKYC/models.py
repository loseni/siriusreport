from django.db import models

# Create your models here.

class Base(models.Model):
    idBase = models.AutoField(primary_key=True)
    codeIsoBase = models.CharField(max_length=4,unique= True)
    libBase = models.CharField(max_length= 10, unique= True)
    typeBase = models.CharField(max_length= 10)
    descBase = models.CharField(max_length= 100, null= True, blank= True)
    
    class Meta:
        indexes = [
            models.Index(fields = ["codeIsoBase"])
        ]
    
    def __str__(self):
        return self.codeIsoBase
     
class Flag(models.Model):
    idFlag = models.AutoField(primary_key= True)
    libFlag = models.CharField(max_length=1 , unique=True, blank= True)
    descFlag = models.CharField(max_length=20)
    
    def __str__(self):
        return self.libFlag
    
class StatutAlert(models.Model):
    idStatut = models.AutoField(primary_key= True)
    libStatut = models.CharField(max_length=20, unique= True)
    descStatut = models.CharField(max_length=50)
    
    def __str__(self):
        return self.libStatut
    
class TypeAlerte(models.Model):
    idTypeAlerte = models.AutoField(primary_key= True)
    libTypeAlerte = models.CharField(max_length= 10, unique= True)
    descTypeAlerte = models.CharField(max_length= 30)
    
    def __str__(self):
        return self.libTypeAlerte
    
class TrancheAge(models.Model):
    idTrancheAge = models.AutoField(primary_key= True)
    borneInferieur = models.IntegerField()
    borneSuperieur = models.IntegerField()
    libTrancheAge = models.CharField(max_length= 50)
    
    def __str__(self):
        return self.libTrancheAge
        
class Agent(models.Model):
    idAgent = models.AutoField(primary_key= True)
    cuidAgent = models.CharField(max_length= 15, unique= True)
    nomAgent = models.CharField(max_length=100, null= True,blank= True)
    prenomAgent = models.CharField(max_length= 100, null= True,blank= True)
    profilAgent = models.CharField(max_length= 10,null= True,blank= True)
    statutAgent = models.CharField(max_length= 10,null= True,blank= True)
    
    def __str__(self):
        return self.cuidAgent
    
class Traitement(models.Model):
    idTraitement = models.AutoField(primary_key= True)
    idBase = models.ForeignKey(Base, on_delete=models.CASCADE)
    idFlag = models.ForeignKey(Flag, on_delete=models.CASCADE)
    idStatut = models.ForeignKey(StatutAlert, on_delete=models.CASCADE)
    idTypeAlerte = models.ForeignKey(TypeAlerte, on_delete=models.CASCADE)
    idAgent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    dateTraitement = models.DateField()
    nombreTraitement = models.IntegerField()
    
   
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['idTraitement', 'idBase', 'idFlag','idStatut', 'idTypeAlerte','idAgent', 'dateTraitement'], name='unique_cle_traitement')
        ]
    
class Stock(models.Model):
    idStock = models.AutoField(primary_key= True)
    idBase = models.ForeignKey(Base, on_delete=models.CASCADE)
    idFlag = models.ForeignKey(Flag, on_delete=models.CASCADE)
    idStatut = models.ForeignKey(StatutAlert, on_delete=models.CASCADE)
    idTypeAlerte = models.ForeignKey(TypeAlerte, on_delete=models.CASCADE)
    idTrancheAge = models.ForeignKey(TrancheAge, on_delete=models.CASCADE)
    dateStock = models.DateField()
    nombreStock = models.IntegerField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['idStock', 'idBase', 'idFlag','idStatut', 'idTypeAlerte', 'idTypeAlerte','dateStock'], name='unique_cle_stock')
        ]