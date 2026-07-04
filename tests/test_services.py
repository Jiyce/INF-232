"""
Tests unitaires pour les services de l'application.

Ce module teste les fonctions de génération de données, statistiques,
clustering et classification.
"""

import pytest
import numpy as np
from typing import List

from app.services.data_generator import generate_students, generate_seed
from app.services.statistics import calculate_descriptive_stats
from app.services.bivariate import calculate_bivariate_stats
from app.services.clustering import calculate_elbow_method, perform_kmeans_clustering
from app.services.classification import prepare_data, train_decision_tree


class TestDataGenerator:
    """Tests pour le générateur de données."""

    def test_generate_seed_determinism(self):
        """Vérifie que le seed est déterministe."""
        seed1 = generate_seed("Dupont")
        seed2 = generate_seed("Dupont")
        assert seed1 == seed2

    def test_generate_seed_different_names(self):
        """Vérifie que des noms différents produisent des seeds différents."""
        seed1 = generate_seed("Dupont")
        seed2 = generate_seed("Martin")
        assert seed1 != seed2

    def test_generate_students_count(self):
        """Vérifie le nombre d'élèves générés."""
        students = generate_students("Dupont", count=100)
        assert len(students) == 100

    def test_generate_students_fields(self):
        """Vérifie que tous les champs sont présents."""
        students = generate_students("Dupont", count=10)
        for student in students:
            assert "nom" in student
            assert "note_math" in student
            assert "heures_etude" in student
            assert "orientation" in student
            assert student["orientation"] in ["Scientifique", "Littéraire"]

    def test_generate_students_notes_range(self):
        """Vérifie que les notes sont dans [0, 20]."""
        students = generate_students("Dupont", count=50)
        for student in students:
            assert 0 <= student["note_math"] <= 20

    def test_generate_students_hours_range(self):
        """Vérifie que les heures sont raisonnables."""
        students = generate_students("Dupont", count=50)
        for student in students:
            assert 0 <= student["heures_etude"] <= 40

    def test_determinism_same_seed(self):
        """Vérifie que le même seed produit les mêmes données."""
        students1 = generate_students("Dupont", count=50)
        students2 = generate_students("Dupont", count=50)
        for s1, s2 in zip(students1, students2):
            assert s1["nom"] == s2["nom"]
            assert abs(s1["note_math"] - s2["note_math"]) < 0.001
            assert abs(s1["heures_etude"] - s2["heures_etude"]) < 0.001


class TestStatistics:
    """Tests pour les statistiques descriptives."""

    def test_calculate_descriptive_stats(self):
        """Vérifie le calcul des statistiques de base."""
        notes = [10.0, 12.0, 14.0, 16.0, 8.1]
        noms = ["A", "B", "C", "D", "E"]
        stats = calculate_descriptive_stats(notes, noms)

        assert "moyenne" in stats
        assert "mediane" in stats
        assert "ecart_type" in stats
        assert stats["count"] == 5
        assert stats["moyenne"] == pytest.approx(12.0, abs=0.1)

    def test_stats_with_outliers(self):
        """Vérifie la détection des valeurs atypiques."""
        notes = [10.0, 11.0, 10.5, 10.2, 10.3, 20.0, 2.1]
        noms = ["A", "B", "C", "D", "E", "F", "G"]
        stats = calculate_descriptive_stats(notes, noms)

        assert len(stats["outliers"]) >= 1


class TestBivariate:
    """Tests pour l'analyse bivariée."""

    def test_calculate_bivariate_stats(self):
        """Vérifie le calcul de la corrélation."""
        heures = [5.0, 10.0, 15.0, 20.1, 8.1]
        notes = [8.0, 12.0, 16.0, 18.1, 10.1]
        stats = calculate_bivariate_stats(heures, notes)

        assert "correlation" in stats
        assert "r_squared" in stats
        assert "coefficient" in stats
        assert stats["correlation"] > 0  # Corrélation positive attendue

    def test_perfect_correlation(self):
        """Vérifie la corrélation parfaite."""
        heures = [1.0, 2.0, 3.0, 4.0, 5.1]
        notes = [2.0, 4.0, 6.0, 8.0, 10.1]
        stats = calculate_bivariate_stats(heures, notes)

        assert stats["correlation"] > 0.95
        assert stats["r_squared"] > 0.9


class TestClustering:
    """Tests pour le clustering K-Means."""

    def test_perform_kmeans(self):
        """Vérifie que le clustering fonctionne."""
        heures = [5.0, 6.0, 7.0, 15.0, 16.0, 17.0, 25.0, 26.0, 27.1]
        notes = [8.0, 9.0, 10.0, 12.0, 13.0, 14.0, 16.0, 17.0, 18.1]
        result = perform_kmeans_clustering(heures, notes, n_clusters=3)

        assert "labels" in result
        assert "silhouette_score" in result
        assert "cluster_stats" in result
        assert len(result["cluster_stats"]) == 3
        assert result["n_clusters"] == 3

    def test_elbow_method(self):
        """Vérifie la méthode du coude."""
        heures = list(range(1, 21))
        notes = [h * 0.5 + 5 for h in heures]
        elbow_data = calculate_elbow_method(heures, notes)

        assert "k_values" in elbow_data
        assert "inertias" in elbow_data
        assert len(elbow_data["k_values"]) == 9  # k=2 à k=10


class TestClassification:
    """Tests pour la classification supervisée."""

    def test_prepare_data(self):
        """Vérifie la préparation des données."""
        heures = [5.0, 10.0, 15.0, 20.1]
        notes = [8.0, 12.0, 16.0, 18.1]
        orientations = ["Scientifique", "Littéraire", "Scientifique", "Littéraire"]

        X, y, orientation_map = prepare_data(heures, notes, orientations)

        assert X.shape == (4, 2)
        assert len(y) == 4
        assert orientation_map["Scientifique"] == 0
        assert orientation_map["Littéraire"] == 1

    def test_train_decision_tree(self):
        """Vérifie l'entraînement de l'arbre de décision."""
        np.random.seed(42)
        heures = np.random.uniform(5, 25, 100).tolist()
        notes = [h * 0.5 + np.random.normal(5, 2) for h in heures]
        orientations = ["Scientifique" if n > 12 else "Littéraire" for n in notes]

        X, y, _ = prepare_data(heures, notes, orientations)
        result = train_decision_tree(X, y)

        assert "metrics" in result
        assert "accuracy" in result["metrics"]
        assert 1 >= result["metrics"]["accuracy"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
