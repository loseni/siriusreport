from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("connexion/", include("connexion.urls")),  # Connexion app
    path("", include("reportingKYC.urls")),  # <--- ici, root URL va vers home
]
