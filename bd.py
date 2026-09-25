import types
import contextlib
import mysql.connector
import os


@contextlib.contextmanager
def creer_connexion():
    """Créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user=os.getenv("BD_UTILISATEUR"),
        password=os.getenv("BD_MDP"),
        host=os.getenv("BD_SERVEUR"),
        database=os.getenv("BD_NOM_SCHEMA"),
        raise_on_warnings=True
    )

    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()


def utilisateur_existe(conn, courriel):
    """Retourne True si un utilisateur avec ce courriel existe déjà"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id FROM utilisateurs WHERE email = %s",
            (courriel,)
        )
        resultat = curseur.fetchone()
        return resultat is not None


def obtenir_utilisateur_par_email(conn, courriel):
    """Retourne l'utilisateur correspondant à ce courriel (dict), ou None"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateurs WHERE email = %s",
            (courriel,)
        )
        return curseur.fetchone()


def ajouter_utilisateur(conn, courriel, mot_de_passe, nom, prenom, est_admin=0):
    """Ajoute un nouvel utilisateur (client par défaut, admin si est_admin=1)"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO utilisateurs (email, mot_de_passe, nom, prenom, est_admin)
            VALUES (%s, %s, %s, %s, %s)
        """, (courriel, mot_de_passe, nom, prenom, est_admin))