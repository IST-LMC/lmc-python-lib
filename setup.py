from setuptools import setup, find_packages
setup(name='lmc-python-lib',
      version='1.0',
      packages=find_packages(),
	  install_requires = [
	  	'python-swiftclient',
		'python-keystoneclient']
      )
