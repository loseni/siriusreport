from django import forms
from .models import Base
from datetime import date


class EtattraitementForm(forms.Form):
    dateDebut = forms.DateField(
        label="Date de Debut",
        initial=date.today,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    dateFin = forms.DateField(
        label="Date de fin",
        initial=date.today,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    base = forms.ModelChoiceField(
        queryset=Base.objects.all(),
        empty_label="Toutes les bases",
        label="Base",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    def clean(self):
        cleanned_data = super().clean()
        dateDebut = cleaned_data.get('dateDebut')
        dateFin = cleaned_data.get('dateFin')
        if dateDebut and dateFin:
            if dateFin < dateDebut:
                raise forms.ValidationError('La date de fin doit être postérieure à la date de début.')
        return cleaned_data
        
