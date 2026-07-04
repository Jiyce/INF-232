"""
Routeurs API pour les statistiques et analyses (Questions 1-4).

Ce module expose les endpoints REST pour accéder aux analyses statistiques,
au clustering et à la classification.
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
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
    calculate_elbow_method,
    perform_kmeans_clustering,
    generate_cluster_scatter_data,
    generate_elbow_plot,
    generate_interpretation_q3,
)
from app.services.classification import (
    prepare_data,
    train_decision_tree,
    train_knn,
    train_logistic_regression,
    generate_confusion_matrix_data,
    compare_models,
    generate_interpretation_q4,
)

router = APIRouter(tags=["statistics"])


def get_students_data(db: Session) -> tuple:
    """
    Récupère les données des élèves depuis la base de données.

    Args:
        db: Session SQLAlchemy

    Returns:
        tuple: (noms, notes, heures, orientations)
    """
    students = db.query(Student).all()
    if not students:
        raise HTTPException(status_code=404, detail="Aucun élève trouvé en base de données")

    noms = [s.nom for s in students]
    notes = [s.note_math for s in students]
    heures = [s.heures_etude for s in students]
    orientations = [s.orientation for s in students]

    return noms, notes, heures, orientations


@router.get("/question1", response_model=Dict[str, Any])
async def question1_stats(db: Session = Depends(get_db)):
    """
    Endpoint pour la Question 1 : Statistiques descriptives des notes.

    Returns:
        Dict[str, Any]: Statistiques descriptives et données des graphiques
    """
    noms, notes, _, _ = get_students_data(db)

    stats = calculate_descriptive_stats(notes, noms)
    histogram = generate_histogram_data(notes)
    boxplot = generate_boxplot_data(notes)
    interpretation = generate_interpretation_q1(stats)

    return {
        "question": "Statistiques Descriptives des Notes de Mathématiques",
        "stats": stats,
        "histogram": histogram,
        "boxplot": boxplot,
        "interpretation": interpretation,
    }


@router.get("/question2", response_model=Dict[str, Any])
async def question2_stats(db: Session = Depends(get_db)):
    """
    Endpoint pour la Question 2 : Analyse bivariée heures/notes.

    Returns:
        Dict[str, Any]: Statistiques bivariées et graphique scatter
    """
    _, notes, heures, _ = get_students_data(db)

    stats = calculate_bivariate_stats(heures, notes)
    scatter = generate_scatter_data(heures, notes, stats)
    interpretation = generate_interpretation_q2(stats)

    return {
        "question": "Analyse Bivariée : Heures d'Étude et Notes",
        "stats": stats,
        "scatter_plot": scatter,
        "interpretation": interpretation,
    }


@router.get("/question3", response_model=Dict[str, Any])
async def question3_clustering(
    n_clusters: int = 3,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour la Question 3 : Clustering K-Means.

    Args:
        n_clusters: Nombre de clusters (défaut: 3)

    Returns:
        Dict[str, Any]: Résultats du clustering et visualisations
    """
    _, notes, heures, _ = get_students_data(db)

    elbow_data = calculate_elbow_method(heures, notes)
    clustering_result = perform_kmeans_clustering(heures, notes, n_clusters)
    cluster_plot = generate_cluster_scatter_data(heures, notes, clustering_result)
    elbow_plot = generate_elbow_plot(elbow_data)
    interpretation = generate_interpretation_q3(clustering_result)

    return {
        "question": "Clustering K-Means des Profils d'Élèves",
        "elbow_data": elbow_data,
        "elbow_plot": elbow_plot,
        "clustering_result": clustering_result,
        "cluster_plot": cluster_plot,
        "interpretation": interpretation,
    }


@router.get("/question4", response_model=Dict[str, Any])
async def question4_classification(db: Session = Depends(get_db)):
    """
    Endpoint pour la Question 4 : Classification supervisée.

    Returns:
        Dict[str, Any]: Résultats des modèles de classification
    """
    _, notes, heures, orientations = get_students_data(db)

    X, y, orientation_map = prepare_data(heures, notes, orientations)

    # Entraînement des modèles
    dt_result = train_decision_tree(X, y)
    knn_result = train_knn(X, y)
    lr_result = train_logistic_regression(X, y)

    results = [dt_result, knn_result, lr_result]

    # Matrices de confusion
    confusion_matrices = []
    for result in results:
        cm_data = generate_confusion_matrix_data(
            result["actual"],
            result["predictions"],
            result["model"]
        )
        confusion_matrices.append({
            "model": result["model"],
            "matrix": cm_data,
        })

    # Comparaison des modèles
    comparison_plot = compare_models(results)

    # Interprétation
    interpretation = generate_interpretation_q4(results)

    return {
        "question": "Classification Supervisée pour l'Orientation",
        "orientation_map": orientation_map,
        "results": results,
        "confusion_matrices": confusion_matrices,
        "comparison_plot": comparison_plot,
        "interpretation": interpretation,
    }


@router.get("/all", response_model=Dict[str, Any])
async def all_analyses(db: Session = Depends(get_db)):
    """
    Endpoint pour récupérer toutes les analyses en une seule requête.

    Returns:
        Dict[str, Any]: Résultats des 4 questions
    """
    q1 = await question1_stats(db)
    q2 = await question2_stats(db)
    q3 = await question3_clustering(db=db)
    q4 = await question4_classification(db)

    return {
        "question1": q1,
        "question2": q2,
        "question3": q3,
        "question4": q4,
    }
