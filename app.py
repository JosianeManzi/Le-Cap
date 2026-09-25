from flask import Flask
from routes_compte import bp_compte
from routes_chambres import bp_chambres
import os, dotenv
if not os.getenv('BD_UTILISATEUR'):
    dotenv.load_dotenv('.env')



app = Flask(__name__)
app.register_blueprint(bp_compte, url_prefix="/compte")
app.register_blueprint(bp_chambres, url_prefix="/chambres")

if __name__ == "__main__":
    app.run(debug=True)