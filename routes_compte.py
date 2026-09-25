import os
from flask import Blueprint, render_template, request, jsonify, session
import bd
import hashlib

bp_compte = Blueprint("compte", __name__)


def hacher_mdp(mdp):
    """hacher mdp"""
    return hashlib.sha512(mdp.encode('utf-8')).hexdigest()


@bp_compte.route("/creer", methods=["GET"])
def page_creer_compte():
    return render_template("comptes/creer_compte.jinja")


@bp_compte.route("/creer_admin", methods=["GET"])
def page_creer_compte_admin():
    return render_template("comptes/creer_compte_admin.jinja")


@bp_compte.route("/connexion", methods=["GET"])
def page_connexion():
    return render_template("comptes/connexion.jinja")


@bp_compte.route("/verifier_courriel", methods=["POST"])
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
            bd.ajouter_utilisateur(conn, courriel, mot_de_passe_hache, nom, prenom, est_admin=0)
    except Exception:
        return jsonify({"succes": False, "message": "Erreur serveur."}), 500

    return jsonify({"succes": True, "message": "Compte créé avec succès."}), 201


@bp_compte.route("/creer_compte_admin", methods=["POST"])
def creer_compte_admin():
    courriel = request.form.get("courriel", "").strip()
    mot_de_passe = request.form.get("mot_de_passe", "").strip()
    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    code_secret = request.form.get("code_secret", "").strip()

    if code_secret != os.getenv("CODE_SECRET_ADMIN"):
        return jsonify({"succes": False, "message": "Code secret invalide."}), 403

    mot_de_passe_hache = hacher_mdp(mot_de_passe)

    try:
        with bd.creer_connexion() as conn:
            if bd.utilisateur_existe(conn, courriel):
                return jsonify({"succes": False, "message": "Un compte existe déjà avec ce courriel."}), 409
            bd.ajouter_utilisateur(conn, courriel, mot_de_passe_hache, nom, prenom, est_admin=1)
    except Exception:
        return jsonify({"succes": False, "message": "Erreur serveur."}), 500

    return jsonify({"succes": True, "message": "Compte administrateur créé avec succès."}), 201


@bp_compte.route("/connexion", methods=["POST"])
def connexion():
    courriel = request.form.get("courriel", "").strip()
    mot_de_passe = request.form.get("mot_de_passe", "").strip()
    mot_de_passe_hache = hacher_mdp(mot_de_passe)

    with bd.creer_connexion() as conn:
        utilisateur = bd.obtenir_utilisateur_par_email(conn, courriel)

    if not utilisateur or utilisateur["mot_de_passe"] != mot_de_passe_hache:
        return jsonify({"succes": False, "message": "Courriel ou mot de passe incorrect."}), 401

    session["utilisateur_id"] = utilisateur["id"]
    session["est_admin"] = bool(utilisateur["est_admin"])
    session["nom"] = utilisateur["nom"]

    return jsonify({"succes": True, "message": f"Bienvenue {utilisateur['prenom']} !"}), 200