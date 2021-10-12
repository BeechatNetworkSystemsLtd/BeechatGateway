# Beechat Gateway
## _Internet-based P2P chat utilising post quantum cryptography_

![BNSLTD](https://beechat.network/wp-content/uploads/2021/02/powered-by-1.png)

## Introduction

This is a simple to use, Python-based TCP socket chat utilising Kyber-Py encryption. The goal is to create a peer-to-peer chat utilising post-quantum cryptography with no third party or rendezvous server (ie: fully decentralised). The chat uses a Flask server to provide a WSGI intuitive user interface. Currently, users can utilise the project as a P2P chat, however the goal is to use this project as an Internet gateway for the Beechat Network in order to connect far away nodes.

## Download
-------------------


How to run the program
-------------------
1) Install Python 3 (Version 3.9.5) and Pip on your computer.
2) Download this repository and extract into a folder of your choice.
3) For Linux go to 3a, for Windows, go to 3b: 
3a) On Debian/Ubuntu Linux distributions, open Terminal within that folder and type ```./install.sh``` then press ```[ENTER]```. The script will (1) prompt to install ```unzip``` (2) unzip ```main/static.zip``` (3) install python packages.
4) After the packages have installed, you are ready to run the program. To run it type ```python3 main.py```.
5) Go to your web browser and type the address listed in the Terminal, it should be ```127.0.0.1:5000```.

Repository Contents
-------------------

* **/main.py** - Main file to run the server/client
* **/myapp** - Folder containing the project files

Features
-------------------

* **Multiple identities:** Switch between different Kyber keypairs within the application
* **SQLite DB:** Store all your conversations in a .db file for easy transport
* **Port settings:** Assign a random port to the application, or set it on your own manually
* **File sending:** (in progress)


Connection Issues
-------------------
Some users might be encountering problems with connecting to other users and getting a ```111 connection refused``` error message in the Terminal. This is due to port forwarding and firewalls. Please open the port you are using via your router and your PC's firewall settings. 


Product Versions
-------------------

REV1.0 - first design revision


License Information
-------------------
The software is released under [Creative Commons ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).

Distributed as-is; no warranty is given.


Suggestions? Corrections? Pull requests?
-------------------
If you have improvements to Beechat Gateway, send us your pull requests!

