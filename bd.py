import types
import contextlib
import mysql.connector
import os


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