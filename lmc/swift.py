import os, swiftclient, swiftclient.service
from swiftclient.service import SwiftUploadObject

import warnings
warnings.filterwarnings("ignore", message="Providing attr without filter_value to get_urls\(\) is deprecated")

CONN = None
SWIFT_SERVICE = None
upload_buffer = {}
download_buffer = {}
upload_success_message = None

def swift_connection():
    global CONN
    if not CONN:
        CONN = swiftclient.Connection(
            user=os.environ["OS_USERNAME"],
            tenant_name=os.environ["OS_TENANT_NAME"],
            key=os.environ["OS_PASSWORD"],
            authurl=os.environ["OS_AUTH_URL"],
            auth_version=2)
    # conn.max_file_size = 1073741823  # 1GB - 1
    return CONN

def swift_service():
    global SWIFT_SERVICE
    if not SWIFT_SERVICE:
        SWIFT_SERVICE = swiftclient.service.SwiftService({
            "os_username": os.environ["OS_USERNAME"],
            "os_tenant_name": os.environ["OS_TENANT_NAME"],
            "os_password":os.environ["OS_PASSWORD"],
            "os_auth_url": os.environ["OS_AUTH_URL"],
            "auth_version": 2 })
    return SWIFT_SERVICE

def fetch(bucket, name, to_folder):
    try:
        fetch_path = os.path.join(to_folder, name)
        download = swift_service().download(bucket, [ name ], { 'out_file': fetch_path }).next()
        return 'success' in download and download['success']
    except swiftclient.exceptions.ClientException as e:
        if(e.http_status == 404):
            print "Error: object '%s' not found in container '%s'" % (name, bucket)
            return False
        else:
            raise e

def cache_fetch(bucket, name, cache_folder):
    cache_path = os.path.join(cache_folder, name)
    # TODO: also fetch if checksums don't match (don't just assume the file's good)
    if not os.path.isfile(cache_path):
        return fetch(bucket=bucket, name=name, to_folder=cache_folder)
    else:
        return True

def upload(bucket, name, from_folder, ttl=None, segment_size="400M", buffer_size=0):
    global upload_buffer

    from_path = os.path.join(from_folder, name)

    headers = []
    if ttl:
        delete_after_header = 'X-Delete-After:%i' % ttl
        headers.append(delete_after_header)

    options = {
        'header': headers,
        'segment_size': __normalized_segment_size(segment_size)
    }

    upload_object = SwiftUploadObject(from_path, object_name=name, options=options)
    if bucket not in upload_buffer:
        upload_buffer[bucket] = []

    upload_buffer[bucket].append(upload_object)
    if len(upload_buffer[bucket]) <= buffer_size:
        return
        
    flush_upload_buffer(bucket)

def flush_upload_buffer(bucket):
    global upload_buffer
    global upload_success_message

    # Nothing buffered
    if bucket not in upload_buffer:
        return

    ### Workaround for: https://bugs.launchpad.net/python-swiftclient/+bug/1478830
    segments = []
    segment_container = None
    ### /Workaround

    for r in swift_service().upload(bucket, upload_buffer[bucket]):
        if not r['success']:
            # Only raise an error if it's on an object. We don't expect containers
            # to be able to be created by users with reduced permissions, but they
            # can upload objects.
            if not ('action' in r and r['action'] == "create_container"):
                raise r['error']
        else:
            ### Workaround for: https://bugs.launchpad.net/python-swiftclient/+bug/1478830
            if 'action' in r and r['action'] == "upload_segment":
                segment_path = [x for x in r['segment_location'].split(os.path.sep) if x != '']
                segment_container = segment_path.pop(0)
                segments.append(os.path.sep.join(segment_path))
            ### /Workaround
            else:
                if upload_success_message:
                    print upload_success_message % r['object']

    ### Workaround for: https://bugs.launchpad.net/python-swiftclient/+bug/1478830
    if segment_container and len(segments) > 0:
        set_expiration_error = False
        for r in swift_service().post(segment_container, segments, { 'header': [ delete_after_header ]}):
            if not r['success']:
                set_expiration_error = True
        print "WARNING: Error response in setting expiration for some segments on: %s." % name
        print "WARNING: The segments will likely still end up with a correct expiration time."
    ### /Workaround

    del upload_buffer[bucket]

    # TODO: Only update if checksums don't match

def list_objects(bucket, ignore_partial=True):
    objects = []
    listing_chunks = swift_service().list(bucket)
    for listing_chunk in listing_chunks:
        objects.extend([ SwiftObject(obj['name'], container=bucket, raw_object=obj) for obj in listing_chunk['listing'] ])
            
    if ignore_partial:
        # TODO: It turns out that application/octet-stream is also what plain .gz files get labelled as.
        # We need a better indicator for when a file is part of a larger object.
        return [obj for obj in objects if obj['content_type'] != 'application/octet-stream']
    else:
        return objects

# Usage:
#
# for obj in lmc.swift.object_iter("some_container"):
#     do_something_with(obj)
class object_iter:
    def __init__(self, bucket):
        self.bucket = bucket
        self.listing_chunks = swift_service().list(bucket)
        self.listing_iter = iter(next(self.listing_chunks)['listing'])
    def __iter__(self):
        return self
    def next(self):
        try:
            obj = next(self.listing_iter)
            return SwiftObject(obj['name'], container=self.bucket, raw_object=obj)
        except StopIteration:
            self.listing_iter = iter(next(self.listing_chunks)['listing'])
            obj = next(self.listing_iter)
            return SwiftObject(obj['name'], container=self.bucket, raw_object=obj)

def find_objects(bucket, regex):
    return [obj for obj in list_objects(bucket) if regex.match(obj['name'])]

def get_object(bucket, name):
    stat_info = next(swift_service().stat(bucket, [ name ]))
    if stat_info['success']:
        return SwiftObject(name, container=bucket, metadata=stat_info['headers'])
    else:
        return None

def expire_object(bucket, name, ttl):
    delete_after_header = 'X-Delete-After:%i' % ttl
    result = next(swift_service().post(bucket, [ name ], { 'header': [ delete_after_header ]}))
    if not result['success']:
        print "ERROR: Couldn't set ttl on %s/%s" % (bucket, name)

# Get the x-timestamp of the object (this involves a metadata query)
def get_timestamp(obj):
    return float(obj.get_metadata()['x-timestamp'])

# Sort objects in the given list by their x-timestamp. If descending=True, the list will
# start with the highest value first. The default will return a list with the lowest value
# first.
#
# Warning: Metadata gets fetched from every object in the list using this function. On large
# lists, it could become quite time consuming.
def sort_objects_by_time(obj_list, descending=False):
    return sorted(obj_list, key=get_timestamp, reverse=descending)

# Find the object with the time closest to the given timestamp. If there is an exact match,
# the matching object will be returned. Otherwise, the object returned will be the first
# object before the timestamp. If after=True, it will be the first object equal to or after
# the timestamp.
#
# Warning: Metadata gets fetched from every object in the list using this function. On large
# lists, it could become quite time consuming.
def object_closest_to_time(obj_list, timestamp, after=False):
    sorted_objects = sort_objects_by_time(obj_list, descending=(not after))
    for obj in sorted_objects:
        if after and get_timestamp(obj) >= timestamp:
            return obj
        elif not after and get_timestamp(obj) <= timestamp:
            return obj
    return None

def most_recent_object(obj_list_or_bucket_name):
    if not isinstance( obj_list_or_bucket_name, (frozenset, list, set, tuple) ):
        obj_list = list_objects(obj_list_or_bucket_name)
    else:
        obj_list = obj_list_or_bucket_name
    sorted_list = sort_objects_by_time(obj_list, descending=True)

    if len(sorted_list) >= 1:
        return sorted_list[0]
    else:
        return None

class SwiftObject:
    def __init__(self, name, container, raw_object=None, metadata=None):
        self.name = name
        self.raw_object = raw_object
        self.container = container
        self.metadata = metadata

    def __getitem__(self, key):
        return self.raw_object[key]

    def get_metadata(self):
        if not self.metadata:
            self.metadata = next(swift_service().stat(self.container, [ self.name ]))['headers']
        return self.metadata

def __normalized_segment_size(segment_size):
    # Adapted from python-swiftclient code
    try:
        # If segment size only has digits assume it is bytes
        return int(segment_size)
    except ValueError:
        try:
            size_mod = "BKMG".index(segment_size[-1].upper())
            multiplier = int(segment_size[:-1])
        except ValueError:
            print("Invalid segment size")

        return str((1024 ** size_mod) * multiplier)
