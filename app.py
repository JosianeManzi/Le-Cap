from flask import Flask
from routes_compte import bp_compte
import os, dotenv
if not os.getenv('BD_UTILISATEUR'):
    dotenv.load_dotenv('.env')



app = Flask(__name__)
app.register_blueprint(bp_compte, url_prefix="/compte")

if __name__ == "__main__":
    app.run(debug=True)
