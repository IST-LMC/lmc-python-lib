from setuptools import setup, find_packages
setup(name='lmc-python-lib',
      version='1.4',
      packages=find_packages(),
	  install_requires = [
	  	'python-swiftclient',
		'python-keystoneclient',
		'certifi',
		'pyopenssl',
		'ndg-httpsclient',
		'pyasn1',
        'psycopg2']
      )
