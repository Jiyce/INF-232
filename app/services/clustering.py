"""
Service de clustering K-Means pour l'analyse des profils d'élèves.

Ce module implémente l'algorithme K-Means pour regrouper les élèves
selon leurs caractéristiques (notes et heures d'étude).
"""

from typing import List, Dict, Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


def calculate_elbow_method(heures: List[float], notes: List[float]) -> Dict[str, Any]:
    """
    Calcule la méthode du coude pour déterminer le nombre optimal de clusters.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes de mathématiques

    Returns:
        Dict[str, Any]: Données pour le graphique du coude
    """
    X = np.column_stack([heures, notes])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    inertias = []
    silhouette_scores = []
    k_range = range(2, 11)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(float(kmeans.inertia_))

        if k >= 2:
            labels = kmeans.labels_
            sil_score = silhouette_score(X_scaled, labels)
            silhouette_scores.append(float(sil_score))
        else:
            silhouette_scores.append(0.1)

    return {
        "k_values": list(k_range),
        "inertias": inertias,
        "silhouette_scores": silhouette_scores,
    }


def perform_kmeans_clustering(
    heures: List[float],
    notes: List[float],
    n_clusters: int = 3
) -> Dict[str, Any]:
    """
    Effectue le clustering K-Means sur les données des élèves.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes de mathématiques
        n_clusters: Nombre de clusters (défaut: 3)

    Returns:
        Dict[str, Any]: Résultats du clustering avec labels et centres
    """
    X = np.column_stack([heures, notes])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Calcul du score silhouette
    sil_score = silhouette_score(X_scaled, labels)

    # Centres des clusters (en coordonnées originales)
    centers_scaled = kmeans.cluster_centers_
    centers = scaler.inverse_transform(centers_scaled)

    # Statistiques par cluster
    cluster_stats = []
    for i in range(n_clusters):
        cluster_mask = labels == i
        cluster_heures = np.array(heures)[cluster_mask]
        cluster_notes = np.array(notes)[cluster_mask]

        cluster_stats.append({
            "cluster_id": i,
            "count": int(np.sum(cluster_mask)),
            "moyenne_heures": round(float(np.mean(cluster_heures)), 2),
            "moyenne_notes": round(float(np.mean(cluster_notes)), 2),
            "centre_heures": round(float(centers[i][0]), 2),
            "centre_notes": round(float(centers[i][1]), 2),
        })

    return {
        "labels": labels.tolist(),
        "silhouette_score": round(float(sil_score), 3),
        "cluster_stats": cluster_stats,
        "n_clusters": n_clusters,
    }


def generate_cluster_scatter_data(
    heures: List[float],
    notes: List[float],
    clustering_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Génère le graphique de dispersion des clusters.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes
        clustering_result: Résultats du clustering

    Returns:
        Dict[str, Any]: Données Plotly pour le scatter plot des clusters
    """
    labels = clustering_result["labels"]
    cluster_stats = clustering_result["cluster_stats"]

    fig = go.Figure()

    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

    for i, stats in enumerate(cluster_stats):
        cluster_mask = [l == i for l in labels]
        cluster_heures = [h for h, m in zip(heures, cluster_mask) if m]
        cluster_notes = [n for n, m in zip(notes, cluster_mask) if m]

        fig.add_trace(go.Scatter(
            x=cluster_heures,
            y=cluster_notes,
            mode='markers',
            name=f'Cluster {i+1} (n={stats["count"]})',
            marker=dict(
                size=10,
                color=colors[i % len(colors)],
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
        ))

    # Ajouter les centres
    for i, stats in enumerate(cluster_stats):
        fig.add_trace(go.Scatter(
            x=[stats["centre_heures"]],
            y=[stats["centre_notes"]],
            mode='markers',
            name=f'Centre {i+1}',
            marker=dict(
                size=15,
                color=colors[i % len(colors)],
                symbol='x',
                line=dict(width=2, color='black')
            ),
        ))

    fig.update_layout(
        title="Clustering K-Means des Profils d'Élèves",
        xaxis_title="Heures d'étude par semaine",
        yaxis_title="Note de mathématiques /20",
        template="plotly_white",
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def generate_elbow_plot(elbow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère le graphique de la méthode du coude.

    Args:
        elbow_data: Données de la méthode du coude

    Returns:
        Dict[str, Any]: Données Plotly pour le graphique du coude
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=elbow_data["k_values"],
        y=elbow_data["inertias"],
        mode='lines+markers',
        name='Inertie',
        line=dict(color='#3498db', width=2),
        marker=dict(size=8),
    ))

    fig.update_layout(
        title="Méthode du Coude pour Déterminer le Nombre Optimal de Clusters",
        xaxis_title="Nombre de clusters (k)",
        yaxis_title="Inertie (WCSS)",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def perform_kmeans_analysis(
    heures: List[float],
    notes: List[float],
    orientations: List[str],
    n_clusters: int = 3
) -> Dict[str, Any]:
    """
    Alias compatible avec l'API de pages.py qui passe (heures, notes, orientations).

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes de mathématiques
        orientations: Liste des orientations (ignoré pour le clustering)
        n_clusters: Nombre de clusters (défaut: 3)

    Returns:
        Dict[str, Any]: Résultats du clustering
    """
    return perform_kmeans_clustering(heures, notes, n_clusters)


# Alias pour compatibilité
generate_cluster_graphs = generate_cluster_scatter_data


def generate_interpretation_q3(clustering_result: Dict[str, Any]) -> str:
    """
    Génère l'interprétation du clustering.

    Args:
        clustering_result: Résultats du clustering

    Returns:
        str: Interprétation en HTML
    """
    n_clusters = clustering_result["n_clusters"]
    sil_score = clustering_result["silhouette_score"]
    cluster_stats = clustering_result["cluster_stats"]

    # Déterminer les profils
    profiles = []
    for stats in cluster_stats:
        if stats["moyenne_notes"] >= 14:
            profile = "élèves à fort potentiel"
        elif stats["moyenne_notes"] >= 10:
            profile = "élèves moyens"
        else:
            profile = "élèves en difficulté"

        if stats["moyenne_heures"] >= 12:
            profile += " travaillant beaucoup"
        elif stats["moyenne_heures"] >= 7:
            profile += " avec travail régulier"
        else:
            profile += " peu investis"

        profiles.append({
            "cluster_id": stats["cluster_id"] + 1,
            "profile": profile,
            "count": stats["count"],
            "note_moy": stats["moyenne_notes"],
            "heures_moy": stats["moyenne_heures"],
        })

    quality = "excellente" if sil_score > 0.6 else "bonne" if sil_score > 0.4 else "moyenne"

    html = f"""
    <p>
        <strong>Qualité du clustering :</strong> Le score silhouette est de <strong>{sil_score}</strong>,
        indiquant une qualité <strong>{quality}</strong> de la séparation des clusters.
    </p>
    <p>
        <strong>Nombre de clusters :</strong> L'algorithme a identifié <strong>{n_clusters} profils distincts</strong>
        parmi les {sum(p['count'] for p in profiles)} élèves analysés.
    </p>
    """

    for profile in profiles:
        html += f"""
    <p>
        <strong>Cluster {profile['cluster_id']} ({profile['count']} élèves) :</strong>
        {profile['profile']}. Moyenne : {profile['note_moy']}/20,
        {profile['heures_moy']} heures/semaine.
    </p>
        """

    html += """
    <p>
        <strong>Conclusion :</strong> Le clustering révèle des groupes homogènes d'élèves.
        Cette segmentation permet d'adapter les stratégies pédagogiques à chaque profil.
    </p>
    """

    return html
