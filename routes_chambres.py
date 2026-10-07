from flask import Blueprint, render_template, request, jsonify
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
    return render_template("chambres/liste.jinja", chambres=chambres)