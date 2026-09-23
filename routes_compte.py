 
from flask import Blueprint,render_template, request, jsonify
import bd
import re
import hashlib
bp_compte = Blueprint("compte", __name__,)


@bp_compte.route("/creer", methods=["GET"])
def page_creer_compte():
    return render_template("comptes/creer_compte.jinja")


@bp_compte.route("/connexion", methods=["GET"])
def page_connexion():
    return render_template("comptes/connexion.jinja")

