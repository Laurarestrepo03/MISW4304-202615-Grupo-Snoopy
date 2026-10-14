import os

from flask import Flask
from flask_jwt_extended import create_access_token
from flask_restful import Api, Resource
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import db, jwt, ma
from resources import BlacklistEmailResource, BlacklistResource, BlacklistResetResource


class Health(Resource):
    def get(self):
        return {"status": "ok"}, 200


app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

db.init_app(app)
ma.init_app(app)
jwt.init_app(app)

api = Api(app)
api.add_resource(Health, "/ping")
api.add_resource(BlacklistResource, "/blacklists")
api.add_resource(BlacklistEmailResource, "/blacklists/<string:email>")

if os.getenv("ENABLE_RESET", "false").lower() == "true":
    api.add_resource(BlacklistResetResource, "/blacklists/reset")

with app.app_context():
    db.create_all()


@app.cli.command("generate-token")
def generate_token():
    print(create_access_token(identity="blacklist-client"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
