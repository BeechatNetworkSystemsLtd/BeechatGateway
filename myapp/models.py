from myapp import db
from datetime import datetime
# from flask_login import UserMixin

class User(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=True)
    ip = db.Column(db.String(17), unique=False, nullable=False)
    port = db.Column(db.String(10), unique=False, nullable=False)
    profile_image = db.Column(db.String(200), unique=False, default='default.jpg')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    user_messages = db.relationship('Messages', backref='user_message', lazy=True)
    user_notification = db.relationship('Notifications', backref="user_notification", lazy=True)

    def __repr__(self):
        return "id: {}, username: {}, ip: {}".format(self.id, self.username, self.ip)


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    has_new_messages = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"id: {self.user_id}, has_notification: {self.has_new_messages}"

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "message: {}, user: {}".format(self.message, self.user_id)

# @login_manager.user_loader
# def user_loader(id):
#     return MyIdentity.query.get(id)

class MyIdentity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = username = db.Column(db.String(50), unique=False, nullable=True)
    profile_pic = db.Column(db.String(200), unique=False, default='default.jpg')
    unique_id = db.Column(db.String(100), unique=False, nullable=True)

    private_key = db.Column(db.String(2500), nullable=False, unique=False)
    public_key = db.Column(db.String(2500), nullable=False, unique=False)
    dil_private_key = db.Column(db.String(2500), nullable=False, unique=False)
    dil_public_key = db.Column(db.String(2500), nullable=False, unique=False)

    def __repr__(self):
        return f"{self.username}"

class CurrentIdentity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identity_no = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return f"{self.identity_no}"


class HostPort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port_no = db.Column(db.Integer, unique=False, nullable=False)
    host = db.Column(db.String(20), nullable=True, unique=True)

class ReceivedPublic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(1200), nullable=False)
