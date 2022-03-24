from audioop import add
import dilithium
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress
import threading
import time

device = XBeeDevice("/dev/ttyUSB0", 9600)
var = True
received_xbee_message = ("","")
i = 0
runDigimesh = False

keys = dilithium.createkeys()

privkey = keys[0]
pubkey = keys[1]
address = keys[2]
print("Address: "+ address)
received_messages_list = []


####DIGIMESH APP IMITATION

def runDigimeshServer():
    var = False
    global runDigimesh

    def listener():
        receivedLokiAddr_and_nonce = ""
        def returnBroadcast(remote_device, lokiAddr_and_nonce):
            global keys
            print("Sending your Beechat address, pubkey and signed lokinet address + nonce...")
            #Sending BA
            remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(str(remote_device)))
            device.send_data(remote_device, keys[2])
            #Sending pubkey
            print("Pubkey: "+ keys[1])
            i = 0
            device.send_data(remote_device, "==PUBKEY==")
            while(i< len(keys[1])):
                device.send_data(remote_device, keys[1][i:i+61])
                print("sending: "+ keys[1][i:i+61])
                i = i+61
            device.send_data(remote_device, "==END-PUBKEY==")
            time.sleep(20)
            #Sending signed lokinet address
            signedLokiAddr_and_nonce = dilithium.signmessage(keys[0], lokiAddr_and_nonce)
            i = 0
            print("Signed LokiAddr+nonce: "+ signedLokiAddr_and_nonce)
            device.send_data(remote_device, "==SIGNED_LOKIADDR+NONCE==")
            while(i<len(signedLokiAddr_and_nonce)):
                device.send_data(remote_device, signedLokiAddr_and_nonce[i:i+61])
                i = i+61
            device.send_data(remote_device, "==END-SIGNED_LOKIADDR+NONCE==")
            

        global received_xbee_message
        lokiAddr_Bool = False
        while var:
            global device
            global received_messages_list

            print("Waiting for LokiAddr + nonce...\n")
            while var:
                
                
                xbee_message = device.read_data()
                if xbee_message is not None:

                    print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
                                            xbee_message.data.decode()))
                    print("ADDR: "+ str(xbee_message.remote_device.get_64bit_addr()))
                    print("DATA: "+ xbee_message.data.decode())
                    received_xbee_message = (xbee_message.remote_device.get_64bit_addr(),xbee_message.data.decode())
                    
                    if(received_xbee_message[1].startswith("==END-GATEWAY-BROADCAST==")):
                        lokiAddr_Bool = False
                        print("Final LOKIADDR+NONCE:"+receivedLokiAddr_and_nonce)
                        device.flush_queues()
                        time.sleep(5)
                        returnBroadcast(received_xbee_message[0],receivedLokiAddr_and_nonce)

                    if(lokiAddr_Bool == True):
                        receivedLokiAddr_and_nonce += received_xbee_message[1]
                        print("Current: "+ receivedLokiAddr_and_nonce)

                    if(received_xbee_message[1] == "==BEGIN-GATEWAY-BROADCAST=="):
                        lokiAddr_Bool = True
                        print("Received Gateway broadcast")
                
    while runDigimesh:
        global device
        device.open()
        t2 = threading.Thread(target=listener)
        print("#t1: Starting #t2 Listener Thread")
        var = True
        t2.start()
        time.sleep(60)
        var = False
        t2.join()
        print("#t1: Listener Thread Done")
        if device is not None and device.is_open():
            device.close()


Digi_t1 = threading.Thread(target=runDigimeshServer)
Digi_t1.daemon = True
print("#t0: Starting Digimesh Server Thread")
runDigimesh = True
Digi_t1.start()

print("#t0: Started Digimesh Server successfully")

time.sleep(240)

runDigimesh = False
Digi_t1.join()
print("#t0: Digimesh Server ended")
#print("#t0: Total broadcasts: "+ str(i))
