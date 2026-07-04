"""
Générateur de données déterministe pour les élèves de Terminale.

Ce module génère des données scolaires réalistes de manière déterministe
à partir du nom du chef de groupe. Le même nom produira toujours
exactement les mêmes données.
"""

import hashlib
from typing import List, Dict, Any

import numpy as np

from app.config import DEFAULT_STUDENT_COUNT, SEED_PREFIX


# Listes de noms français pour générer des noms réalistes
PRENOMS_F = [
    "Marie", "Jeanne", "Françoise", "Monique", "Catherine", "Nathalie",
    "Isabelle", "Sylvie", "Christine", "Sandrine", "Stéphanie", "Sophie",
    "Valérie", "Véronique", "Laurence", "Alexandra", "Emilie", "Julie",
    "Camille", "Léa", "Manon", "Sarah", "Laura", "Clara", "Chloé",
    "Alice", "Emma", "Inès", "Jade", "Lola", "Zoé", "Lucie", "Margaux",
    "Romane", "Théa", "Lina", "Léna", "Anna", "Juliette", "Eva",
    "Rose", "Louise", "Ambre", "Maëlle", "Lily", "Anna", "Victoire",
    "Alix", "Charlotte", "Gabrielle", "Romy", "Sofia", "Agathe",
    "Joséphine", "Louna", "Mila", "Olivia", "Capucine", "Elena",
    "Apolline", "Léonie", "Mathilde", "Noémie", "Océane", "Pauline",
    "Quitterie", "Raphaëlle", "Salomé", "Tessa", "Ursule", "Violette",
    "Wendy", "Xénia", "Yasmine", "Zélie", "Adèle", "Bérénice",
    "Céleste", "Daphné", "Eléonore", "Fanny", "Garance", "Hortense",
    "Iris", "Jeanne", "Kassandra", "Ludivine", "Melissa", "Ninon",
    "Ophélie", "Priscille", "Quiéta", "Rebecca", "Ségolène", "Tatiana",
    "Uma", "Viviane", "Wanda", "Yana", "Zora"
]

PRENOMS_M = [
    "Jean", "Pierre", "Michel", "André", "Philippe", "René", "Louis",
    "Alain", "Jacques", "Bernard", "Marcel", "Daniel", "Roger", "Robert",
    "Paul", "Maurice", "Henri", "Georges", "Nicolas", "François",
    "Thomas", "Claude", "Éric", "Christian", "Patrick", "Christophe",
    "David", "Stéphane", "Laurent", "Sébastien", "Alexandre", "Maxime",
    "Quentin", "Alexis", "Julien", "Romain", "Antoine", "Baptiste",
    "Guillaume", "Lucas", "Théo", "Tom", "Nathan", "Enzo", "Mathis",
    "Louis", "Hugo", "Jules", "Gabriel", "Léo", "Raphaël", "Arthur",
    "Ethan", "Noah", "Maël", "Aaron", "Adam", "Ayoub", "Bastien",
    "Cédric", "Dorian", "Eliott", "Fabien", "Gabin", "Hadrien",
    "Ilan", "Johan", "Kenny", "Léandre", "Malo", "Nolan", "Oscar",
    "Paolo", "Robin", "Samuel", "Timéo", "Ugo", "Victor", "William",
    "Xavier", "Yanis", "Zacharie", "Adrien", "Benjamin", "Cyril",
    "Damien", "Esteban", "Florent", "Grégory", "Hector", "Isaac",
    "Jérôme", "Kylian", "Lilian", "Marin", "Noham", "Owen"
]

NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand",
    "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy",
    "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard", "Bonnet",
    "Dupont", "Lambert", "François", "Martinez", "Legrand", "Garnier",
    "Faure", "Rousseau", "Vincent", "Müller", "Lefranc", "Mercier", "Dupuy",
    "Lévy", "Clement", "Morin", "Marchand", "Duval", "Brun", "Hubert",
    "Perrin", "Moulin", "Louis", "Deschamps", "Hamon", "Rivière", "Bourgeois",
    "Picard", "André", "Masson", "Poirier", "Gauthier", "Maillard", "Marchal",
    "Gauthier", "Pereira", "Schmitt", "Jacob", "Lemaire", "Dufour", "Blanchard",
    "Barbier", "Gillet", "Chevalier", "Mallet", "Bouvier", "Michaud", "Delorme",
    "Lacroix", "Hébert", "Roussel", "Guichard", "Collin", "Tessier", "Joubert",
    "Benoit", "Hoarau", "Hardy", "Boucher", "Léger", "Valentin", "Fernandez",
    "Lopes", "Renaud", "Bazin", "Pichon", "Gros", "Raynaud", "Bodin", "Verdier",
    "Coulon", "Gomez", "Gonzalez", "Albert", "Chauvin", "Mallet", "Navarro",
    "Reynaud", "Antoine", "Lecomte", "Humbert", "Pons", "Masse", "Besnard",
    "Bousquet", "Brunet", "Ramos", "Gerard", "Langlois", "Lejeune", "Perrot",
    "Chambon", "Pelletier", "Boulanger", "Grondin", "Maire", "Jacquet",
    "Adam", "Legros", "Charles", "Joly", "Bouchet", "Benoît", "Rossi",
    "Gaudin", "Tanguy", "Rouault", "Thibault", "Goujon", "Charpentier",
    "Baudry", "Meyer", "Lucas", "Lombard", "Blanc", "Guerin", "Muller",
    "Genin", "Laporte", "Poulain", "Guyot", "Caron", "Lebrun", "Arnaud",
    "Maillet", "Leblanc", "Klein", "Carpentier", "Jourdain", "Delacroix",
    "Benard", "Mary", "Guillot", "Renard", "Milcent", "Godard", "Manuel",
    "Gay", "Bertin", "Pinot", "Pierre", "Breton", "Samson", "Huet",
    "Guillaume", "Roche", "Thierry", "Cohen", "Boulay", "Maury", "Schneider",
    "Maurice", "Savary", "Briand", "Keller", "Marion", "Baudin", "Marty",
    "Rémy", "Le Goff", "Perrier", "Le Roux", "Daniel", "Gilles", "Raymond",
    "Aubry", "Béraud", "Maillot", "Leduc", "Chéron", "Pannequin", "Blin",
    "Guillet", "Lecocq", "Perez", "Carlier", "Dumas", "Rousseaux", "Maillot",
    "Leroux", "Geoffroy", "Baudouin", "Chapelain", "Lecointe", "Oliveira",
    "Cousin", "Lamy", "Delattre", "Bourdon", "Morel", "Lebreton", "Grosjean",
    "Lepage", "Guillou", "Hamon", "Pichard", "Baudet", "Lecoq", "Delorme",
    "Chapuis", "Fleury", "Bouvier", "Lavigne", "Rousset", "Ledoux", "Guillon",
    "Bouillon", "Bousquet", "Lapierre", "Thibaud", "Mounier", "Hamard",
    "Rocher", "Pinet", "Gallet", "Chateau", "Bourgeois", "Leproux",
    "Delmas", "Perrault", "Girault", "Chauvet", "Boutin", "Laroche",
    "Gimenez", "Barre", "Lacombe", "Baudouin", "Martins", "Gomes",
    "Ferreira", "Lima", "Silva", "Santos", "Rodrigues", "Alves",
    "Fernandes", "Costa", "Oliveira", "Sousa", "Martins", "Johansen",
    "Nielsen", "Hansen", "Pedersen", "Andersen", "Jensen", "Larsen",
    "Sørensen", "Rasmussen", "Christensen", "Petersen", "Madsen",
    "Kristensen", "Eriksen", "Olsen", "Thomsen", "Christiansen"
]


def generate_seed(chef_groupe: str) -> int:
    """
    Génère une graine numérique déterministe à partir du nom du chef de groupe.

    La graine est créée en calculant le hash MD5 du nom (normalisé en minuscules
    sans espaces superflus), puis en convertissant les 8 premiers octets en entier.

    Args:
        chef_groupe: Nom complet du chef de groupe

    Returns:
        int: Graine numérique positive pour le générateur aléatoire

    Example:
        >>> generate_seed("Marie Curie")
        1234567890  # valeur déterministe
    """
    normalized = chef_groupe.strip().lower()
    hash_bytes = hashlib.md5(normalized.encode("utf-8")).digest()
    # Utilise les 8 premiers octets pour créer un entier 64 bits
    seed = int.from_bytes(hash_bytes[:8], byteorder="big")
    # S'assurer que la graine est positive et dans la plage de NumPy
    return abs(seed) % (2**32 - 1)


def generate_students(chef_groupe: str, count: int = DEFAULT_STUDENT_COUNT) -> List[Dict[str, Any]]:
    """
    Génère une liste d'élèves de Terminale de manière déterministe.

    À partir du nom du chef de groupe, cette fonction produit exactement
    les mêmes données à chaque appel. Les données sont réalistes et
    présentent des corrélations logiques entre heures d'étude et notes.

    Args:
        chef_groupe: Nom complet du chef de groupe (utilisé comme graine)
        count: Nombre d'élèves à générer (défaut: 250)

    Returns:
        List[Dict[str, Any]]: Liste des élèves avec leurs caractéristiques

    Structure d'un élève:
        - nom: str - Nom complet de l'élève
        - note_math: float - Note de mathématiques sur 20
        - heures_etude: float - Heures d'étude par semaine
        - orientation: str - "Scientifique" ou "Littéraire"
    """
    # Initialisation du générateur avec la graine déterministe
    seed = generate_seed(chef_groupe)
    rng = np.random.default_rng(seed)

    students = []

    # Génération des noms
    for i in range(count):
        # 50% de chances d'être une fille ou un garçon
        if rng.random() < 0.5:
            prenom = rng.choice(PRENOMS_F)
        else:
            prenom = rng.choice(PRENOMS_M)

        nom_famille = rng.choice(NOMS)
        nom_complet = f"{prenom} {nom_famille}"

        # Génération des heures d'étude (distribution normale tronquée)
        # Moyenne: 12h, écart-type: 4h, entre 2h et 30h
        heures = rng.normal(loc=12.0, scale=4.0)
        heures = max(2.0, min(30.0, heures))
        heures = round(heures, 1)

        # Génération de la note basée sur les heures d'étude avec bruit
        # Formule: note de base + coefficient * heures + bruit aléatoire
        # Cela crée une corrélation positive réaliste
        note_base = 5.0  # Note minimum théorique
        coefficient = 0.6  # Chaque heure apporte ~0.6 point
        bruit = rng.normal(loc=1.0, scale=2.5)  # Bruit centré sur 1 avec écart-type 2.5

        note = note_base + coefficient * heures + bruit

        # Tronquer dans une plage réaliste [4, 19]
        note = max(4.0, min(19.0, note))
        note = round(note, 2)

        # Déterminer l'orientation en fonction de la combinaison note + heures
        # Score combiné: plus il est élevé, plus l'orientation est scientifique
        score_combine = note + heures * 0.5

        # Seuil avec un peu d'aléatoire pour éviter une séparation trop nette
        seuil_scientifique = 22.1 + rng.normal(loc=0, scale=1.5)

        if score_combine >= seuil_scientifique:
            orientation = "Scientifique"
        else:
            orientation = "Littéraire"

        students.append({
            "nom": nom_complet,
            "note_math": note,
            "heures_etude": heures,
            "orientation": orientation,
        })

    return students


def get_generation_info(chef_groupe: str, count: int = DEFAULT_STUDENT_COUNT) -> Dict[str, Any]:
    """
    Retourne les informations sur la génération sans créer les données.

    Utile pour afficher un résumé avant la génération effective.

    Args:
        chef_groupe: Nom du chef de groupe
        count: Nombre d'élèves prévu

    Returns:
        Dict[str, Any]: Informations sur la génération (graine, nombre, etc.)
    """
    seed = generate_seed(chef_groupe)
    return {
        "chef_groupe": chef_groupe,
        "seed": seed,
        "count": count,
        "message": f"Génération déterministe de {count} élèves avec la graine {seed}"
    }
