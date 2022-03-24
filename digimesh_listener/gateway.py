import dilithium
from digi.xbee.devices import XBeeDevice
import threading
import time
import subprocess
import random

device = XBeeDevice("/dev/ttyUSB1", 9600)
i = 0
received_messages_list = []
lokiAddr_and_nonce = ""

##### DIGIMESH GATEWAY
def runDigimeshServer():
    var = False
    global runDigimesh
    def listener():
        def returnBroadcast(remote_device):
            device.send_data_broadcast(remote_device)
            

        while var:            
            global device
            global received_messages_list
            global lokiAddr_and_nonce
            pubkey_Bool = False
            lokiAddr_Bool = False
            receivedSignature = ""
            receivedPubkey = ""
            print("Challenge: " + lokiAddr_and_nonce)
            try:
                device.open()
                device.flush_queues()
                print("#t2: Waiting for data...\n")
                while var:
                    xbee_message = device.read_data()
                    if xbee_message is not None:
                        print("#t2: From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
                                                xbee_message.data.decode()))
                        #Check if we received a signed response
                        received_xbee_message = (xbee_message.remote_device.get_64bit_addr(),xbee_message.data.decode())

                        if(received_xbee_message[1].startswith("L_")):
                            print("received lokiAddr packet")
                            received_messages_list.append(received_xbee_message[1])
                            print("added lokiAddr packet to list:\n"+str(received_xbee_message[1]))
                        if(received_xbee_message[1].endswith("_E")):
                            #Send back OK
                            returnBroadcast(received_xbee_message[0],"OK")

                        if(received_xbee_message[1].startswith("==END-PUBKEY==")):
                            pubkey_Bool = False
                            print("Final pubkey:"+receivedPubkey)
                            device.flush_queues()
                            time.sleep(5)
                        if(received_xbee_message[1].startswith("==END-SIGNED_LOKIADDR+NONCE==")):
                            lokiAddr_Bool = False
                            print("Final signed lokiaddr+nonce: "+ receivedSignature)
                            print("Final message: "+ dilithium.checkmessage(receivedPubkey,receivedSignature))
                            if(lokiAddr_and_nonce == dilithium.checkmessage(receivedPubkey,receivedSignature)):
                                print("Challenge success... Posting to Kademlia...")
                                

                        if(pubkey_Bool):
                            receivedPubkey += received_xbee_message[1]
                        if(lokiAddr_Bool):
                            receivedSignature += received_xbee_message[1]
                        if(received_xbee_message[1].startswith("==PUBKEY==")):
                            pubkey_Bool = True

                        if(received_xbee_message[1].startswith("==SIGNED_LOKIADDR+NONCE==")):
                            lokiAddr_Bool = True


            finally:
                if device is not None and device.is_open():
                    device.close()
    while runDigimesh:
        t2 = threading.Thread(target=listener)
        print("#t1: Starting #t2 Listener Thread")
        var = True
        t2.start()
        time.sleep(60)
        var = False
        t2.join()
        print("#t1: Listener Thread Done")
        print("#t1: Broadcast initiated")

        nonce = random.getrandbits(16)
        i = 0
        global lokiAddr_and_nonce
        lokiAddr_and_nonce = str(lokiAddress + ";" + str(nonce)+"_E")
        if device is not None and device.is_open():
            device.close()
        device.open()
        while(i<len(lokiAddr_and_nonce)):
            device.send_data_broadcast("L_" + lokiAddr_and_nonce[i:i+61])
            i = i + 61
        device.close()
        print("#t1: Broadcast done")
        


lokiAddress = subprocess.getoutput("dig @127.3.2.1 -t cname +short localhost.loki")
#lokiAddress = "TESTLOKIADDRESS.loki"


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
print("#t0: Total broadcasts: "+ str(i))
