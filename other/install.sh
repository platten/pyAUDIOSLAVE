#!/bin/bash

echo Installing prereqs
sudo apt-get -y install python-software-properties
sudo add-apt-repository ppa:shiki/mediainfo
sudo apt-get update
sudo apt-get -y install build-essential git libboost1.42-dev libtag1-dev zlib1g-dev cifs-utils python-pip python-dev ffmpeg lame flac faad faac mpg123 mediainfo python-demjson
sudo apt-get -y install rabbitmq-server redis-server mongodb-server screen

echo Setting up echoprint-codegen
cd ~
git clone http://github.com/echonest/echoprint-codegen.git
cd echoprint-codegen/src
make
make install

echo Setting up python prereqs
sudo pip install python-magic pymediainfo pyechonest celery pymongo redis

echo Installing pyAUDIOSLAVE
cd ~
git clone http://github.com/platten/pyAUDIOSLAVE
cd pyAUDIOSLAVE
sudo python setup.py install