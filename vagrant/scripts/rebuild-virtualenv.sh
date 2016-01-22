#!/bin/bash

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "Needs to be run as root"
    exit
fi

rm -fr /usr/local/lmc-python
virtualenv -p /usr/bin/python2.7 /usr/local/lmc-python
source /usr/local/lmc-python/bin/activate
pip install git+git://github.com/cybera/lmc-python-lib.git@no-pyrax
deactivate
