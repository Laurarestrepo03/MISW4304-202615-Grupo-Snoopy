from flask import Flask
from flask_restful import Api, Resource

from config import Config
from extensions import db, jwt, ma


class Health(Resource):
    def get(self):
        return {"status": "ok"}, 200

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
ma.init_app(app)
jwt.init_app(app)

api = Api(app)
api.add_resource(Health, "/ping")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)