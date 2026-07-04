"""
Service de classification supervisée pour prédire l'orientation des élèves.

Ce module implémente plusieurs algorithmes de classification :
- Arbre de décision
- K-Nearest Neighbors (KNN)
- Régression Logistique
"""

from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


def prepare_data(
    heures: List[float],
    notes: List[float],
    orientations: List[str]
) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
    """
    Prépare les données pour la classification.

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes
        orientations: Liste des orientations ("Scientifique" ou "Littéraire")

    Returns:
        Tuple: (X features, y labels encodés, mapping des classes)
    """
    X = np.column_stack([heures, notes])

    # Encodage des orientations
    orientation_map = {"Scientifique": 0, "Littéraire": 1}
    y = np.array([orientation_map[o] for o in orientations])

    return X, y, orientation_map


def train_decision_tree(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Entraîne un arbre de décision pour la classification.

    Args:
        X: Features (heures, notes)
        y: Labels encodés
        test_size: Proportion du jeu de test
        random_state: Graine aléatoire

    Returns:
        Dict[str, Any]: Résultats de l'arbre de décision
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Entraînement
    clf = DecisionTreeClassifier(max_depth=3, random_state=random_state)
    clf.fit(X_train, y_train)

    # Prédictions
    y_pred = clf.predict(X_test)

    # Métriques
    metrics = calculate_metrics(y_test, y_pred)

    # Importance des features
    feature_importance = {
        "heures_etude": round(float(clf.feature_importances_[0]), 3),
        "note_math": round(float(clf.feature_importances_[1]), 3),
    }

    # Règles de l'arbre
    tree_rules = export_text(clf, feature_names=["heures_etude", "note_math"])

    return {
        "model": "Decision Tree",
        "metrics": metrics,
        "feature_importance": feature_importance,
        "tree_rules": tree_rules,
        "predictions": y_pred.tolist(),
        "actual": y_test.tolist(),
    }


def train_knn(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
    n_neighbors: int = 5
) -> Dict[str, Any]:
    """
    Entraîne un classificateur KNN.

    Args:
        X: Features
        y: Labels
        test_size: Proportion du jeu de test
        random_state: Graine aléatoire
        n_neighbors: Nombre de voisins

    Returns:
        Dict[str, Any]: Résultats du KNN
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    clf = KNeighborsClassifier(n_neighbors=n_neighbors)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    metrics = calculate_metrics(y_test, y_pred)

    return {
        "model": "KNN",
        "metrics": metrics,
        "n_neighbors": n_neighbors,
        "predictions": y_pred.tolist(),
        "actual": y_test.tolist(),
    }


def train_logistic_regression(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Entraîne une régression logistique.

    Args:
        X: Features
        y: Labels
        test_size: Proportion du jeu de test
        random_state: Graine aléatoire

    Returns:
        Dict[str, Any]: Résultats de la régression logistique
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    clf = LogisticRegression(random_state=random_state, max_iter=1000)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    metrics = calculate_metrics(y_test, y_pred)

    # Coefficients
    coefficients = {
        "heures_etude": round(float(clf.coef_[0][0]), 4),
        "note_math": round(float(clf.coef_[0][1]), 4),
        "intercept": round(float(clf.intercept_[0]), 4),
    }

    return {
        "model": "Logistic Regression",
        "metrics": metrics,
        "coefficients": coefficients,
        "predictions": y_pred.tolist(),
        "actual": y_test.tolist(),
    }


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Calcule les métriques de performance d'un modèle.

    Args:
        y_true: Valeurs réelles
        y_pred: Prédictions

    Returns:
        Dict[str, Any]: Métriques de performance
    """
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 3),
        "precision": round(float(precision_score(y_true, y_pred, average="binary")), 3),
        "recall": round(float(recall_score(y_true, y_pred, average="binary")), 3),
        "f1_score": round(float(f1_score(y_true, y_pred, average="binary")), 3),
    }


def generate_confusion_matrix_data(
    y_true: List[int],
    y_pred: List[int],
    model_name: str
) -> Dict[str, Any]:
    """
    Génère la matrice de confusion sous forme de heatmap.

    Args:
        y_true: Valeurs réelles
        y_pred: Prédictions
        model_name: Nom du modèle

    Returns:
        Dict[str, Any]: Données Plotly pour la heatmap
    """
    cm = confusion_matrix(y_true, y_pred)

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=["Scientifique (Prédit)", "Littéraire (Prédit)"],
        y=["Scientifique (Réel)", "Littéraire (Réel)"],
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 16},
        colorscale="Blues",
        showscale=False,
    ))

    fig.update_layout(
        title=f"Matrice de Confusion - {model_name}",
        template="plotly_white",
        height=400,
        width=500,
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def compare_models(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare les performances des différents modèles.

    Args:
        results: Liste des résultats des modèles

    Returns:
        Dict[str, Any]: Données de comparaison
    """
    models = [r["model"] for r in results]
    accuracies = [r["metrics"]["accuracy"] for r in results]
    precisions = [r["metrics"]["precision"] for r in results]
    recalls = [r["metrics"]["recall"] for r in results]
    f1_scores = [r["metrics"]["f1_score"] for r in results]

    fig = go.Figure()

    fig.add_trace(go.Bar(name='Accuracy', x=models, y=accuracies, marker_color='#3498db'))
    fig.add_trace(go.Bar(name='Precision', x=models, y=precisions, marker_color='#2ecc71'))
    fig.add_trace(go.Bar(name='Recall', x=models, y=recalls, marker_color='#e74c3c'))
    fig.add_trace(go.Bar(name='F1-Score', x=models, y=f1_scores, marker_color='#f39c12'))

    fig.update_layout(
        title="Comparaison des Modèles de Classification",
        barmode='group',
        template="plotly_white",
        height=450,
        yaxis_title="Score",
        xaxis_title="Modèle",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


# Alias pour compatibilité avec les imports de pages.py
def perform_classification_analysis(heures: List[float], notes: List[float], orientations: List[str]) -> List[Dict[str, Any]]:
    """
    Effectue l'analyse de classification complète (alias pour compatibilité).

    Args:
        heures: Liste des heures d'étude
        notes: Liste des notes
        orientations: Liste des orientations

    Returns:
        List[Dict[str, Any]]: Résultats des trois modèles
    """
    X, y, _ = prepare_data(heures, notes, orientations)
    dt_result = train_decision_tree(X, y)
    knn_result = train_knn(X, y)
    lr_result = train_logistic_regression(X, y)
    return [dt_result, knn_result, lr_result]


def generate_classification_graphs(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Génère les graphiques de classification (alias pour compatibilité).

    Args:
        results: Résultats des modèles

    Returns:
        Dict[str, Any]: Graphiques de comparaison et matrices de confusion
    """
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

    comparison_plot = compare_models(results)

    return {
        "confusion_matrices": confusion_matrices,
        "comparison_plot": comparison_plot,
    }


def generate_interpretation_q4(results: List[Dict[str, Any]]) -> str:
    """
    Génère l'interprétation de la classification.

    Args:
        results: Résultats des modèles

    Returns:
        str: Interprétation en HTML
    """
    # Trouver le meilleur modèle
    best_model = max(results, key=lambda x: x["metrics"]["accuracy"])
    best_name = best_model["model"]
    best_acc = best_model["metrics"]["accuracy"]

    html = f"""
    <p>
        <strong>Meilleur modèle :</strong> <strong>{best_name}</strong> avec une accuracy de <strong>{best_acc}</strong>.
    </p>
    """

    for result in results:
        model = result["model"]
        metrics = result["metrics"]
        html += f"""
    <p>
        <strong>{model} :</strong> Accuracy={metrics['accuracy']}, Precision={metrics['precision']},
        Recall={metrics['recall']}, F1={metrics['f1_score']}.
    </p>
        """

    # Interprétation spécifique pour l'arbre de décision
    for result in results:
        if result["model"] == "Decision Tree" and "feature_importance" in result:
            fi = result["feature_importance"]
            most_important = max(fi, key=fi.get)
            html += f"""
    <p>
        <strong>Importance des variables (Arbre de Décision) :</strong>
        La variable la plus importante est <strong>{most_important}</strong> ({fi[most_important]}).
        {'Les notes de mathématiques sont le principal critère d\'orientation.' if most_important == 'note_math' else 'Les heures d\'étude sont un facteur clé dans l\'orientation.'}
    </p>
            """

    html += """
    <p>
        <strong>Conclusion :</strong> Les modèles confirment que les notes de mathématiques
        et les heures d'étude sont des prédicteurs fiables de l'orientation scientifique ou littéraire.
        L'arbre de décision offre l'avantage d'être interprétable.
    </p>
    """

    return html


def predict_orientation(
    heures: float,
    notes: float,
    model: Any
) -> str:
    """
    Prédit l'orientation d'un élève à partir de ses caractéristiques.

    Args:
        heures: Heures d'étude par semaine
        notes: Note de mathématiques
        model: Modèle entraîné

    Returns:
        str: Orientation prédite ("Scientifique" ou "Littéraire")
    """
    X = np.array([[heures, notes]])
    prediction = model.predict(X)[0]
    return "Scientifique" if prediction == 0 else "Littéraire"
