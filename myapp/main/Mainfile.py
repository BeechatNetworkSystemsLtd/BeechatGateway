#! /usr/bin/env python
from hashlib import blake2s
import socket
import sys
import time
import threading
sys.path.append("./")
import kyber as Kyber
import dilithium as Dilithium
from base64 import b64encode, b64decode
import json
from Crypto.Cipher import ChaCha20
from hashlib import blake2b
import requests
import upnpcclient

receivedkyberpubkey = ""

#OPEN A PORT
try:
    f = open('openport.txt', 'r')
    port = f.readline()
    f.close()
    if (port == ""):
        raise ValueError
    print("Port is: "+ port)
except:
    upnpcobject = upnpcclient.port_manager()
    upnpcobject.unmap_ports()
    port=upnpcobject.mapport()[1]
    print("Using port: "+ port)    
    f = open('openport.txt', 'w')
    f.write(str(port))
    f.close()

port = int(port)

#CREATE KEYS
data = []
try:
    with open('user.json') as json_file:
        data = json.load(json_file)
        if (not data):
            raise ValueError
except:
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

    with open('user.json', 'w') as fp:
        json.dump(myuser, fp,  indent=4)
    data = myuser

privatekey = data["Ki"]
publickey = data["Kp"]


class Server(threading.Thread):
    def run(self):
        print("My Kyber public key: "+ data["Kp"])
        hashofpub = str(blake2s(data["Kp"].encode()).hexdigest())
        print("Hash of my Kyber public key: "+hashofpub)

        print("My Dilithium public key: "+ data["Dp"])
        dilhashofpub = str(blake2s(data["Dp"].encode()).hexdigest())
        print("Hash of my Dilithium public key: "+dilhashofpub)

        hashofpub = str(blake2s((data["Kp"] + data["Dp"]).encode()).hexdigest())
        print("My Kyber+Dilithium hash: "+hashofpub)

        req = requests.get("https://checkip.amazonaws.com/", 'html.parser')
        print("Your external IP is: "+ req.text)
    
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Server started successfully\n")
        hostname=''

        self.sock.bind((hostname,port))
        self.sock.listen(1)
        print("Listening on port %d\n" %port)        
        #time.sleep(2)    
        (clientname,address)=self.sock.accept()
        print("Connection from %s\n" % str(address))
        
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
                f = open('received.public', 'w')
                f.write(receivedkyberpubkey)
                f.close()

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
                decapsulatedkey = Kyber.decapsulate(receivedctkey,privatekey)
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
                print("CHACHA Data:"+str(chachadata))
                b64 = json.loads(chachadata)
                nonce = b64decode(b64['nonce'])
                ciphertext = b64decode(b64['ciphertext'])
                chachakey = bytes( blake2b( decapsulatedkey.encode(),digest_size=16 ).hexdigest(), "utf-8")
                #print("CHACHAKEY:"+str(chachakey))
                cipher = ChaCha20.new(key=chachakey, nonce=nonce)
                plaintext = cipher.decrypt(ciphertext)
                print(str(address)+':'+ str(plaintext, "utf-8") )
                chachacounter = 0
                chachasignal = False
            if( "==CC20-DATA==" in messagelist[counter] ):
                chachacounter = counter
                chachasignal = True
            
            counter += 1


class Client(threading.Thread):    
    def connect(self,host,port):
        self.sock.connect((host,port))
    def client(self,host,port,msg):               
        sent=self.sock.send(msg)           
        #print("Sent\n")
    def run(self):
        try:
            self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                host=input("Enter the hostname\n>>")
                if host=='exit':
                    exit()
                port=int(input("Enter the port\n>>"))
                if host=='exit':
                    exit()
            except EOFError:
                print("Error")
                return 1
            
            print("Connecting\n")
            s=''
            # Here there should be a block of code for loading public keys of the other person, 
            # Then creating an encapsulated key
            # Then signing the ct.key with Dilithium
            # Then Sending the encapsulated + signed to the other host
            # This secret will be used by this node so they can decrypt data.
            # They have to send us their own encapsulated secret and we use it to read data they send us
            
            self.connect(host,port)
            print("Connected\n")
            self.client(host,port,bytes("==PUBKEY==\n","utf-8"))
            time.sleep(0.1)
            self.client(host,port,bytes(publickey,"utf-8"))


            while 1:            
                print("Waiting for message\n")
                msg=input('>>')
                if msg=='exit':
                    break
                if msg=='':
                    continue

                #KEMKey = Kyber.encapsulate(receivedkyberpubkey)
                f = open('received.public', 'r')
                pk = f.readline()
                f.close()            
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
                #print("CHACHA Result: "+ result)

                self.client(host,port,bytes("==KEM-KEY-INIT==\n","utf-8"))
                time.sleep(0.1)
                self.client(host,port,bytes(ciphertext,"utf-8"))
                time.sleep(0.1)
                self.client(host,port,bytes("==CC20-DATA==\n","utf-8"))
                time.sleep(0.1)
                self.client(host,port,bytes(result,"utf-8"))                            
            return(1)
        except KeyboardInterrupt as details:
            upnpcobject.unmap_ports()
            print("CTRL-C exception!", details)

"""
from flask import Flask
from flask import render_template
from flask import request, redirect, Response
import random, json

app = Flask(__name__)

@app.route('/')
def output():
	# serve index template
	return render_template('index2.html', name='Joe')
@app.route('/receiver', methods = ['POST'])
def worker():
	# read json + reply
	data = request.get_json()
	result = ''
	for item in data:
		# loop over every row
		result += str(item['make']) + ''
	return result
"""

if __name__=='__main__':
    srv=Server()
    srv.daemon=True

    print("Starting server")
    srv.start()
    time.sleep(1)
    print("Starting client")
    cli=Client()
    print("Started successfully")
    cli.start()