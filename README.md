lmc-python-lib
==============

### Getting started

#### Cloning the repository

```bash
git clone git@github.com:cybera/lmc-python-lib.git
```

#### Creating the development environment

1. Put your credentials in vagrant/credentials (files with the extension .openrc or .sh in the credentials folder will be ignored by git)

2. Create your vagrant VM:

	*VirtualBox provider:*

	```bash
	cd vagrant
	vagrant box add ubuntu/trusty64
	vagrant up --provider virtualbox
	```

	*VMWare provider:*

	```bash
	cd vagrant
	vagrant box add cybera/ubuntu-trusty
	vagrant up --provider vmware_fusion
	```

#### SSH into the VM

```bash
cd vagrant
vagrant ssh
```

#### Do everything

```bash
source /vagrant/credentials/your-credentials.openrc
sudo /vagrant/scripts/rebuild-virtualenv.sh
/vagrant/scripts/setup-test-containers.sh
/vagrant/scripts/test-lmc-python.py
```

#### Scripts

*rebuild-virtualenv.sh*

Creates a virtual environment in /opt/lmc-python and installs lmc-python-lib and its dependencies in that location. If run again, it will remove the old version before re-creating.

*setup-test-containers.sh*

Creates `lmc-python-test` and `lmc-python-test_segments` for use with the test script.

*test-lmc-python.py*

Example script to exercise the lmc-python-lib library.

#### Installing lmc-python-lib via pip

*(...as done in the rebuild-virtualenv.sh script...)*

```bash
pip install git+git://github.com/cybera/lmc-python-lib.git@master
```

#### Building an Ubuntu install package

TODO...

#### Notes

- Currently the containers used in the test are hardcoded, so these tests can only be run by a single person in an OpenStack project.

- Containers aren't given read/write ACLs so that these can be tested (Coming soon!)
