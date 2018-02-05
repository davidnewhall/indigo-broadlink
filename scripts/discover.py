#!/usr/bin/env python

import broadlink


print "discovering"
devices = broadlink.discover(timeout=9)
print devices
for device in devices:
    if device.auth():
        print device.host[0]
    else:
        print "Error authenticating with device : {}".format(device.host)
