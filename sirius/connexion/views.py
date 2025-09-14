from django.shortcuts import render



# Create your views here.
def connexion(request):
    context = {"data": ""}
    return render(request, "connexion/connexion.html",context)