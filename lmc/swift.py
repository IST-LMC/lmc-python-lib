import pyrax, os, swiftclient

def connection():
	pyrax.settings.set('identity_type', 'keystone')
	pyrax.set_setting("auth_endpoint", os.environ["OS_AUTH_URL"])
	pyrax.set_credentials(username=os.environ["OS_USERNAME"], api_key=os.environ["OS_PASSWORD"], tenant_id=os.environ["OS_TENANT_ID"])
	conn = pyrax.connect_to_cloudfiles(os.environ["OS_REGION_NAME"])
	conn.max_file_size = 1073741823  # 1GB - 1
	return conn

def fetch(bucket, name, to_folder):
	swift_connection = connection()
	cont = swift_connection.get_container(bucket)
	obj = cont.get_object(name)
	fetch_path = os.path.join(to_folder, name)
	file = open(fetch_path, "w")
	for chunk in obj.fetch(chunk_size=1024*1024):
		file.write(chunk)
	file.close()

def cache_fetch(bucket, name, cache_folder):
	cache_path = os.path.join(cache_folder, name)
	# TODO: also fetch if checksums don't match (don't just assume the file's good)
	if not os.path.isfile(cache_path):
		fetch(bucket=bucket, name=name, to_folder=cache_folder)

def upload(bucket, name, from_folder):
	swift_connection = connection()
	cont = swift_connection.get_container(bucket)
	from_path = os.path.join(from_folder, name)
	# TODO: Only update if checksums don't match
	cont.upload_file(from_path, name)

def list_objects(bucket, ignore_partial=True):
	swift_connection = connection()
	cont = swift_connection.get_container(bucket)
	objects = cont.get_objects()
	if ignore_partial:
		return [obj for obj in objects if obj.content_type != 'application/octet-stream']
	else:
		return objects
