from flask import Blueprint, render_template, session, redirect, url_for, request
import bd

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