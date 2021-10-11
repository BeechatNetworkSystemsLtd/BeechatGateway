#!/bin/sh
sudo apt-get install unzip
mkdir ./myapp/static/
unzip ./myapp/static.zip -d ./myapp/static/
pip3 install -r requirements.txt
