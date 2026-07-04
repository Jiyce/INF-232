"""
Routeurs API pour l'export des rapports PDF.

Ce module expose les endpoints pour générer et télécharger les rapports PDF.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.services.report_generator import generate_full_report, generate_summary_report
from app.services.statistics import calculate_descriptive_stats
from app.services.bivariate import calculate_bivariate_stats
from app.services.clustering import perform_kmeans_clustering
from app.services.classification import (
    prepare_data,
    train_decision_tree,
    train_knn,
    train_logistic_regression,
)

router = APIRouter(tags=["export"])


@router.post("/pdf")
async def export_pdf(
    include_q1: bool = Query(True, description="Inclure Question 1"),
    include_q2: bool = Query(True, description="Inclure Question 2"),
    include_q3: bool = Query(True, description="Inclure Question 3"),
    include_q4: bool = Query(True, description="Inclure Question 4"),
    db: Session = Depends(get_db)
):
    """
    Génère et retourne un rapport PDF complet.

    Args:
        include_q1: Inclure l'analyse descriptive
        include_q2: Inclure l'analyse bivariée
        include_q3: Inclure le clustering
        include_q4: Inclure la classification

    Returns:
        FileResponse: Fichier PDF téléchargeable
    """
    students = db.query(Student).all()
    if not students:
        raise HTTPException(status_code=404, detail="Aucun élève trouvé en base de données")

    noms = [s.nom for s in students]
    notes = [s.note_math for s in students]
    heures = [s.heures_etude for s in students]
    orientations = [s.orientation for s in students]

    # Préparation des données pour chaque question
    q1_stats = None
    q2_stats = None
    q3_result = None
    q4_results = None

    if include_q1:
        q1_stats = calculate_descriptive_stats(notes, noms)

    if include_q2:
        q2_stats = calculate_bivariate_stats(heures, notes)

    if include_q3:
        q3_result = perform_kmeans_clustering(heures, notes, n_clusters=3)

    if include_q4:
        X, y, _ = prepare_data(heures, notes, orientations)
        dt_result = train_decision_tree(X, y)
        knn_result = train_knn(X, y)
        lr_result = train_logistic_regression(X, y)
        q4_results = [dt_result, knn_result, lr_result]

    # Génération du PDF
    output_path = generate_full_report(
        students_data={"count": len(students)},
        q1_stats=q1_stats,
        q2_stats=q2_stats,
        q3_result=q3_result,
        q4_results=q4_results,
    )

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="rapport_analyse_terminale.pdf",
    )


@router.post("/pdf/summary")
async def export_summary_pdf(db: Session = Depends(get_db)):
    """
    Génère et retourne un rapport PDF de synthèse.

    Returns:
        FileResponse: Fichier PDF téléchargeable
    """
    students = db.query(Student).all()
    if not students:
        raise HTTPException(status_code=404, detail="Aucun élève trouvé en base de données")

    output_path = generate_summary_report(students_count=len(students))

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="rapport_synthese_terminale.pdf",
    )


@router.get("/status")
async def export_status(db: Session = Depends(get_db)):
    """
    Vérifie si des données sont disponibles pour l'export.

    Returns:
        dict: Statut de disponibilité
    """
    count = db.query(Student).count()
    return {
        "available": count > 0,
        "students_count": count,
        "message": f"{count} élèves disponibles pour l'export" if count > 1 else "Aucune donnée disponible",
    }
