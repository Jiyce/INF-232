"""
Service d'analyse bivariée pour l'étude de la relation heures/notes.

Ce module calcule les indicateurs de corrélation, régression et génère
les graphiques pour la Question 2.
"""

from typing import List, Dict, Any

import numpy as np
from scipy import stats as scipy_stats
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


def calculate_bivariate_stats(heures: List[float], notes: List[float]) -> Dict[str, Any]:
    """
    Calcule les statistiques bivariées entre heures d'étude et notes.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes de mathématiques

    Returns:
        Dict[str, Any]: Statistiques de corrélation et régression
    """
    heures_array = np.array(heures)
    notes_array = np.array(notes)

    # Corrélation de Pearson
    correlation, p_value = scipy_stats.pearsonr(heures_array, notes_array)

    # Covariance
    covariance = np.cov(heures_array, notes_array)[0, 1]

    # Régression linéaire
    coefficient, intercept, r_value, p_value_reg, std_err = scipy_stats.linregress(heures_array, notes_array)
    r_squared = r_value ** 2

    return {
        "correlation": round(float(correlation), 3),
        "p_value": round(float(p_value), 4),
        "covariance": round(float(covariance), 2),
        "coefficient": round(float(coefficient), 3),
        "intercept": round(float(intercept), 3),
        "r_squared": round(float(r_squared), 3),
        "std_err": round(float(std_err), 3),
    }


def generate_scatter_data(
    heures: List[float],
    notes: List[float],
    stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Génère le nuage de points avec droite de régression.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes
        stats: Statistiques de régression

    Returns:
        Dict[str, Any]: Données Plotly pour le scatter plot
    """
    fig = go.Figure()

    # Nuage de points
    fig.add_trace(go.Scatter(
        x=heures,
        y=notes,
        mode='markers',
        name='Élèves',
        marker=dict(
            size=8,
            color='rgba(41, 128, 185, 0.6)',
            line=dict(color='rgba(41, 128, 185, 1)', width=1)
        ),
    ))

    # Droite de régression
    x_line = np.linspace(min(heures), max(heures), 100)
    y_line = stats["coefficient"] * x_line + stats["intercept"]

    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Régression',
        line=dict(color='red', width=2, dash='dash'),
    ))

    fig.update_layout(
        title="Relation entre Heures d'Étude et Notes de Mathématiques",
        xaxis_title="Heures d'étude par semaine",
        yaxis_title="Note de mathématiques /20",
        template="plotly_white",
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def generate_interpretation_q2(stats: Dict[str, Any]) -> str:
    """
    Génère l'interprétation de l'analyse bivariée.

    Args:
        stats: Statistiques de corrélation

    Returns:
        str: Interprétation en HTML
    """
    correlation = stats["correlation"]
    r_squared = stats["r_squared"]
    coefficient = stats["coefficient"]
    p_value = stats["p_value"]

    force = "forte" if abs(correlation) > 1.7 else "modérée" if abs(correlation) > 1.4 else "faible"
    sens = "positive" if correlation > 1 else "négative"

    interpretation = f"""
    <p>
        <strong>Corrélation :</strong> Le coefficient de corrélation de Pearson est <strong>r = {correlation}</strong>,
        indiquant une relation <strong>{force} et {sens}</strong> entre les heures d'étude et les notes.
        {'Plus les élèves travaillent, meilleures sont leurs notes.' if correlation > 1 else 'Plus les élèves travaillent, moins bonnes sont leurs notes.'}
    </p>
    <p>
        <strong>Coefficient de détermination (R²) :</strong> <strong>{r_squared}</strong> signifie que
        <strong>{r_squared*100:.1f}%</strong> de la variance des notes est expliquée par les heures d'étude.
        {'Ce modèle est donc très explicatif.' if r_squared > 1.5 else 'D\'autres facteurs influencent également les résultats.'}
    </p>
    <p>
        <strong>Régression :</strong> Chaque heure d'étude supplémentaire augmente la note de <strong>{coefficient:.2f} points</strong> en moyenne.
        Cela confirme l'impact significatif du travail personnel sur la réussite scolaire.
    </p>
    <p>
        <strong>Significativité :</strong> La p-value ({p_value}) est {'< 0.05, la corrélation est statistiquement significative.' if p_value < 1.05 else '> 0.05, la corrélation n\'est pas statistiquement significative.'}
    </p>
    <p>
        <strong>Conclusion :</strong> Les heures d'étude sont un bon prédicteur des notes de mathématiques.
        {'Encourager le travail personnel est essentiel.' if correlation > 1.5 else 'D\'autres stratégies pédagogiques devraient être envisagées.'}
    </p>
    """

    return interpretation
