from flask import Blueprint, render_template, request, jsonify
import bd
import os
from werkzeug.utils import secure_filename

bp_chambres = Blueprint("chambres", __name__)


@bp_chambres.route("/ajouter", methods=["GET"])
def page_ajouter_chambre():
    return render_template("chambres/ajouter.jinja")


@bp_chambres.route("/ajouter_chambre", methods=["POST"])
@bp_chambres.route("/ajouter_chambre", methods=["POST"])
def ajouter_chambre():
    type_chambre = request.form.get("type_chambre", "").strip()
    description = request.form.get("description", "").strip()
    prix_nuit = request.form.get("prix_nuit", "").strip()
    disponible = request.form.get("disponible", "1")

    if not all([type_chambre, description, prix_nuit]):
        return jsonify({"succes": False, "message": "Merci de remplir tous les champs obligatoires."}), 400

    try:
        prix_nuit = float(prix_nuit)
    except ValueError:
        return jsonify({"succes": False, "message": "Le prix doit être un nombre."}), 400

    nom_image = None
    fichier_image = request.files.get("image")
    if fichier_image and fichier_image.filename:
        nom_image = secure_filename(fichier_image.filename)
        chemin_dossier = os.path.join("static", "img")
        os.makedirs(chemin_dossier, exist_ok=True)
        fichier_image.save(os.path.join(chemin_dossier, nom_image))

    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_chambre(conn, type_chambre, description, prix_nuit, nom_image, disponible)
    except Exception as e:
        print("ERREUR AJOUTER_CHAMBRE:", e)
        return jsonify({"succes": False, "message": "Erreur serveur."}), 500

    return jsonify({"succes": True, "message": "Chambre ajoutée avec succès."}), 201

@bp_chambres.route("/liste", methods=["GET"])
def page_liste_chambres():
    with bd.creer_connexion() as conn:
        chambres = bd.obtenir_chambres(conn)
    return render_template("chambres/liste.jinja", chambres=chambres)