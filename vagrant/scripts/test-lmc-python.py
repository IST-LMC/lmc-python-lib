#!/usr/local/lmc-python/bin/python

import lmc, os

print "**** creating test files ****"
os.system("mkdir -p /tmp/lmc-python-test/upload")
os.system("mkdir -p /tmp/lmc-python-test/download")
os.system("echo testing >/tmp/lmc-python-test/upload/test.txt")

print "**** listing objects (should be none) ****"
lmc.swift.list_objects("lmc-python-test")

print "**** uploading to swift ****"
lmc.swift.upload("lmc-python-test", "test.txt", "/tmp/lmc-python-test/upload", 60)

print "**** listing objects (should have test.txt) ****"
print lmc.swift.list_objects("lmc-python-test")[0]['name']

print "**** fetching test.txt from swift ****"
lmc.swift.cache_fetch("lmc-python-test", "test.txt", "/tmp/lmc-python-test/download")

print "**** diff upload/download versions ****"
os.system("diff -s /tmp/lmc-python-test/upload/test.txt /tmp/lmc-python-test/download/test.txt")

print "**** deleting test files ****"
os.system("rm -fr /tmp/lmc-python-test")

# TODO:
# 1. test segmented upload w/ ttl set (can use the segment_size optional param to make the
# segment sizes smaller for a quicker test)
# 2. test fetching the most recent object in a container
# 3. test fetching the object closest to a time in a container
# 4. test that cache fetch doesn't grab the file if it's present on the local system
# 5. test that ACLs work properly:
#		a. create users that can't create containers but can read/write to them
#		b. create users that can read from a container but can't write to it
# 6. test that setting the ttl properly expires objects and any related segments
