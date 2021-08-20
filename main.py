from myapp import create_app, socketio
# from myapp import db
# from myapp.models import *



app = create_app()
# with app.app_context():
#     db.create_all()


if __name__=='__main__':
    socketio.run(app)
