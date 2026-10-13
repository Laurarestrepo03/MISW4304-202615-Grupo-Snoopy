from marshmallow import fields, validate

from extensions import ma


class BlacklistCreateSchema(ma.Schema):
    email = fields.Email(required=True)
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(max=255)
    )
