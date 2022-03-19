import argparse
import logging
import asyncio
import subprocess

from kademlia.network import Server

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

server = Server()
# Get Computer Loki Address
lokiAddress = subprocess.getoutput("dig @127.3.2.1 -t cname +short localhost.loki")
print(lokiAddress)
# Exit if Lokinet isn't running
if lokiAddress == "":
    print("Please start Lokinet.")
    exit()

def connect_to_bootstrap_node():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try: 
        loop.run_until_complete(server.save_state_regularly("DHT.dat",60))
    except: 
        pass
    loop.run_until_complete(server.listen(8469, lokiAddress))
    bootstrap_node = ("rgnbbdskjzjf9789uiseq68jofudtpwwgsqqwtdzbyxsyq84tamo.loki", 8468)
    loop.run_until_complete(server.bootstrap([bootstrap_node]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def main():
    try:
        server.load_state("DHT.dat")
    except:
        pass

    connect_to_bootstrap_node()
    #else:
    #    create_bootstrap_node()


if __name__ == "__main__":
    main()
