#!/bin/bash

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "Needs to be run as root"
    exit
fi

# Necessary for psycopg2 installation (lmc-packages does not run install.sh
# when doing a package build)
sudo apt-get install libpq-dev -y

rm -fr /opt/lmc-python
virtualenv -p /usr/bin/python2.7 /opt/lmc-python
source /opt/lmc-python/bin/activate
pip install git+git://github.com/cybera/lmc-python-lib.git@no-pyrax
deactivate
