from flask import Blueprint, render_template

bp_services = Blueprint("services", __name__)


@bp_services.route("/", methods=["GET"])
def page_services():
    return render_template("services/services.jinja")