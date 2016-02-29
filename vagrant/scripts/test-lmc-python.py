#!/opt/lmc-python/bin/python

import lmc, os, time, sys

class TerminalColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def ok(str):
    print TerminalColor.OKGREEN + str + TerminalColor.ENDC

def warn(str):
    print TerminalColor.WARNING + str + TerminalColor.ENDC

def error(str):
    print TerminalColor.FAIL + str + TerminalColor.ENDC

print "**** creating test files ****"
os.system("mkdir -p /tmp/lmc-python-test/upload")
os.system("mkdir -p /tmp/lmc-python-test/download")
os.system("echo testing >/tmp/lmc-python-test/upload/test.txt")
os.system("echo testing >/tmp/lmc-python-test/upload/test2.txt")

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

print "**** upload object with no ttl ****"
lmc.swift.upload("lmc-python-test", "test2.txt", "/tmp/lmc-python-test/upload")
if 'x-delete-at' not in lmc.swift.get_object("lmc-python-test", "test2.txt").metadata:
    ok("object with no ttl created")
time.sleep(10)
lmc.swift.expire_object("lmc-python-test", "test2.txt", 60)
if 'x-delete-at' not in lmc.swift.get_object("lmc-python-test", "test2.txt").metadata:
    error("ttl not set after explicitly expiring object")
else:
    ok("ttl explicitly set")

print "**** creating large objects ****"
os.system("dd if=/dev/urandom of=/tmp/lmc-python-test/upload/test.10MB bs=1M count=10")
lmc.swift.upload("lmc-python-test", "test.10MB", "/tmp/lmc-python-test/upload", ttl=60, segment_size="4M")
lmc.swift.cache_fetch("lmc-python-test", "test.10MB", "/tmp/lmc-python-test/download")
os.system("diff -s /tmp/lmc-python-test/upload/test.10MB /tmp/lmc-python-test/download/test.10MB")

sys.stdout.write("waiting for ttl to expire objects")
start_time = time.time()
wait_time = 5 * 60
objects_alive = True
while time.time() - start_time < wait_time:
    objects_alive = len(lmc.swift.list_objects("lmc-python-test", ignore_partial=False)) > 0
    segments_alive = len(lmc.swift.list_objects("lmc-python-test_segments", ignore_partial=False)) > 0
    if objects_alive or segments_alive:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(10)
    else:
        break
print ""
waited = time.time() - start_time
if waited < wait_time:
    ok("all objects expired after %f seconds" % waited)
elif objects_alive or segments_alive:
    error("timed out and objects with ttl still there")
else:
    warn("objects expired after timing out")

print "**** deleting test files ****"
os.system("rm -fr /tmp/lmc-python-test")

# TODO:
# 1. test fetching the most recent object in a container
# 2. test fetching the object closest to a time in a container
# 3. test that cache fetch doesn't grab the file if it's present on the local system
# 4. test that ACLs work properly:
#		a. create users that can't create containers but can read/write to them
#		b. create users that can read from a container but can't write to it
