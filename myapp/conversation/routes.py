from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from myapp.models import User, Messages, Notifications
from myapp import db
import requests
import json

conversation = Blueprint('conversation', __name__)

@conversation.route('/connect', methods=['GET', 'POST'])
def connect():
    req = requests.get("https://checkip.amazonaws.com/", 'html.parser').text.strip('\n')
    print(req)

    
    if request.method == 'GET':
        username = request.args.get('username')
        host = request.args.get('host')
        port = request.args.get('port')
    elif request.method == 'POST':
        username = request.json['username']
        host = request.json['host']
        port = request.json['port']
    if req == str(host):
        host = ''
    user = User.query.filter(User.ip==host).filter(User.port==port).first()
    print(username)
    print(host)
    print(port)
    if user:
        print(f"user ip is: {user.ip}, port: {user.port}")
        if user.ip == host and user.port == port:
            return f"{user.id}"
            return redirect(url_for('main.chat', id=user.id))

    # if new chat

    # register it to database first
    newuser = User(username=username, ip=host, port=port)
    db.session.add(newuser)
    db.session.commit()

    # redirect to /chat with user.id
    get_newuser = User.query.filter_by(ip=host, port=port).first()
    if get_newuser:
        return f"{get_newuser.id}"

    return "Error"


@conversation.route('/get_messages/<string:userid>')
def get_messages(userid):
    messages = Messages.query.filter_by(user_id=userid).all()
    # print(messages[0].message)
    # print([i.message for i in messages])

    if messages:
        messages = [i.message for i in messages]
    else:
        messages = []
    user = User.query.get(userid)
    client_pic = user.profile_image
    host = user.ip
    port = user.port

    # reurning a list of messages into a dictionary
    return {'client_pic': client_pic, 'messages':  messages, 'host': host, 'port': port}
    


@conversation.route('/save_message', methods=['POST'])
def save_message():
    mess = request.json['message']
    user_id = request.json['user_id']
    if user_id==None:
        host = session['host']
        port = session['port']
        user = User.query.filter(User.ip == host).filter(User.port == port).first()
        user_id = user.id
    message = Messages(message=mess, user_id=user_id)
    db.session.add(message)
    try:
        db.session.commit()
    except:
        return "not added"
    return "added"

@conversation.route('/save_notification', methods=['POST'])
def save_notification():
    id = request.json['id']

    notification = Notifications(has_new_messages=True, user_id=id)
    db.session.add(notification)
    db.session.commit()

    return f"{id}"

@conversation.route('/remove_notification', methods=['POST'])
def remove_notification():
    id = request.json['id']
    print(id)
    allnotif = Notifications.query.all()
    for i in allnotif:
        print(i.user_id)
        print(i.user_id==None)
        if i.user_id == None:
            db.session.delete(i)
            # print(f"deleted: {i.ip}:{i.port}")
        db.session.commit()


    notification = Notifications.query.filter_by(user_id=id).first()
    print(f"notification: {notification}")
    if notification:
        db.session.delete(notification)
    db.session.commit()

    return "deleted"




@conversation.route('/delete_user/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        messages = Messages.query.filter_by(user_id=user.id).all()
        print(messages)
        [db.session.delete(i) for i in messages]
        db.session.delete(user)
        
        notification = Notifications.query.filter_by(user_id=id).first()
        if notification:
            db.session.delete(notification)
        db.session.commit()
        flash("User deleted successfully", "success")
    
    return "user deleted"
