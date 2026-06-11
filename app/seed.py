"""
seed.py — Données initiales de la bibliothèque.

Ce script est appelé automatiquement au démarrage de l'app (voir main.py).
Il insère les livres uniquement si la table est vide, donc il est idempotent :
relancer l'app ne crée pas de doublons.

Pour ajouter des livres : compléter la liste BOOKS ci-dessous et redéployer.
"""

from app.database import SessionLocal
from app.models import Book

BOOKS = [
    # (title, author, type, status)
    # type : roman | essai_philo | essai_politique | socio
    # status : en_cours | terminé
    ("Les Raisins de la Colère",              "John Steinbeck",           "roman",           "terminé"),
    ("Crime et Châtiment",                    "Fedor Dostoïevski",        "roman",           "terminé"),
    ("Etoile Rouge",                          "Florian Ferrier",          "roman",           "terminé"),
    ("La Condition Humaine",                  "André Malraux",            "roman",           "terminé"),
    ("1984",                                  "George Orwell",            "roman",           "terminé"),
    ("Voyage au bout de la nuit",             "Céline",                   "roman",           "en_cours"),
    ("L'étranger",                            "Albert Camus",             "roman",           "terminé"),
    ("La Plaisanterie",                       "Kundera",                  "roman",           "terminé"),
    ("Jacaranda",                             "Gael Faye",                "roman",           "terminé"),
    ("Petit Pays",                            "Gael Faye",                "roman",           "terminé"),
    ("La Métamorphose",                       "Frantz Kafka",             "roman",           "terminé"),
    ("Les Carnets du sous sol",               "Fedor Dostoïevski",        "roman",           "en_cours"),
    ("L'art d'être heureux",                  "Arthur Schopenhauer",      "essai_philo",     "terminé"),
    ("L'art de se connaître soi-même",        "Arthur Schopenhauer",      "essai_philo",     "terminé"),
    ("Manifeste du parti communiste",         "Marx & Engels",            "essai_politique", "terminé"),
    ("Du mensonge à la violence",             "Hannah Arendt",            "essai_philo",     "en_cours"),
    ("L'antifascisme",                        "Mark Bray",                "essai_politique", "terminé"),
    ("Le crépuscule des idoles",              "Nietzsche",                "essai_philo",     "en_cours"),
    ("Le mythe de Sisyphe",                   "Albert Camus",             "essai_philo",     "terminé"),
    ("Du contrat social",                     "Rousseau",                 "essai_politique", "terminé"),
    ("L'existentialisme est un Humanisme",    "Jean Paul Sartre",         "essai_philo",     "terminé"),
    ("Privilège",                             "Alice de Rochechouart",    "essai_philo",     "terminé"),
    ("Saint Luigi",                           "Nicolas Framont",          "socio",           "terminé"),
    ("Discours de la Méthode",                "René Descartes",           "essai_philo",     "terminé"),
    ("Les Héritiers",                         "Pierre Bourdieu",          "socio",           "en_cours"),
    ("Le Capital",                            "Karl Marx",                "essai_politique", "en_cours"),
    ("L'hégémonie culturelle",                "Antonio Gramsci",          "essai_politique", "terminé"),
    ("La vie devant soi",                     "Romain Gary",              "roman",           "en_cours"),
    ("Peaux noires masques blancs",           "Frantz Fanon",             "essai_philo",     "en_cours"),
    ("Les damnés de la terre",                "Frantz Fanon",             "essai_philo",     "en_cours"),
    ("L'homme révolté",                       "Albert Camus",             "essai_philo",     "en_cours"),
    ("Il n'y a pas de petite querelle",       "Amadou Hampâté Bâ",        "roman",           "en_cours"),
    ("Cyberpunk",                             "Asma Mhalla",              "essai_politique", "en_cours"),
    ("Les Jours viennent et passent",         "Hemley Boum",              "roman",           "en_cours"),
    ("Comme un empire dans un empire",        "Alice Zeniter",            "roman",           "terminé"),
    ("De la vie heureuse",                    "Sénèque",                  "essai_philo",     "terminé"),
]


def run_seed():
    """
    Insère les livres en base si et seulement si la table est vide.
    Appelé au démarrage dans main.py.
    """
    db = SessionLocal()
    try:
        if db.query(Book).count() > 0:
            return  # Déjà peuplé, on ne touche à rien
        for title, author, book_type, status in BOOKS:
            db.add(Book(title=title, author=author, type=book_type, status=status))
        db.commit()
        print(f"[seed] {len(BOOKS)} livres insérés.")
    finally:
        db.close()
