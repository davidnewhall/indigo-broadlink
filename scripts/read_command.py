#!/usr/bin/env python
""" Read a command from an RM/RM2/RM3/RMmini. """

import time
import broadlink

DEVICE_IP = "192.168.1.235"
DEVICE_ID = "0x2712"


def main():
    """ Read a command from an RM/RM2/RM3/RMmini. """
    device = broadlink.gendevice(int(DEVICE_ID, 0), (DEVICE_IP, 80), "000000000000")
    print("reading command from {}".format(DEVICE_IP))
    device.auth()

    device.enter_learning()
    data = None
    print("Learning... (push a button)")
    timeout = 30

    while (data is None) and (timeout > 0):
        time.sleep(1)
        timeout -= 1
        data = device.check_data()

    if data:
        print("Captured command!")
        print("".join(format(x, "02x") for x in bytearray(data)))


main()
