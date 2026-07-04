/**
 * Lycée Analytics - JavaScript principal
 * Gestion des interactions et appels API
 */

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lycée Analytics - Application chargée');

    // Activer les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Gestionnaire pour le formulaire de génération
    const generationForm = document.getElementById('generationForm');
    if (generationForm) {
        generationForm.addEventListener('submit', handleGeneration);
    }

    // Gestionnaire pour la prédiction Q2
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', handlePrediction);
    }
});

/**
 * Gère la soumission du formulaire de génération de données
 */
async function handleGeneration(event) {
    event.preventDefault();

    const chefGroupe = document.getElementById('chefGroupe').value;
    const count = document.getElementById('studentCount').value || 250;
    const resultDiv = document.getElementById('generationResult');
    const spinner = document.getElementById('generationSpinner');

    if (!chefGroupe.trim()) {
        showAlert('Veuillez entrer le nom du chef de groupe.', 'warning');
        return;
    }

    // Afficher le spinner
    if (spinner) spinner.classList.remove('d-none');
    if (resultDiv) resultDiv.innerHTML = '';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chef_groupe: chefGroupe,
                count: parseInt(count)
            })
        });

        const data = await response.json();

        if (response.ok) {
            showGenerationResult(data, resultDiv);
            showAlert('Données générées avec succès !', 'success');
        } else {
            showAlert(data.detail || 'Erreur lors de la génération.', 'danger');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur de connexion au serveur.', 'danger');
    } finally {
        if (spinner) spinner.classList.add('d-none');
    }
}

/**
 * Affiche le résultat de la génération
 */
function showGenerationResult(data, container) {
    if (!container) return;

    const html = `
        <div class="alert alert-success">
            <h5><i class="bi bi-check-circle-fill me-2"></i>${data.message}</h5>
            <div class="row mt-3">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${data.new_count}</div>
                        <div class="stat-label">Élèves générés</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${data.statistics.note_moyenne}/20</div>
                        <div class="stat-label">Note moyenne</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${data.statistics.heures_moyennes}h</div>
                        <div class="stat-label">Heures moyennes</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-value">${data.statistics.scientifique}</div>
                        <div class="stat-label">Scientifiques</div>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <a href="/students" class="btn btn-primary">
                    <i class="bi bi-people me-2"></i>Voir les élèves
                </a>
                <a href="/question1" class="btn btn-outline-primary ms-2">
                    <i class="bi bi-graph-up me-2"></i>Voir les analyses
                </a>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

/**
 * Gère la prédiction de note (Question 2)
 */
async function handlePrediction(event) {
    event.preventDefault();

    const heures = document.getElementById('predictionHeures').value;
    const resultDiv = document.getElementById('predictionResult');

    if (!heures || heures < 1 || heures > 40) {
        showAlert('Veuillez entrer un nombre d\'heures valide (1-40).', 'warning');
        return;
    }

    try {
        const response = await fetch(`/api/stats/predict?heures=${heures}`);
        const data = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="alert alert-info mt-3">
                    <h6><i class="bi bi-magic me-2"></i>Prédiction</h6>
                    <p class="mb-0">
                        Pour un élève étudiant <strong>${heures} heures</strong> par semaine,
                        la note prédite est <strong>${data.note_predite}/20</strong>.
                    </p>
                    <small class="text-muted">
                        Basé sur la droite de régression : y = ${data.coefficient.toFixed(2)}x + ${data.intercept.toFixed(2)}
                    </small>
                </div>
            `;
        } else {
            showAlert(data.detail || 'Erreur lors de la prédiction.', 'danger');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur de connexion.', 'danger');
    }
}

/**
 * Affiche une alerte temporaire
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer') || document.body;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alertDiv);

    // Auto-fermeture après 5 secondes
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5001);
}

/**
 * Exporte un graphique Plotly en image PNG
 */
function exportPlot(graphId, filename) {
    const graph = document.getElementById(graphId);
    if (graph) {
        Plotly.downloadImage(graph, {
            format: 'png',
            filename: filename,
            height: 600,
            width: 800
        });
    }
}

/**
 * Rafraîchit les données d'une page
 */
async function refreshData(endpoint, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '<div class="spinner-container"><div class="spinner-border text-primary"></div></div>';

    try {
        const response = await fetch(endpoint);
        const data = await response.json();

        if (response.ok) {
            // La mise à jour spécifique est gérée par chaque page
            location.reload();
        } else {
            showAlert('Erreur lors du rafraîchissement.', 'danger');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur de connexion.', 'danger');
    }
}

// Export des fonctions pour utilisation globale
window.showAlert = showAlert;
window.exportPlot = exportPlot;
window.refreshData = refreshData;
