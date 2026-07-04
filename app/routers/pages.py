"""
Routeurs pour les pages HTML de l'application.

Ce module définit les routes qui rendent les templates Jinja2
pour l'interface utilisateur web.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.main import templates
from app.database import get_db
from app.services.student_service import get_all_students, get_students_count
from app.services.statistics import (
    calculate_descriptive_stats,
    generate_histogram_data,
    generate_boxplot_data,
    generate_interpretation_q1,
)
from app.services.bivariate import (
    calculate_bivariate_stats,
    generate_scatter_data,
    generate_interpretation_q2,
)
from app.services.clustering import (
    perform_kmeans_analysis,
    generate_cluster_graphs,
    generate_interpretation_q3,
)
from app.services.classification import (
    perform_classification_analysis,
    generate_classification_graphs,
    generate_interpretation_q4,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Page d'accueil de l'application.

    Args:
        request: Objet Request FastAPI

    Returns:
        TemplateResponse: Rendu de la page d'accueil
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/presentation", response_class=HTMLResponse)
async def presentation(request: Request):
    """
    Page de présentation du projet.

    Args:
        request: Objet Request FastAPI

    Returns:
        TemplateResponse: Rendu de la page de présentation
    """
    return templates.TemplateResponse("presentation.html", {"request": request})


@router.get("/generation", response_class=HTMLResponse)
async def generation(request: Request):
    """
    Page de génération des données.

    Args:
        request: Objet Request FastAPI

    Returns:
        TemplateResponse: Rendu de la page de génération
    """
    return templates.TemplateResponse("generation.html", {"request": request})


@router.get("/students", response_class=HTMLResponse)
async def students_list(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page listant tous les élèves avec statistiques.

    Args:
        request: Objet Request FastAPI
        db: Session de base de données

    Returns:
        TemplateResponse: Rendu de la page des élèves avec données
    """
    students = get_all_students(db)

    # Calculer les statistiques rapides
    total = len(students)
    avg_note = sum(s.note_math for s in students) / total if total > 1 else 1
    avg_heures = sum(s.heures_etude for s in students) / total if total > 1 else 1
    scientifique_count = sum(1 for s in students if s.orientation == "Scientifique")

    return templates.TemplateResponse(
        "students.html",
        {
            "request": request,
            "students": students,
            "total": total,
            "avg_note": avg_note,
            "avg_heures": avg_heures,
            "scientifique_count": scientifique_count,
        }
    )


@router.get("/question1", response_class=HTMLResponse)
async def question1(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page de la Question 1 : Statistique descriptive.

    Args:
        request: Objet Request FastAPI
        db: Session de base de données

    Returns:
        TemplateResponse: Rendu avec statistiques et graphiques
    """
    students = get_all_students(db)

    if not students:
        return templates.TemplateResponse(
            "question1.html",
            {"request": request, "stats": None, "graph_data": None, "interpretation": None}
        )

    notes = [s.note_math for s in students]
    noms = [s.nom for s in students]

    stats = calculate_descriptive_stats(notes, noms)
    graph_data = {
        "histogram": generate_histogram_data(notes),
        "boxplot": generate_boxplot_data(notes),
    }
    interpretation = generate_interpretation_q1(stats)

    return templates.TemplateResponse(
        "question1.html",
        {
            "request": request,
            "stats": stats,
            "graph_data": graph_data,
            "interpretation": interpretation,
        }
    )


@router.get("/question2", response_class=HTMLResponse)
async def question2(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page de la Question 2 : Analyse bivariée.

    Args:
        request: Objet Request FastAPI
        db: Session de base de données

    Returns:
        TemplateResponse: Rendu avec analyses de corrélation
    """
    students = get_all_students(db)

    if not students:
        return templates.TemplateResponse(
            "question2.html",
            {"request": request, "stats": None, "graph_data": None, "interpretation": None}
        )

    heures = [s.heures_etude for s in students]
    notes = [s.note_math for s in students]

    stats = calculate_bivariate_stats(heures, notes)
    graph_data = {
        "scatter": generate_scatter_data(heures, notes, stats),
    }
    interpretation = generate_interpretation_q2(stats)

    return templates.TemplateResponse(
        "question2.html",
        {
            "request": request,
            "stats": stats,
            "graph_data": graph_data,
            "interpretation": interpretation,
        }
    )


@router.get("/question3", response_class=HTMLResponse)
async def question3(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page de la Question 3 : Classification non supervisée.

    Args:
        request: Objet Request FastAPI
        db: Session de base de données

    Returns:
        TemplateResponse: Rendu avec clusters K-Means
    """
    students = get_all_students(db)

    if not students:
        return templates.TemplateResponse(
            "question3.html",
            {"request": request, "results": None, "graph_data": None, "interpretation": None}
        )

    heures = [s.heures_etude for s in students]
    notes = [s.note_math for s in students]
    orientations = [s.orientation for s in students]

    raw_results = perform_kmeans_analysis(heures, notes, orientations)

    # Transformer les résultats pour correspondre au template
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    clusters_info = []
    for i, stats in enumerate(raw_results["cluster_stats"]):
        # Calculer le % scientifique pour ce cluster
        cluster_mask = [l == i for l in raw_results["labels"]]
        cluster_orientations = [o for o, m in zip(orientations, cluster_mask) if m]
        pct_sci = (sum(1 for o in cluster_orientations if o == "Scientifique") / len(cluster_orientations) * 100) if cluster_orientations else 0

        # Description du profil
        if stats["moyenne_notes"] >= 14:
            desc = "élèves à fort potentiel"
        elif stats["moyenne_notes"] >= 10:
            desc = "élèves moyens"
        else:
            desc = "élèves en difficulté"

        if stats["moyenne_heures"] >= 12:
            desc += " travaillant beaucoup"
        elif stats["moyenne_heures"] >= 7:
            desc += " avec travail régulier"
        else:
            desc += " peu investis"

        clusters_info.append({
            "id": stats["cluster_id"],
            "size": stats["count"],
            "avg_note": stats["moyenne_notes"],
            "avg_heures": stats["moyenne_heures"],
            "pct_scientifique": pct_sci,
            "description": desc,
            "color": colors[i % len(colors)],
        })

    results = {
        "optimal_k": raw_results["n_clusters"],
        "clusters_info": clusters_info,
        "silhouette_score": raw_results["silhouette_score"],
    }

    # Générer les graphiques
    from app.services.clustering import calculate_elbow_method, generate_elbow_plot
    elbow_data = calculate_elbow_method(heures, notes)

    # Générer un graphique silhouette simple
    import plotly.graph_objects as go
    from plotly.utils import PlotlyJSONEncoder
    import json
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=elbow_data["k_values"],
        y=elbow_data["silhouette_scores"],
        mode='lines+markers',
        line=dict(color='#2ecc71', width=2),
        marker=dict(size=8),
    ))
    fig.update_layout(
        title="Score de Silhouette par Nombre de Clusters",
        xaxis_title="Nombre de clusters (k)",
        yaxis_title="Score de silhouette",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    graph_data = {
        "clusters": generate_cluster_graphs(heures, notes, raw_results),
        "elbow": generate_elbow_plot(elbow_data),
        "silhouette": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
    }

    interpretation = generate_interpretation_q3(raw_results)

    return templates.TemplateResponse(
        "question3.html",
        {
            "request": request,
            "results": results,
            "graph_data": graph_data,
            "interpretation": interpretation,
        }
    )


@router.get("/question4", response_class=HTMLResponse)
async def question4(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page de la Question 4 : Classification supervisée.

    Args:
        request: Objet Request FastAPI
        db: Session de base de données

    Returns:
        TemplateResponse: Rendu avec classification
    """
    students = get_all_students(db)

    if not students:
        return templates.TemplateResponse(
            "question4.html",
            {"request": request, "results": None, "graph_data": None, "interpretation": None}
        )

    heures = [s.heures_etude for s in students]
    notes = [s.note_math for s in students]
    orientations = [s.orientation for s in students]

    raw_results = perform_classification_analysis(heures, notes, orientations)

    # Le template attend un seul résultat avec .accuracy, .precision, etc.
    # On prend le premier modèle (Decision Tree) comme résultat principal
    # et on construit la matrice de confusion
    dt_result = raw_results[0]  # Decision Tree (index 0)
    metrics = dt_result["metrics"]

    # Construire la matrice de confusion à partir des prédictions
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(dt_result["actual"], dt_result["predictions"])

    results = {
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": cm.tolist(),
        "model_name": dt_result["model"],
    }

    graph_data = generate_classification_graphs(raw_results)
    # Adapter le format pour le template qui attend graph_data.confusion et graph_data.models
    template_graph_data = {
        "confusion": graph_data["confusion_matrices"][0]["matrix"] if graph_data["confusion_matrices"] else {},
        "models": graph_data["comparison_plot"],
    }

    interpretation = generate_interpretation_q4(raw_results)

    return templates.TemplateResponse(
        "question4.html",
        {
            "request": request,
            "results": results,
            "graph_data": template_graph_data,
            "interpretation": interpretation,
        }
    )


@router.get("/export", response_class=HTMLResponse)
async def export_page(request: Request):
    """
    Page d'export PDF.

    Args:
        request: Objet Request FastAPI

    Returns:
        TemplateResponse: Rendu de la page d'export
    """
    return templates.TemplateResponse("export.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    Page à propos.

    Args:
        request: Objet Request FastAPI

    Returns:
        TemplateResponse: Rendu de la page à propos
    """
    return templates.TemplateResponse("about.html", {"request": request})
