from flask_classy import FlaskView, route
from flask import jsonify, request
from schemas import UserSchema, NotificationSchema, UserNotificationsSchema, RegistrationSchema
from models import User
from werkzeug.exceptions import Unauthorized, BadRequest, InternalServerError, Conflict
from database import db, push_service
from models import Notification


def validate_auth():
    auth = request.authorization
    if not auth:
        raise BadRequest("Authorization data was not provided")
    email = auth.email
    user = User.query.filter_by(email=email).first()
    if user is None or user.password != auth.password:
        raise Unauthorized("Incorrect username or password. Please try again.")
    return user


class UsersView(FlaskView):
    user_schema = UserSchema()
    notification_schema = NotificationSchema()
    user_notifications_schema = UserNotificationsSchema()
    user_registration_schema = RegistrationSchema()

    def index(self):
        users = User.query.all()
        users_data = self.user_schema.dump(users, many=True).data
        return jsonify({'users': users_data}), 200

    def get(self, id_user):
        user = User.query.filter(User.id == int(id_user)).first()
        user_data = self.user_schema.dump(user).data
        return jsonify({'user': user_data})

    @route('/notification', methods=['POST'])
    def notification(self):
        user_tokens = []
        notifications_to_users = []
        notification_data = request.json
        message_title = notification_data.get('message_title')
        message_body = notification_data.get('message_body')
        users_notifications = notification_data.get('users', None)
        notification = Notification(message_title, message_body)

        if users_notifications is None:
            user_tokens_result = User.query.filter(User.fcm_token is not None).with_entities(User.fcm_token).all()
            user_tokens = [token[0] for token in user_tokens_result]
            users_data = User.query.all()
            for user in users_data:
                notifications_to_users.append(user)
        else:
            for user in users_notifications:
                check_user = User.query.filter(User.email == user).first()
                notifications_to_users.append(check_user)
                get_token = check_user.fcm_token
                if get_token is not None:
                    user_tokens.append(get_token)

        notification.users = notifications_to_users

        try:
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise InternalServerError("Internal Server Error")

        try:
            push_service.notify_multiple_devices(registration_ids=user_tokens, message_title=message_title,
                                                 message_body=message_body)
        except Exception as e:
            raise BadRequest("Bad Request")

        return "", 204

    def user_notifications(self):
        user = validate_auth()
        user_id = user.id
        notifications_user = User.query.filter(User.id == user_id).first()
        notification_data = self.user_notifications_schema.dump(notifications_user).data
        return jsonify(notification_data)

    def login(self):
        user = validate_auth()
        token = request.headers.get('fcm_token', None)
        if token:
            user.fcm_token = token
            try:
                db.session.merge(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise InternalServerError("Internal Server Error")
        user_data = self.user_schema.dump(user).data
        return jsonify({'user': user_data})

    @route('/logout', methods=['POST'])
    def logout(self):
        user = validate_auth()
        user.fcm_token = None
        try:
            db.session.merge(user)
            db.session.commit()
        except Exception as e:
            raise InternalServerError("User can't be properly logged out")
        return "", 204

    def post(self):
        user_data = request.json
        password = user_data.get('password', None)
        email = user_data.get('email', None)
        name = user_data.get('name', None)
        last_name = user_data.get('last_name', None)
        birth_day = user_data.get('birth_day', None)
        country = user_data.get('country', None)
        city = user_data.get('city', None)
        role = user_data.get('role', None)
        if user_data is not None and email is not None and password is not None:
            existing_user = User.query.filter(User.username == email).first()
            if existing_user is None:
                user = User(password=password, email=email, name=name, last_name=last_name, birth_day=birth_day,
                            country=country, city=city, role=role)
                try:
                    db.session.add(user)
                    db.session.commit()
                    check_user = User.query.filter(User.email == email).first()
                    user_data = self.user_registration_schema.dump(check_user).data
                except Exception as e:
                    db.session.rollback()
                    raise InternalServerError("User cannot be added to the database")
            else:
                raise Conflict("User already exists")
        else:
            raise BadRequest("The user or password were not sent correctly")
        return jsonify({'user': user_data})
