import types
import contextlib
import mysql.connector
import os


@contextlib.contextmanager
def creer_connexion():
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
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id FROM utilisateurs WHERE email = %s",
            (courriel,)
        )
        resultat = curseur.fetchone()

        if resultat:
            return True
        else:
            return False

def ajouter_utilisateur(conn, courriel, mot_de_passe, nom, prenom):
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO utilisateurs (email, mot_de_passe, nom, prenom, est_admin)
            VALUES (%s, %s, %s, %s, 0)
        """, (courriel, mot_de_passe, nom, prenom))

def ajouter_chambre(conn, type_chambre, description, prix_nuit, image, disponible=1):
    """Ajoute une nouvelle chambre dans la BD"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO chambres (type_chambre, description, prix_nuit, image, disponible)
            VALUES (%s, %s, %s, %s, %s)
        """, (type_chambre, description, prix_nuit, image, disponible))


def obtenir_chambres(conn):
    """Retourne la liste de toutes les chambres"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM chambres")
        return curseur.fetchall()