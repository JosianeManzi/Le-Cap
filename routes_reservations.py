from flask import Blueprint, render_template, request, jsonify
import bd
import os
from werkzeug.utils import secure_filename

bp_reservations = Blueprint("reservations", __name__)

@bp_reservations.route("/reserver", methods=["GET"])
def reservations():
    return render_template("reservations/navigation.jinja")