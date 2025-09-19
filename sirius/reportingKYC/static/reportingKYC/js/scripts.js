document.addEventListener('DOMContentLoaded', function() {
        // Récupérer la date d'aujourd'hui
        const today = new Date().toISOString().split('T')[0]; // Format YYYY-MM-DD
        
        // Remplir les champs de date avec la date d'aujourd'hui
        document.getElementById('debutPeriode').value = today;
        document.getElementById('finPeriode').value = today;
    });
