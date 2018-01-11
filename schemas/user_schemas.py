from marshmallow import fields, Schema


class NotificationSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    message = fields.String()
    datetime = fields.DateTime()


class UserNotificationsSchema(Schema):
    notifications = fields.List(fields.Nested(NotificationSchema()))


class RegistrationSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    last_name = fields.String()
    country = fields.String()
    city = fields.String()
    email = fields.String()
    birth_day = fields.Date()
    role = fields.String()


class UserSchema(Schema):
    id = fields.Integer()
    email = fields.String()
    role = fields.String()
