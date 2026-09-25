from flask import Flask,render_template
from dotenv import load_dotenv
import os
from routes_compte import bp_compte


if not os.getenv("DB_USER"):
    load_dotenv(".env")

app = Flask(__name__)
app.secret_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
app.register_blueprint(bp_compte, url_prefix="/compte")
app.register_blueprint(bp_chambres, url_prefix="/chambres")

if __name__ == "__main__":
    app.run(debug=True)