// Gestion du basculement du statut des tables
function toggleTableStatus(tableId, element) {
    const url = `/admin/tables/table/${tableId}/toggle-status/`;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Mettre à jour l'interface utilisateur
            const statusBadge = document.querySelector(`#table-${tableId} .status-badge`);
            const statusCell = document.querySelector(`#table-${tableId} .status-cell`);
            const toggleButton = element;
            
            if (data.new_status === 'blocked') {
                statusBadge.className = 'status-badge blocked';
                statusBadge.textContent = 'Bloquée';
                toggleButton.innerHTML = '<i class="fas fa-unlock"></i>';
                toggleButton.title = 'Débloquer la table';
            } else {
                statusBadge.className = 'status-badge active';
                statusBadge.textContent = 'Active';
                toggleButton.innerHTML = '<i class="fas fa-lock"></i>';
                toggleButton.title = 'Bloquer la table';
            }
            
            // Afficher un message de succès
            const messages = document.getElementById('messages');
            if (messages) {
                const message = document.createElement('div');
                message.className = 'alert alert-success';
                message.role = 'alert';
                message.innerHTML = `Le statut de la table a été mis à jour avec succès.`;
                messages.appendChild(message);
                
                // Supprimer le message après 5 secondes
                setTimeout(() => {
                    message.remove();
                }, 5000);
            }
        } else {
            alert('Une erreur est survenue lors de la mise à jour du statut de la table.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de la communication avec le serveur.');
    });
    
    return false;
}

// Initialisation des tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips de Bootstrap si disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Gestion des messages flash
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 1000);
        }, 5000);
    });
});
