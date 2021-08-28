#! /usr/bin/env python
from hashlib import blake2s
import os
import socket
import sys
import time
import threading
sys.path.append("./")
from myapp.main import kyber as Kyber
from myapp.main import dilithium as Dilithium
from base64 import b64encode, b64decode
import json
from Crypto.Cipher import ChaCha20
from hashlib import blake2b
import requests
from myapp.main import upnpcclient

receivedkyberpubkey = ""

from flask import (Blueprint, render_template, session, copy_current_request_context, 
                    request, redirect, url_for, flash)
from flask_socketio import emit
from myapp import socketio, db
from myapp.models import (User, Messages, MyIdentity, 
                            CurrentIdentity, Notifications, HostPort,
                            ReceivedPublic)
from werkzeug.utils import secure_filename
from flask import current_app


mylist = []

main = Blueprint('main', __name__)


@main.before_app_first_request
def start_server_first():
    current_identity = CurrentIdentity.query.first()
    if current_identity==None:
        print("current empty")
        myid = MyIdentity.query.first()
        if myid==None:
            print("myid empty")
            flash("There is no identity available. \
            Please make an identity first!", "danger")

    # try:
    #     if session['privatekey'] and session['publickey']:
    #         pass
    #         # flash("Client started.", "info")
    # except KeyError:
    #     create_keys()
        # flash("Client started.", "info")

    res = start_server()
    session['server started'] = True
    session.pop('current_client', None)
    print('Server started')


@main.route('/dropall')
def dropall():
    # db.session.rollback()
    db.drop_all()
    db.create_all()
    return redirect(url_for('main.home'))


@main.route('/amd')
def erase():
    return "Erased called"

@main.route('/')
def home():
    users = User.query.all()
    pr = HostPort.query.first()
    if pr==None:
        return "Restart the server from console!"
    else:
        host = pr.host
        port = pr.port_no

    current_identity = CurrentIdentity.query.first()

    if current_identity:
        myid = MyIdentity.query.get(current_identity.identity_no)
    else:
        myid = MyIdentity.query.first()
    allids = MyIdentity.query.all()

    notifications = Notifications.query.all()


    return render_template('new_layout.html', users=users, myhost=host, myport=port, 
                                    myid=myid, allids=allids, notifications=notifications)

@main.route('/change_profile', methods=['POST'])
def change_profile():
    id = request.json['id']

    # removing all id
    CurrentIdentity.query.delete()

    # adding new current id
    cid = CurrentIdentity(identity_no=id)
    db.session.add(cid)
    db.session.commit()

    return "done"



def create_keys():
    mykeys = Kyber.createkeys()
    privatekey = mykeys[0]
    publickey = mykeys[1]
    mydilkeys = Dilithium.createkeys()
    dilprivatekey = mydilkeys[0]
    dilpublickey = mydilkeys[1]



    myuser = {
        "Ki": privatekey,
        "Kp": publickey,
        "Di": dilprivatekey,
        "Dp": dilpublickey
    }

    return myuser

@main.route('/create_newid', methods=['POST'])
def create_newid():
    if request.method == "POST":
        profile_pic = request.files['profile_pic']
        username = request.form.get('username')
        keys = create_keys()
        private_key = keys["Ki"]
        public_key = keys["Kp"]
        dil_private_key = keys["Di"]
        dil_public_key = keys["Dp"]
        # unique_id = session['unique_id']

        filename = secure_filename(profile_pic.filename)
        if filename and filename is not None and filename != '':
            profile_pic.save(os.path.join('myapp/static/images', filename))
        else:
            filename = 'default.jpg'


        myid = MyIdentity(username=username, private_key=private_key, public_key=public_key,
                            dil_private_key=dil_private_key, dil_public_key=dil_public_key,
                            unique_id='none', profile_pic=filename)

        db.session.add(myid)
        db.session.commit()

        
        return redirect(url_for('main.home'))

    return "you have made a 'Get' request"



@main.route('/renewport')
def renewport():
    upnpcobject = upnpcclient.port_manager()
    upnpcobject.unmap_ports()
    port=upnpcobject.mapport()[1]
    print("Using port: "+ port)

    pr = HostPort.query.first()
    if pr==None:
        p = HostPort(port_no=port)
        db.session.add(p)
    # f = open('openport.txt', 'w')
    # f.write(str(port))
    # f.close()
    else:
        pr.port_no = port

    db.session.commit()
    return {'port': port}

# New conversation
@main.route('/server')
def start_server():
    pr = HostPort.query.first()
    if pr==None:
        port=renewport()['port']
    else:
        port = pr.port_no

    @copy_current_request_context
    def startServer():
        req = requests.get("https://checkip.amazonaws.com/", 'html.parser').text
        print("Your external IP is: "+ req)

        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Server started successfully\n")
        hostname=''

        try:
            sock.bind((hostname, port ))
        except:
            renewport()
            return redirect(url_for('main.start_server'))

        # session['myport'] = port
        sock.listen(1)
        print("Listening on port %d\n" % port)        
        #time.sleep(2)    
        (clientname,address)=sock.accept()
        print("Connection from %s\n" % str(address))

        # getting keys from currentidentity
        current_identity = CurrentIdentity.query.first()
        if current_identity:
            myid = MyIdentity.query.get(current_identity.identity_no)
        else:
            myid = MyIdentity.query.first()

        hashofpub = str(blake2s((myid.public_key + myid.dil_public_key).encode()).hexdigest())
        print("My Kyber+Dilithium hash: "+hashofpub)
        session['unique_id'] = hashofpub
        print('unique id below: ')
        print(session['unique_id'])

        counter = 0
        messagelist = []
        decapsulatedkey = ""

        pubkeycounter = 0
        pubkeysignal = False
        receivedkyberpubkey = ""

        ctkeycounter = 0
        ctsignal = False
        receivedctkey = ""

        chachacounter = 0
        chachasignal = False
        chachadata = ""

        while 1:
            chunk=clientname.recv(4096)            
            #print(str(address)+':'+chunk.decode(encoding="utf-8"))
            messagelist.append(chunk.decode(encoding="utf-8"))

            
            if (pubkeycounter > 0 or pubkeysignal == True):
                receivedkyberpubkey = messagelist[ctkeycounter+1]
                print("Received public key:"+receivedkyberpubkey)
                hashofpub = str(blake2s(receivedkyberpubkey.encode()).hexdigest())
                print("Hash of public key:"+hashofpub)
                ReceivedPublic.query.delete()
                received_public = ReceivedPublic(key=receivedkyberpubkey)
                db.session.add(received_public)
                db.session.commit()
                # f = open('received.public', 'w')
                # f.write(receivedkyberpubkey)
                # f.close()


                pubkeycounter = 0
                pubkeysignal = False

            if( "==PUBKEY==" in messagelist[counter] ):
                pubkeycounter = counter
                pubkeysignal = True

            if (ctkeycounter > 0 or ctsignal == True):
                #Process KEM key
                receivedctkey = messagelist[ctkeycounter+1]
                #print("KEM key:"+receivedctkey)
                hashofkem = str(blake2s(receivedctkey.encode()).hexdigest())
                #print("HASH of KEM: "+ hashofkem)
                decapsulatedkey = Kyber.decapsulate(receivedctkey, myid.private_key)
                #print("DECAPSULATED KEY:"+decapsulatedkey)
                ctkeycounter = 0
                ctsignal = False
            if( "==KEM-KEY-INIT==" in messagelist[counter] ):
                ctkeycounter = counter
                ctsignal = True
                    #print("KEM detected: "+ str(ctkeycounter))

            
            if (chachacounter > 0 or chachasignal == True):
                #Process CHACHADATA
                chachadata = messagelist[chachacounter+1]
                #print("CHACHA Data:"+str(chachadata))
                chachadata = chachadata.replace('\\"',"\"")
                chachadata = chachadata[1:-1]
                b64 = json.loads(chachadata)
                nonce = b64decode(b64['nonce'])
                ciphertext = b64decode(b64['ciphertext'])
                chachakey = bytes( blake2b( decapsulatedkey.encode(),digest_size=16 ).hexdigest(), "utf-8")
                #print("CHACHAKEY:"+str(chachakey))
                cipher = ChaCha20.new(key=chachakey, nonce=nonce)
                plaintext = cipher.decrypt(ciphertext)
                
                # Printing and sending client message
                new_message = str(plaintext, "utf-8")
                print(str(address)+':'+ new_message)

                msg = new_message.split(',')
                client_host = msg[0].split(':')[0]
                client_port = msg[0].split(':')[1]
                message = msg[1]
                message = {'host': client_host, 'port': client_port, 'message': message}
                socketio.emit('new_message', message, json=True)

                print(req.strip('\n'))
                if client_host == req.strip('\n'):
                    client_host = ''
                print(client_host == req.strip('\n'))

                messg = 'client: ' + str(msg[1])
                user = User.query.filter(User.ip == client_host).filter(User.port == client_port).first()
                if user:
                    mess = Messages(message=messg, user_id=user.id)
                    db.session.add(mess)
                    db.session.commit()
                else:
                    # register user and then save it's mesaage to database
                    # register user
                    newuser = User(username='', ip=client_host, port=client_port)
                    db.session.add(newuser)
                    db.session.commit()

                    # save message to database
                    user = User.query.filter_by(ip=client_host, port=client_port).first()
                    message = Messages(message=messg, user_id=user.id)
                    db.session.add(message)
                    db.session.commit()

                    

                chachacounter = 0
                chachasignal = False
            if( "==CC20-DATA==" in messagelist[counter] ):
                chachacounter = counter
                chachasignal = True
            
            counter += 1
    
    thread = threading.Thread(target=startServer)
    thread.start()
    resp = {'ip': requests.get("https://checkip.amazonaws.com/", 'html.parser').text, 'port': port}
    pr = HostPort.query.first()
    pr.host = resp['ip'].strip('\n')
    pr.port_no = resp['port']
    db.session.commit()
    return resp

class StartClient():
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self, host, port):
        cid = CurrentIdentity.query.first()
        if cid:
            myid = MyIdentity.query.get(cid.identity_no)
        else:
            myid = MyIdentity.query.first()
        if myid == None:
            socketio.emit("flash_message" ,"You cannot send a message without any identity!")
            return redirect(url_for('main.home'))
        self.sock.connect((host,port))
        self.client(host,port,bytes("==PUBKEY==\n","utf-8"))
        time.sleep(0.1)
        self.client(host,port,bytes(myid.public_key,"utf-8"))
        print(f"my public key is: {myid.public_key}")

    def client(self,host,port,msg):
        try:
            self.sock.send(msg)
        except:
            flash('client has been disconnected, please conect to a new one!', 'info')
            return "not connected" 

    def sendMessage(self, host, port, msg):
        #KEMKey = Kyber.encapsulate(receivedkyberpubkey)
        received_public = ReceivedPublic.query.first()
        if received_public==None:
            print("Received.public is empty")
            return "waiting for public key"
        pk = received_public.key
        # f = open('received.public', 'r')
        # pk = f.readline()
        # f.close()            
        KEMKey = Kyber.encapsulate(pk)

        skey = KEMKey[1]
        #print("Decapsulated Secret key:"+ skey)
        ciphertext = KEMKey[0]
        #print("Ciphertext:"+ciphertext)
        hashofkem = str(blake2s(ciphertext.encode()).hexdigest())
        #print("HASH: "+ hashofkem)
        
        chachakey = bytes( blake2b( skey.encode(),digest_size=16 ).hexdigest(), "utf-8")
        print("CHACHAKEY:"+str(chachakey))
        chachacipher = ChaCha20.new(key=chachakey)
        chachaciphertext = chachacipher.encrypt(bytes(msg, "utf-8"))
        nonce = b64encode(chachacipher.nonce).decode('utf-8')
        ct = b64encode(chachaciphertext).decode('utf-8')
        result = json.dumps({'nonce':nonce, 'ciphertext':ct})
        # print("CHACHA Result: "+ result)

        self.client(host,port,bytes("==KEM-KEY-INIT==\n","utf-8"))
        time.sleep(0.1)
        self.client(host,port,bytes(ciphertext,"utf-8"))
        time.sleep(0.1)
        self.client(host,port,bytes("==CC20-DATA==\n","utf-8"))
        time.sleep(0.1)
        self.client(host,port,bytes(result, "utf-8"))
        



@main.route('/newclient', methods=['GET', 'POST'])
def newclient():
    print("new client called")
    host = request.json['host']
    port = int(request.json['port'])
    try:
        new_client = session['current_client'].split(':')
        p_host = new_client[0]
        p_port = int(new_client[1])
        if p_host == host and p_port == port and len(mylist) > 0:
            print("Already connected to client!")
            session['host'] = host
            session['port'] = port
            return "client connected"
        else:
            session.pop('current_client', None)
            raise Error
    except:
        session['host'] = host
        session['port'] = port
        myclient = StartClient()
        print(f"client started and host port is: {host}:{port}")
        try:
            myclient.connect(host , port)
        except Exception as e:
            print(f"exception is from new client: {e}")
            return 'client not available'
        print('here is a list of previously connected clients:')
        print(mylist)
        mylist.clear()
        mylist.append({'obj': myclient, 'host': host, 'port': port})
        session['current_client'] = f"{host}:{port}"
        return "client connected"
    return 'client not available'


@main.route('/send_message', methods=['POST'])
def send_message():
    message = request.json['sendMessage']
    host = request.json['host']
    port = request.json['port']
    message = f"{host}:{port}, {message}"
    try:
        function = mylist[-1]['obj']
    except Exception as e:
        print(f"Excetption is: {e}")
        return "not connected"

    port = mylist[-1]['port']
    host = mylist[-1]['host']

    can_send_message = True
    try:
        resp = function.sendMessage(host, int(port), message)
        print(resp)
        if resp == "waiting for public key":
            socketio.emit('flash_message', "Waiting for client's public key!")
            can_send_message = False
    except Exception as e:
        print(f"Excetption is: {e}")
        return "not connected"
    session['current_client'] = f"{host}:{port}" 

    if can_send_message:
        # saving messages to database:
        user = User.query.filter(User.ip == host).filter(User.port == port).first()
        message_only = str(message.split(',')[-1])
        message = Messages(message='me: ' + message_only, user_id=user.id)
        db.session.add(message)
        db.session.commit()

    return f"{message}"

@main.route('/check_client', methods=['POST'])
def check_client():
    host = request.json['host']
    port = request.json['port']

    try:
        liport = mylist[-1]['port']
        lihost = mylist[-1]['host']

        print("comparing ports:")
        print(str(liport)==str(port))

        if str(liport)==str(port) and str(host)==str(lihost):
            return "True"
        else:
            return "False"
    except:
        return "False"



# conversation starts here
@main.route('/chat/<int:id>')
def chat(id):
    user = User.query.get(id)
    port = user.port
    ip = user.ip
    username = user.username

    messages = [i.message for i in user.user_messages]
    pr = HostPort.query.first()
    myip = pr.host
    myport = pr.port_no

    return render_template('conversation/chat.html', messages=messages, 
                            ip=ip, port=port, username=username 
                            ,home='home', myip=myip,
                                        myport=myport)
