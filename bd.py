<<<<<<< HEAD
"""
Accès à la base de données
"""

=======
import types
>>>>>>> aec3e9399fad3d3ff947600f9f52db4c961595fe
import contextlib
import mysql.connector
import os


<<<<<<< HEAD
# connexion a la base de donnée
@contextlib.contextmanager
def _creer_connexion():
    """Créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user=os.getenv("BD_UTILISATEUR"),
        password=os.getenv("BD_MDP"),
        host=os.getenv("BD_SERVEUR"),
        database=os.getenv("BD_NOM_SCHEMA"),
        raise_on_warnings=True
    )

=======
@contextlib.contextmanager
def creer_connexion():
    conn = mysql.connector.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        raise_on_warnings=True
    )

    conn.get_curseur = types.MethodType(get_curseur, conn)

>>>>>>> aec3e9399fad3d3ff947600f9f52db4c961595fe
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


<<<<<<< HEAD
@contextlib.contextmanager
=======
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
>>>>>>> aec3e9399fad3d3ff947600f9f52db4c961595fe
