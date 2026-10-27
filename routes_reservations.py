from flask import Blueprint, render_template, request, redirect, url_for,flash, session
import bd
from datetime import date

bp_reservations = Blueprint("reservations", __name__)

@bp_reservations.route("/reserver")
def reserver():
    arrivee = request.args.get("arrivee", "")
    depart = request.args.get("depart", "")
    clients = request.args.get("clients", 1,type=int)
    return render_template("reservations/navigation.jinja", arrivee=arrivee, depart=depart, clients=clients)


@bp_reservations.route("/chambres", methods=["GET", "POST"])
def liste():
    arrivee = request.values.get("arrivee", "")
    depart = request.values.get("depart", "")
    clients = request.values.get("clients", 1, type=int)
    type_chambre = request.values.get("type_chambre", "")

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
            chambres = bd.obtenir_liste_chambres(conn, arrivee, depart, clients, type_chambre)
    except Exception:
        return retour("Erreur serveur.")
    return render_template("reservations/chambres.jinja", chambres=chambres, arrivee=arrivee, depart=depart, clients=clients, type_chambre=type_chambre)

@bp_reservations.route("/reservations")
def reservations():
    id_chambre = request.args.get("id_chambre", type=int)
    arrivee = request.args.get("arrivee", "")
    depart = request.args.get("depart", "")
    clients = request.args.get("clients", 1, type=int)
    type_chambre = request.args.get("type_chambre", "")

    if "id_utilisateur" not in session:
        session["apres_connexion"] = url_for(
            "reservations.liste", arrivee=arrivee, depart=depart,
            clients=clients, type_chambre=type_chambre)
        flash("Connectez-vous pour réserver.", "erreur")
        return redirect(url_for("compte.page_connexion"))
    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_reservation(conn, session["id_utilisateur"], id_chambre, arrivee, depart)
    except Exception:
        return redirect(url_for("reservations.reserver", arrivee=arrivee, depart=depart, clients=clients))

    return redirect(url_for("compte.page_utilisateur"))

@bp_reservations.route("/reservations/<int:id_reservation>/annuler", methods=["POST"])
def annuler(id_reservation):
    id_utilisateur = session.get("id_utilisateur")
    with bd.creer_connexion() as conn:
        annulee = bd.annuler_reservation(conn, id_reservation, id_utilisateur)

    if annulee:
        flash("Réservation annulée.", "success")
    else:
        flash("Impossible d'annuler cette réservation.", "error")

    return redirect(url_for("compte.page_utilisateur"))