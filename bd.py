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
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO utilisateurs (email, mot_de_passe, nom, prenom, est_admin)
            VALUES (%s, %s, %s, %s, 0)
        """, (courriel, mot_de_passe, nom, prenom))

def ajouter_chambre(conn, type_chambre, description, prix_nuit, image, nb_personnes, disponible=1):
    """Ajoute une nouvelle chambre dans la BD"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO chambres (type_chambre, description, prix_nuit, image, nb_personnes, disponible)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (type_chambre, description, prix_nuit, image, nb_personnes, disponible))

def obtenir_chambres(conn):
    """Retourne la liste de toutes les chambres"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM chambres")
        return curseur.fetchall()
def chercher_utilisateur(conn, courriel, mot_de_passe_hache):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateurs WHERE email = %s AND mot_de_passe = %s",
            (courriel, mot_de_passe_hache)
        )
        utilisateur = curseur.fetchone()
        return utilisateur
def obtenir_utilisateur(conn, id_utilisateur):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateurs WHERE id = %s",
            (id_utilisateur,)
        )
        return curseur.fetchone()

def obtenir_plats(conn):
    """Retourne tous les plats disponibles, classés par catégorie puis par nom"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM plats WHERE disponible = 1 ORDER BY categorie, nom")
        return curseur.fetchall()


def obtenir_plats_par_ids(conn, ids):
    """Retourne les plats dont l'id est dans la liste"""
    if not ids:
        return []
    marqueurs = ", ".join(["%s"] * len(ids))
    with conn.get_curseur() as curseur:
        curseur.execute(
            f"SELECT * FROM plats WHERE disponible = 1 AND id IN ({marqueurs}) ORDER BY categorie, nom",
            tuple(ids)
        )
        return curseur.fetchall()

def creer_commande(conn, id_utilisateur, lignes):
    """lignes : liste de (id_plat, quantite, prix_unitaire). Retourne l'id de la commande."""
    total = sum(quantite * prix for _, quantite, prix in lignes)
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO commandes (id_utilisateur, total) VALUES (%s, %s)",
            (id_utilisateur, total)
        )
        id_commande = curseur.lastrowid
        for id_plat, quantite, prix in lignes:
            curseur.execute(
                """INSERT INTO commande_plats (id_commande, id_plat, quantite, prix_unitaire)
                   VALUES (%s, %s, %s, %s)""",
                (id_commande, id_plat, quantite, prix)
            )
    return id_commande


def obtenir_commande(conn, id_commande, id_utilisateur):
    """Retourne la commande avec ses lignes, seulement si elle appartient à cet utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM commandes WHERE id = %s AND id_utilisateur = %s",
            (id_commande, id_utilisateur)
        )
        commande = curseur.fetchone()
        if not commande:
            return None
        curseur.execute(
            """SELECT cp.quantite, cp.prix_unitaire, p.nom
               FROM commande_plats cp
               JOIN plats p ON p.id = cp.id_plat
               WHERE cp.id_commande = %s""",
            (id_commande,)
        )
        commande["lignes"] = curseur.fetchall()
        return commande


def payer_commande(conn, id_commande, id_utilisateur):
    """Passe la commande à 'payee'. Retourne le nombre de lignes modifiées (0 ou 1)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """UPDATE commandes SET statut = 'payee'
               WHERE id = %s AND id_utilisateur = %s AND statut = 'en_attente'""",
            (id_commande, id_utilisateur)
        )
        return curseur.rowcount
def obtenir_liste_chambres(conn, arrivee, depart, clients, type_chambre=""):
    with conn.get_curseur() as curseur:
        curseur.execute("""SELECT c.* FROM chambres c WHERE c.disponible = 1 AND c.nb_personnes >= %s
              AND NOT EXISTS ( SELECT 1 FROM reservations r WHERE r.chambre_id = c.id
              AND r.date_arrivee < %s AND r.date_depart > %s )
              AND (%s = '' OR c.type_chambre = %s) ORDER BY c.prix_nuit """,
            (clients, depart, arrivee, type_chambre, type_chambre),
        )
        return curseur.fetchall()

def ajouter_reservation(conn, id_utilisateur, id_chambre, arrivee, depart):
    with conn.get_curseur() as curseur:
        curseur.execute(""" INSERT INTO reservations (utilisateur_id, chambre_id, date_arrivee, date_depart)
            VALUES (%s, %s, %s, %s) """
            , (id_utilisateur, id_chambre, arrivee, depart))

def obtenir_reservations_utilisateur(conn, id_utilisateur):
    with conn.get_curseur() as curseur:
        curseur.execute(""" SELECT r.id AS id, c.type_chambre, c.prix_nuit, r.date_arrivee, r.date_depart
               FROM reservations r JOIN chambres c ON c.id = r.chambre_id
               WHERE r.utilisateur_id = %s """, (id_utilisateur,))
        return curseur.fetchall()

def annuler_reservation(conn, id_reservation, id_utilisateur):
    with conn.get_curseur() as curseur:
        curseur.execute(
            """DELETE FROM reservations
               WHERE id = %s AND utilisateur_id = %s""",
            (id_reservation, id_utilisateur),
        )
        return curseur.rowcount > 0

def supprimer_reservations_passees(conn):
    with conn.get_curseur() as curseur:
        curseur.execute(
            """DELETE FROM reservations
               WHERE date_depart < CURDATE()"""
        )
        return curseur.rowcount