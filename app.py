from flask import Flask
from routes_compte import bp_compte

app = Flask(__name__)
app.register_blueprint(bp_compte, url_prefix="/compte")

if __name__ == "__main__":
    app.run(debug=True)