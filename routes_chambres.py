from flask import Blueprint, render_template, request, jsonify
import bd

bp_chambres = Blueprint("chambres", __name__)


@bp_chambres.route("/ajouter", methods=["GET"])
def page_ajouter_chambre():
    return render_template("chambres/ajouter.jinja")


@bp_chambres.route("/ajouter_chambre", methods=["POST"])
def ajouter_chambre():
    type_chambre = request.form.get("type_chambre", "").strip()
    description = request.form.get("description", "").strip()
    prix_nuit = request.form.get("prix_nuit", "").strip()
    image = request.form.get("image", "").strip()
    disponible = request.form.get("disponible", "1")

    if not all([type_chambre, description, prix_nuit]):
        return jsonify({"succes": False, "message": "Merci de remplir tous les champs obligatoires."}), 400

    try:
        prix_nuit = float(prix_nuit)
    except ValueError:
        return jsonify({"succes": False, "message": "Le prix doit être un nombre."}), 400

    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_chambre(conn, type_chambre, description, prix_nuit, image, disponible)
    except Exception:
        return jsonify({"succes": False, "message": "Erreur serveur."}), 500

    return jsonify({"succes": True, "message": "Chambre ajoutée avec succès."}), 201


@bp_chambres.route("/liste", methods=["GET"])
def page_liste_chambres():
    with bd.creer_connexion() as conn:
        chambres = bd.obtenir_chambres(conn)
    return render_template("chambres/liste.jinja", chambres=chambres)