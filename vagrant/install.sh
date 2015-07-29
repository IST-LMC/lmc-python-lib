#!/bin/bash

sudo apt-get update
sudo apt-get install git -y
sudo apt-get install python-pip -y
sudo apt-get install python-dev -y
sudo apt-get install libffi-dev -y
sudo apt-get install libssl-dev -y
sudo pip install virtualenv

# helpful tools (not really necessary for the python library)
sudo apt-get install vim -y
