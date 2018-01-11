from marshmallow import fields, Schema


class MessageSchema(Schema):
    message = fields.String()
    send_time = fields.DateTime()
