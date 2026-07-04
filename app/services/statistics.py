"""
Service de statistique descriptive pour l'analyse des notes.

Ce module calcule les indicateurs statistiques classiques et génère
les graphiques pour la Question 1.
"""

from typing import List, Dict, Any

import numpy as np
from scipy import stats as scipy_stats
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


def calculate_descriptive_stats(notes: List[float], noms: List[str]) -> Dict[str, Any]:
    """
    Calcule les statistiques descriptives complètes des notes.

    Args:
        notes: Liste des notes de mathématiques
        noms: Liste des noms des élèves

    Returns:
        Dict[str, Any]: Dictionnaire contenant toutes les statistiques
    """
    notes_array = np.array(notes)

    # Statistiques de base
    moyenne = float(np.mean(notes_array))
    mediane = float(np.median(notes_array))
    variance = float(np.var(notes_array, ddof=1))
    ecart_type = float(np.std(notes_array, ddof=1))
    minimum = float(np.min(notes_array))
    maximum = float(np.max(notes_array))
    etendue = maximum - minimum

    # Mode (peut y en avoir plusieurs)
    mode_result = scipy_stats.mode(notes_array, keepdims=True)
    mode_val = float(mode_result.mode[0]) if len(mode_result.mode) > 1 else float(notes_array[0])

    # Quartiles
    q1 = float(np.percentile(notes_array, 25))
    q2 = float(np.percentile(notes_array, 50))
    q3 = float(np.percentile(notes_array, 75))
    iqr = q3 - q1

    # Valeurs atypiques (méthode des IQR)
    borne_inf = q1 - 1.5 * iqr
    borne_sup = q3 + 1.5 * iqr

    outliers = []
    for i, note in enumerate(notes):
        if note < borne_inf or note > borne_sup:
            outliers.append({
                "nom": noms[i],
                "valeur": float(note),
            })

    return {
        "moyenne": round(moyenne, 2),
        "mediane": round(mediane, 2),
        "mode": round(mode_val, 2),
        "variance": round(variance, 2),
        "ecart_type": round(ecart_type, 2),
        "minimum": round(minimum, 2),
        "maximum": round(maximum, 2),
        "etendue": round(etendue, 2),
        "quartiles": {
            "q1": round(q1, 2),
            "q2": round(q2, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
        },
        "outliers": outliers,
        "count": len(notes),
    }


def generate_histogram_data(notes: List[float]) -> Dict[str, Any]:
    """
    Génère les données pour l'histogramme des notes.

    Args:
        notes: Liste des notes

    Returns:
        Dict[str, Any]: Données Plotly pour l'histogramme
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=notes,
        nbinsx=15,
        marker_color='rgba(41, 128, 185, 0.7)',
        marker_line_color='rgba(41, 128, 185, 1)',
        marker_line_width=1,
        name='Distribution',
    ))

    fig.add_vline(
        x=np.mean(notes),
        line_dash="dash",
        line_color="red",
        annotation_text="Moyenne",
        annotation_position="top"
    )

    fig.update_layout(
        title="Distribution des Notes de Mathématiques",
        xaxis_title="Note /20",
        yaxis_title="Fréquence",
        template="plotly_white",
        showlegend=False,
        height=400,
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def generate_boxplot_data(notes: List[float]) -> Dict[str, Any]:
    """
    Génère les données pour la boîte à moustaches.

    Args:
        notes: Liste des notes

    Returns:
        Dict[str, Any]: Données Plotly pour le boxplot
    """
    fig = go.Figure()

    fig.add_trace(go.Box(
        y=notes,
        name="Notes",
        boxpoints='outliers',
        marker_color='rgba(41, 128, 185, 0.7)',
        line_color='rgba(41, 128, 185, 1)',
    ))

    fig.update_layout(
        title="Boîte à Moustaches des Notes",
        yaxis_title="Note /20",
        template="plotly_white",
        showlegend=False,
        height=400,
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def generate_interpretation_q1(stats: Dict[str, Any]) -> str:
    """
    Génère une interprétation automatique des statistiques descriptives.

    Args:
        stats: Dictionnaire des statistiques calculées

    Returns:
        str: Interprétation en HTML
    """
    moyenne = stats["moyenne"]
    mediane = stats["mediane"]
    ecart_type = stats["ecart_type"]
    outliers_count = len(stats["outliers"])

    interpretation = f"""
    <p>
        <strong>Analyse de la distribution :</strong> La moyenne des notes est de <strong>{moyenne}/20</strong>,
        ce qui indique un niveau général {'satisfaisant' if moyenne >= 10 else 'à renforcer'}.
        La médiane ({mediane}/20) est {'proche de' if abs(moyenne - mediane) < 1 else 'éloignée de'} la moyenne,
        suggérant une distribution {'symétrique' if abs(moyenne - mediane) < 1 else 'asymétrique'}.
    </p>
    <p>
        <strong>Dispersion :</strong> L'écart-type de {ecart_type} points indique
        {'une forte' if ecart_type > 3 else 'une modérée' if ecart_type > 2 else 'une faible'} variabilité
        dans les performances des élèves. {'Les notes sont donc très dispersées.' if ecart_type > 3 else 'Les notes sont relativement homogènes.'}
    </p>
    <p>
        <strong>Valeurs atypiques :</strong> {outliers_count} valeur(s) atypique(s) {'ont été détectée(s)' if outliers_count > 1 else 'a été détectée'}.
        {'Ces élèves nécessitent une attention particulière.' if outliers_count > 1 else 'Cet élève nécessite une attention particulière.'}
    </p>
    <p>
        <strong>Conclusion :</strong> La classe présente un niveau {'homogène' if ecart_type < 2.5 else 'hétérogène'}.
        {'Une différenciation pédagogique serait bénéfique.' if ecart_type > 3 else 'La progression collective semble possible.'}
    </p>
    """

    return interpretation
