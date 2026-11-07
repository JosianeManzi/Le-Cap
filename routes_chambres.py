from flask import Blueprint, render_template, request, jsonify, redirect, session, flash, abort, url_for
import bd
import os
from werkzeug.utils import secure_filename
import uuid

TYPES_CHAMBRE = ("Standard", "Suite", "Luxueux")
EXTENSIONS_IMAGE = {"jpg", "jpeg", "png", "webp", "gif"}

bp_chambres = Blueprint("chambres", __name__)



@bp_chambres.route("/ajouter", methods=["GET"])
def page_ajouter_chambre():
    return render_template("chambres/ajouter.jinja")


@bp_chambres.route("/ajouter_chambre", methods=["POST"])
def ajouter_chambre():
    type_chambre = request.form.get("type_chambre", "").strip()
    description = request.form.get("description", "").strip()
    prix_nuit = request.form.get("prix_nuit", "").strip()
    disponible = request.form.get("disponible", "1")

    if not all([type_chambre, description, prix_nuit]):
        return jsonify({"succes": False, "message": "Merci de remplir tous les champs obligatoires."}), 400

    if type_chambre not in TYPES_CHAMBRE:
        return jsonify({"succes": False, "message": "Type de chambre invalide."}), 400

    try:
        prix_nuit = float(prix_nuit)
    except ValueError:
        return jsonify({"succes": False, "message": "Le prix doit être un nombre."}), 400

    try:
        nb_personnes = int(request.form.get("nb_personnes", ""))
    except ValueError:
        return jsonify({"succes": False, "message": "Le nombre de personnes doit être un entier."}), 400
    if not 1 <= nb_personnes <= 4:
        return jsonify({"succes": False, "message": "Le nombre de personnes doit être entre 1 et 4."}), 400

    # Image obligatoire
    fichier_image = request.files.get("image")
    if not fichier_image or not fichier_image.filename:
        return jsonify({"succes": False, "message": "L'image est obligatoire."}), 400

    extension = fichier_image.filename.rsplit(".", 1)[-1].lower()
    if extension not in EXTENSIONS_IMAGE:
        return jsonify({"succes": False, "message": "Format d'image non accepté."}), 400

    # Préfixe unique pour que deux images du même nom ne s'écrasent pas
    nom_image = f"{uuid.uuid4().hex[:8]}_{secure_filename(fichier_image.filename)}"
    chemin_dossier = os.path.join("static", "img")
    os.makedirs(chemin_dossier, exist_ok=True)
    fichier_image.save(os.path.join(chemin_dossier, nom_image))

    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_chambre(conn, type_chambre, description, prix_nuit, nom_image, nb_personnes, disponible)
    except Exception as e:
        print("ERREUR AJOUTER_CHAMBRE:", e)
        return jsonify({"succes": False, "message": "Erreur serveur."}), 500

    return jsonify({"succes": True, "message": "Chambre ajoutée avec succès."}), 201


@bp_chambres.route("/liste", methods=["GET"])
def page_liste_chambres():
    with bd.creer_connexion() as conn:
        chambres = bd.obtenir_chambres(conn)
    chambres = [c for c in chambres if c["disponible"]]
    return render_template("chambres/liste.jinja", chambres=chambres)

def admin_requis():
    if not session.get("est_admin"):
        abort(403)


@bp_chambres.route("/admin", methods=["GET"])
def page_admin_chambres():
    admin_requis()
    with bd.creer_connexion() as conn:
        chambres = bd.obtenir_chambres(conn)
        for chambre in chambres:
            chambre["reservee"] = bd.chambre_est_reservee(conn, chambre["id"])
    return render_template("chambres/admin_liste.jinja", chambres=chambres)


@bp_chambres.route("/modifier/<int:id_chambre>", methods=["GET"])
def page_modifier_chambre(id_chambre):
    admin_requis()
    with bd.creer_connexion() as conn:
        chambre = bd.obtenir_chambre(conn, id_chambre)
        reservee = bd.chambre_est_reservee(conn, id_chambre)
    if not chambre:
        abort(404)
    if reservee:
        flash("Cette chambre a déjà été réservée, elle ne peut plus être modifiée.", "danger")
        return redirect(url_for("chambres.page_admin_chambres"))
    return render_template("chambres/modifier.jinja", chambre=chambre, types=TYPES_CHAMBRE)


@bp_chambres.route("/modifier/<int:id_chambre>", methods=["POST"])
def modifier_chambre_admin(id_chambre):
    admin_requis()
    with bd.creer_connexion() as conn:
        if bd.chambre_est_reservee(conn, id_chambre):
            flash("Cette chambre a déjà été réservée, elle ne peut plus être modifiée.", "danger")
            return redirect(url_for("chambres.page_admin_chambres"))
    type_chambre = request.form.get("type_chambre", "")
    description = request.form.get("description", "").strip()
    prix_nuit = request.form.get("prix_nuit", type=float)
    nb_personnes = request.form.get("nb_personnes", type=int)
    disponible = 1 if request.form.get("disponible") else 0
    image = request.files.get("image")

    if (type_chambre not in TYPES_CHAMBRE or not description
            or prix_nuit is None or prix_nuit <= 0
            or nb_personnes is None or not 1 <= nb_personnes <= 4):
        flash("Merci de remplir correctement tous les champs.", "danger")
        return redirect(url_for("chambres.page_modifier_chambre", id_chambre=id_chambre))

    nom_image = None
    if image and image.filename:
        extension = image.filename.rsplit(".", 1)[-1].lower()
        if extension not in EXTENSIONS_IMAGE:
            flash("Format d'image non accepté.", "danger")
            return redirect(url_for("chambres.page_modifier_chambre", id_chambre=id_chambre))
        nom_image = f"{uuid.uuid4().hex[:8]}_{secure_filename(image.filename)}"
        image.save(os.path.join("static", "img", nom_image))

    with bd.creer_connexion() as conn:
        bd.modifier_chambre(conn, id_chambre, type_chambre, description, prix_nuit,
                            nb_personnes, disponible, nom_image)

    flash("La chambre a été modifiée.", "success")
    return redirect(url_for("chambres.page_admin_chambres"))



@bp_chambres.route("/basculer/<int:id_chambre>", methods=["POST"])
@bp_chambres.route("/basculer/<int:id_chambre>", methods=["POST"])
def basculer_chambre_admin(id_chambre):
    admin_requis()
    with bd.creer_connexion() as conn:
        chambre = bd.obtenir_chambre(conn, id_chambre)
        if not chambre:
            abort(404)
        if chambre["disponible"] and bd.chambre_est_reservee(conn, id_chambre):
            flash("Cette chambre a déjà été réservée, elle ne peut pas être retirée.", "danger")
            return redirect(url_for("chambres.page_admin_chambres"))
        bd.basculer_disponibilite_chambre(conn, id_chambre)
    return redirect(url_for("chambres.page_admin_chambres"))