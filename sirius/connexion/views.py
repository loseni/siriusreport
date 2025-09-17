from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def connexion(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('reportingKYC:home')  # ou autre nom de vue
        else:
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
    return render(request, 'connexion/connexion.html')

@login_required
def deconnexion(request):
    logout(request)  # supprime la session utilisateur
    return redirect('connexion:connexion') 