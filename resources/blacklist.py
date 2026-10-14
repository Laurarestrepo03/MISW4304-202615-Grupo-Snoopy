from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from models import Blacklist
from schemas import BlacklistCreateSchema

create_schema = BlacklistCreateSchema()


class BlacklistResource(Resource):
    @jwt_required()
    def post(self):
        payload = request.get_json(silent=True)
        if payload is None:
            return {"msg": "El cuerpo de la solicitud debe ser JSON"}, 400

        try:
            data = create_schema.load(payload)
        except ValidationError as err:
            return {"msg": "Datos inválidos", "errors": err.messages}, 400

        email = data["email"].lower()

        if Blacklist.query.filter_by(email=email).first():
            return {"msg": f"El email {email} ya está en la lista negra"}, 409

        entry = Blacklist(
            email=email,
            app_uuid=data["app_uuid"],
            blocked_reason=data["blocked_reason"],
            request_ip=request.remote_addr,
        )
        db.session.add(entry)
        db.session.commit()

        return {"msg": f"El email {email} fue agregado a la lista negra"}, 201


class BlacklistEmailResource(Resource):
    @jwt_required()
    def get(self, email):
        email = email.lower()
        entry = Blacklist.query.filter_by(email=email).first()

        if entry is None:
            return {"is_blacklisted": False, "blocked_reason": None}, 200

        return {"is_blacklisted": True, "blocked_reason": entry.blocked_reason}, 200


class BlacklistResetResource(Resource):
    # @jwt_required()
    def post(self):
        deleted = Blacklist.query.delete()
        db.session.commit()
        return {"msg": "Lista negra reiniciada", "deleted": deleted}, 200
