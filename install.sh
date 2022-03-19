#!/bin/sh
sudo chmod +X ./reqs/lokinetInstaller.sh
sudo ./reqs/lokinetInstaller.sh
sudo apt install python3 python3-pip
pip3 install kademlia
pip3 install -r requirements.txt
