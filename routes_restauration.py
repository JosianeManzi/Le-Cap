from flask import Blueprint, render_template, session, redirect, url_for, request, abort,flash
import bd
from datetime import date

bp_restauration = Blueprint("restauration", __name__)

CATEGORIES = [
    ("petit-dejeuner", "Petit-déjeuner", "🥐"),
    ("dejeuner", "Déjeuner", "🥗"),
    ("diner", "Dîner", "🍽️"),
]

QUANTITE_MAX = 20


def nombre_articles():
    return sum(session.get("panier", {}).values())


@bp_restauration.route("/", methods=["GET"])
def page_menu():
    with bd.creer_connexion() as conn:
        plats = bd.obtenir_plats(conn)

    plats_par_categorie = {cle: [] for cle, _, _ in CATEGORIES}
    for plat in plats:
        plats_par_categorie[plat["categorie"]].append(plat)

    return render_template(
        "restauration/menu.jinja",
        categories=CATEGORIES,
        plats_par_categorie=plats_par_categorie,
        nb_articles=nombre_articles()
    )


@bp_restauration.route("/panier", methods=["GET"])
def page_panier():
    panier = session.get("panier", {})
    lignes = []
    total = 0

    if panier:
        with bd.creer_connexion() as conn:
            plats = bd.obtenir_plats_par_ids(conn, [int(i) for i in panier])
        for plat in plats:
            quantite = panier[str(plat["id"])]
            sous_total = plat["prix"] * quantite
            total += sous_total
            lignes.append({"plat": plat, "quantite": quantite, "sous_total": sous_total})

    return render_template("restauration/panier.jinja", lignes=lignes, total=total)


@bp_restauration.route("/panier/ajouter/<int:id_plat>", methods=["POST"])
def ajouter_au_panier(id_plat):
    panier = session.get("panier", {})
    cle = str(id_plat)
    panier[cle] = min(panier.get(cle, 0) + 1, QUANTITE_MAX)
    session["panier"] = panier
    return redirect(url_for("restauration.page_menu"))


@bp_restauration.route("/panier/modifier/<int:id_plat>", methods=["POST"])
def modifier_panier(id_plat):
    panier = session.get("panier", {})
    cle = str(id_plat)

    if cle in panier:
        action = request.form.get("action")
        if action == "plus":
            panier[cle] = min(panier[cle] + 1, QUANTITE_MAX)
        elif action == "moins":
            panier[cle] -= 1
        elif action == "retirer":
            panier[cle] = 0

        if panier[cle] <= 0:
            del panier[cle]

    session["panier"] = panier
    return redirect(url_for("restauration.page_panier"))



@bp_restauration.route("/commander", methods=["POST"])
def commander():
    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        return redirect(url_for("compte.page_connexion"))

    panier = session.get("panier", {})
    if not panier:
        return redirect(url_for("restauration.page_panier"))

    with bd.creer_connexion() as conn:
        plats = bd.obtenir_plats_par_ids(conn, [int(i) for i in panier])
        lignes = [(p["id"], panier[str(p["id"])], p["prix"]) for p in plats]

        if not lignes:
            session.pop("panier", None)
            return redirect(url_for("restauration.page_panier"))

        id_commande = bd.creer_commande(conn, id_utilisateur, lignes)

    session.pop("panier", None)
    return redirect(url_for("restauration.page_confirmation", id_commande=id_commande))


@bp_restauration.route("/commande/<int:id_commande>", methods=["GET"])
def page_confirmation(id_commande):
    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        return redirect(url_for("compte.page_connexion"))

    with bd.creer_connexion() as conn:
        commande = bd.obtenir_commande(conn, id_commande, id_utilisateur)

    if not commande:
        abort(404)

    return render_template("restauration/confirmation.jinja", commande=commande)


def valider_carte(nom, numero, expiration, cvv):
    """Retourne un message d'erreur, ou None si tout est correct."""
    if not nom:
        return "Le nom sur la carte est obligatoire."
    if not (numero.isdigit() and len(numero) == 16):
        return "Le numéro de carte doit contenir 16 chiffres."
    try:
        mois, annee = expiration.split("/")
        mois, annee = int(mois), 2000 + int(annee)
    except ValueError:
        return "L'expiration doit être au format MM/AA."
    if not 1 <= mois <= 12:
        return "Le mois d'expiration est invalide."
    aujourdhui = date.today()
    if (annee, mois) < (aujourdhui.year, aujourdhui.month):
        return "Cette carte est expirée."
    if not (cvv.isdigit() and len(cvv) == 3):
        return "Le code CVV doit contenir 3 chiffres."
    return None


@bp_restauration.route("/commande/<int:id_commande>/paiement", methods=["GET"])
def page_paiement(id_commande):
    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        return redirect(url_for("compte.page_connexion"))

    with bd.creer_connexion() as conn:
        commande = bd.obtenir_commande(conn, id_commande, id_utilisateur)

    if not commande:
        abort(404)
    if commande["statut"] == "payee":
        return redirect(url_for("restauration.page_confirmation", id_commande=id_commande))

    return render_template("restauration/paiement.jinja", commande=commande, erreur=None, nom_carte="")


@bp_restauration.route("/commande/<int:id_commande>/payer", methods=["POST"])
def payer(id_commande):
    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        return redirect(url_for("compte.page_connexion"))

    with bd.creer_connexion() as conn:
        commande = bd.obtenir_commande(conn, id_commande, id_utilisateur)

    if not commande:
        abort(404)
    if commande["statut"] == "payee":
        return redirect(url_for("restauration.page_confirmation", id_commande=id_commande))

    nom_carte = request.form.get("nom_carte", "").strip()
    numero = request.form.get("numero_carte", "").replace(" ", "")
    expiration = request.form.get("expiration", "").strip()
    cvv = request.form.get("cvv", "").strip()

    erreur = valider_carte(nom_carte, numero, expiration, cvv)
    if erreur:
        return render_template("restauration/paiement.jinja",
                               commande=commande, erreur=erreur, nom_carte=nom_carte)

    with bd.creer_connexion() as conn:
        bd.payer_commande(conn, id_commande, id_utilisateur)

    return redirect(url_for("restauration.page_confirmation", id_commande=id_commande))



def admin_requis():
    """Refuse l'accès (403) si l'utilisateur n'est pas administrateur"""
    if not session.get("est_admin"):
        abort(403)


@bp_restauration.route("/admin", methods=["GET"])
def page_admin_menu():
    admin_requis()
    with bd.creer_connexion() as conn:
        plats = bd.obtenir_tous_les_plats(conn)

    plats_par_categorie = {cle: [] for cle, _, _ in CATEGORIES}
    for plat in plats:
        plats_par_categorie[plat["categorie"]].append(plat)

    return render_template("restauration/admin_menu.jinja",
                           categories=CATEGORIES,
                           plats_par_categorie=plats_par_categorie)


@bp_restauration.route("/admin/ajouter", methods=["POST"])

def ajouter_plat_menu():
    admin_requis()
    nom = request.form.get("nom", "").strip()
    description = request.form.get("description", "").strip()
    categorie = request.form.get("categorie", "")

    try:
        prix = round(float(request.form.get("prix", "").replace(",", ".")), 2)
    except ValueError:
        prix = 0

    if not nom or not description:
        flash("Le nom et la description sont obligatoires.", "danger")
    elif len(nom) > 100:
        flash("Le nom ne peut pas dépasser 100 caractères.", "danger")
    elif categorie not in [cle for cle, _, _ in CATEGORIES]:
        flash("Catégorie invalide.", "danger")
    elif not 0 < prix <= 500:
        flash("Le prix doit être entre 0,01 $ et 500 $.", "danger")
    else:
        with bd.creer_connexion() as conn:
            bd.ajouter_plat(conn, nom, description, prix, categorie)
        flash(f"« {nom} » a été ajouté au menu.", "success")

    return redirect(url_for("restauration.page_admin_menu"))


@bp_restauration.route("/admin/basculer/<int:id_plat>", methods=["POST"])

def basculer_plat(id_plat):
    admin_requis()
    with bd.creer_connexion() as conn:
        bd.basculer_disponibilite_plat(conn, id_plat)
    return redirect(url_for("restauration.page_admin_menu"))