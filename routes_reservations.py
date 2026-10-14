from flask import Blueprint, render_template, request, jsonify
import bd
from datetime import date

bp_reservations = Blueprint("reservations", __name__)

@bp_reservations.route("/reserver")
def reserver():
    arrivee = request.args.get("arrivee", "")
    depart = request.args.get("depart", "")
    clients = request.args.get("clients", 1,type=int)
    return render_template("reservations/navigation.jinja", arrivee=arrivee, depart=depart, clients=clients)

from flask import request, render_template, redirect, url_for, flash

@bp_reservations.route("/chambres", methods=["POST"])
def liste():
    arrivee = request.form.get("arrivee", "")
    depart = request.form.get("depart", "")
    clients = request.form.get("clients", 1,type=int)

    def retour(message):
        flash(message, "erreur")
        return redirect(url_for("reservations.reserver", arrivee=arrivee, depart=depart, clients=clients))

    if not arrivee or not depart:
        return retour("Choisissez vos dates d'arrivée et de départ.")

    date_jour = date.fromisoformat(arrivee)
    if date_jour < date.today():
        return retour("La date d'arrivée ne peut pas être dans le passé.")

    if depart <= arrivee:
        return retour("La date de départ doit être après la date d'arrivée.")

    try:
        with bd.creer_connexion() as conn:
            chambres = bd.obtenir_liste_chambres(conn, arrivee, depart, clients)
    except Exception:
        return retour("Erreur serveur.")
    return render_template("reservations/chambres.jinja",chambres=chambres,arrivee=arrivee,depart=depart,clients=clients,
    )