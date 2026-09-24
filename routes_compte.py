 
from flask import Blueprint,render_template, request, jsonify
import bd
import hashlib
bp_compte = Blueprint("compte", __name__,)


@bp_compte.route("/creer", methods=["GET"])
def page_creer_compte():
    return render_template("comptes/creer_compte.jinja")

@bp_compte.route("/connexion", methods=["GET"])
def page_connexion():
    return render_template("comptes/connexion.jinja")

def hacher_mdp(mdp):
    """hacher mdp"""
    return hashlib.sha512(mdp.encode('utf-8')).hexdigest()

@bp_compte.route("/api/verifier_courriel", methods=["POST"])
def verifier_courriel():
    courriel = request.form.get("courriel", "").strip()
    with bd.creer_connexion() as conn:
        existe = bd.utilisateur_existe(conn, courriel)
    return jsonify({"existe": existe})

@bp_compte.route("/creer_compte", methods=["POST"])
def creer_compte():

    courriel = request.form.get("courriel", "").strip()
    mot_de_passe = request.form.get("mot_de_passe", "").strip()
    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    mot_de_passe_hache = hacher_mdp(mot_de_passe)
    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_utilisateur(conn,courriel,mot_de_passe_hache,nom,prenom)

    except Exception as e:
        return jsonify({"succes": False,"message": "Erreur serveur."}), 500

    return jsonify({"succes": True,"message": "Compte créé avec succès."}), 201

