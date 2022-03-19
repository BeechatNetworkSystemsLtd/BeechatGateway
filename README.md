# Beechat Gateway
## _Digimesh-Lokinet bridge based on Kademlia to allow connections between mesh islands_

![BNSLTD](https://beechat.network/wp-content/uploads/2021/02/powered-by-1.png)

## Introduction

Beechat Gateway is a Python-based app users can access via their browsers, to set up a Beechat Gateway for themselves, and the local community. Setting up a Gateway allows users to communicate with other users that are in a different radio network. This allows people without Internet to communicate with each other accross vast distances and continents, in this case, only Gateways need Internet access, but not the end-user.

 Requirements
 -------------------

 1) Linux computer, such as a Raspberry Pi 4 with a weather proof enclosure
 2) Clip board with an antenna connected to the RPi
 3) (Optional) Solar panel for the RPi and battery to make the system self-sufficient
 

## Download & Install
-------------------

1) Install the latest Python 3 (Version 3.9.5) and Pip on the computer.
2) Download this repository and extract into a folder of your choice.
3) Open Terminal within that folder and type:
   * ```./install.sh``` then press ```[ENTER]```. 
   * The script will ask to install ```python3``` and ```pip```, press [ENTER], then wait for it to install and run
   * The script will ask to install ```lokinet```, press [ENTER], then wait for it to install and run
4) After the packages have installed, you are ready to run the program. To run it type ```python3 main.py``` in the main folder.
5) Go to your web browser and type the address listed in the Terminal, it should be ```127.0.0.1:5000```.

Repository Contents
-------------------

* **/main.py** - Main file to run the Gateway
* **/myapp** - Folder containing the project files
* **/support_node** - Folder containing node.py and systemd unit file to connect to the Beechat Kademlia test network
* **/bootstrap_node** - Folder containing node.py and systemd unit file to set up your own Kademlia network

Features
-------------------

* **Retrieve Beechat address information:** Switch between different Kyber keypairs within the application
* **Lokinet addressing:** Store all your conversations in a .db file for easy transport
* **Beechat protocol over Digimesh:** Assign a random port to the application, or set it on your own manually


Versions
-------------------

REV1.0 - first revision

License Information
-------------------
The software is released under [Creative Commons ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/).

Distributed as-is; no warranty is given.


Suggestions? Corrections? Pull requests?
-------------------
If you have improvements to Beechat Gateway, send us your pull requests!

