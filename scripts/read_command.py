#!/usr/bin/env python

import time
import broadlink

DEVICE_IP = "192.168.1.235"
RM_PRO_PLUS_DEV = "0x2712"


def main():
    """ Read a command. """
    rm_pro_dev = broadlink.gendevice(int(RM_PRO_PLUS_DEV, 0), (DEVICE_IP, 80), "000000000000")
    print "reading command from " + DEVICE_IP
    rm_pro_dev.auth()

    rm_pro_dev.enter_learning()
    data = None
    print "Learning..."
    timeout = 30

    while (data is None) and (timeout > 0):
        time.sleep(1)
        timeout -= 1
        data = rm_pro_dev.check_data()

    if data:
        print ''.join(format(x, '02x') for x in bytearray(data))


main()
