from flask import Flask
from .config import Config
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session




socketio = SocketIO()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(app)
    db.init_app(app)

    app.config['SESSION_SQLALCHEMY'] = db
    sess = Session()
    sess.init_app(app)


    from myapp.main.routes import main
    from myapp.conversation.routes import conversation

    app.register_blueprint(main)
    app.register_blueprint(conversation)

    return app

