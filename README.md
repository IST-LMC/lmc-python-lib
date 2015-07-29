lmc-python-lib
==============

### Getting started

#### Creating the development environment

1. Put your credentials in vagrant/credentials (files with the extension .openrc or .sh in the credentials folder will be ignored by git)

2. Create your vagrant VM:

	*VirtualBox provider:*

	```bash
	vagrant box add ubuntu/trusty64
	vagrant up
	```

	*VMWare provider:*

	```bash
	vagrant box add cybera/ubuntu-trusty
	vagrant up
	```

#### Do everything

```bash
source /vagrant/credentials/your-credentials.openrc
/vagrant/scripts/rebuild-virtualenv.sh
/vagrant/scripts/setup-test-containers.sh
/vagrant/scripts/test-lmc-python.py
```

#### scripts

*rebuild-virtualenv.sh*

Creates a virtual environment in /usr/local/lmc-python and installs lmc-python-lib and its dependencies in that location. If run again, it will remove the old version before re-creating.

*setup-test-containers.sh*

Creates `lmc-python-test` and `lmc-python-test_segments` for use with the test script.

*test-lmc-python.py*

Example script to exercise the lmc-python-lib library.

#### Notes

- Currently the containers used in the test are hardcoded, so these tests can only be run by a single person in an OpenStack project.

- Containers aren't given read/write ACLs so that these can be tested (Coming soon!)
