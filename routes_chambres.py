from flask import Blueprint, render_template, request, jsonify,redirect,current_app,session,flash,abort,url_for
import bd
import os
from werkzeug.utils import secure_filename
import uuid
from mysql.connector.errors import IntegrityError

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
    return render_template("chambres/liste.jinja", chambres=chambres)


def admin_requis():
    """Refuse l'accès (403) si l'utilisateur n'est pas administrateur"""
    if not session.get("est_admin"):
        abort(403)


def enregistrer_image(fichier):
    """Enregistre l'image dans static/img. Retourne (nom_du_fichier, message_d_erreur)."""
    nom_original = fichier.filename
    extension = nom_original.rsplit(".", 1)[-1].lower() if "." in nom_original else ""
    if extension not in EXTENSIONS_IMAGE:
        return None, "L'image doit être au format jpg, jpeg, png, webp ou gif."

    nom_fichier = f"{uuid.uuid4().hex[:8]}_{secure_filename(nom_original)[-80:]}"
    fichier.save(os.path.join(current_app.root_path, "static", "img", nom_fichier))
    return nom_fichier, None


@bp_chambres.route("/modifier/<int:id_chambre>", methods=["GET"])
def page_modifier_chambre(id_chambre):
    admin_requis()
    with bd.creer_connexion() as conn:
        chambre = bd.obtenir_chambre(conn, id_chambre)

    if not chambre:
        abort(404)

    return render_template("chambres/modifier.jinja", chambre=chambre, types=TYPES_CHAMBRE)


@bp_chambres.route("/modifier/<int:id_chambre>", methods=["POST"])
def modifier_chambre_admin(id_chambre):
    admin_requis()
    type_chambre = request.form.get("type_chambre", "")
    description = request.form.get("description", "").strip()
    nb_personnes = request.form.get("nb_personnes", type=int)
    disponible = 1 if request.form.get("disponible") else 0
    image = request.files.get("image")

    try:
        prix_nuit = round(float(request.form.get("prix_nuit", "").replace(",", ".")), 2)
    except ValueError:
        prix_nuit = 0

    erreur = None
    if type_chambre not in TYPES_CHAMBRE:
        erreur = "Type de chambre invalide."
    elif not description:
        erreur = "La description est obligatoire."
    elif not 0 < prix_nuit <= 100000:
        erreur = "Le prix doit être supérieur à 0 $."
    elif nb_personnes is None or not 1 <= nb_personnes <= 4:
        erreur = "Le nombre de personnes doit être entre 1 et 4."

    nom_image = None
    if not erreur and image and image.filename:
        nom_image, erreur = enregistrer_image(image)

    if erreur:
        flash(erreur, "danger")
        return redirect(url_for("chambres.page_modifier_chambre", id_chambre=id_chambre))

    with bd.creer_connexion() as conn:
        if not bd.obtenir_chambre(conn, id_chambre):
            abort(404)
        bd.modifier_chambre(conn, id_chambre, type_chambre, description, prix_nuit,
                            nb_personnes, disponible, nom_image)

    flash("La chambre a été modifiée.", "success")
    return redirect(url_for("chambres.page_liste_chambres"))


@bp_chambres.route("/supprimer/<int:id_chambre>", methods=["POST"])
def supprimer_chambre_admin(id_chambre):
    admin_requis()
    try:
        with bd.creer_connexion() as conn:
            bd.supprimer_chambre(conn, id_chambre)
        flash("La chambre a été supprimée.", "success")
    except IntegrityError:
        flash("Impossible de supprimer cette chambre : elle a des réservations. "
              "Modifiez-la et décochez « Disponible » pour la retirer.", "danger")

    return redirect(url_for("chambres.page_liste_chambres"))