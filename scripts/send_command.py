#!/usr/bin/env python
""" Send a command to an RM/RM2/RM3/RMmini. """

import broadlink

DEVICE_IP = "192.168.1.235"
DEVICE_ID = "0x2712"
IR_COMMAND = "2600500000012695121411391114113912381238123911141139121312381214111410151114123812391139111411391238121411141114111411141139121312141139113911391200051e0001274b11000d050000000000000000"


def main():
    """ Send a command. """
    device = broadlink.gendevice(int(DEVICE_ID, 0), (DEVICE_IP, 80), "000000000000")
    print("Sending command to {}".format(DEVICE_IP))
    device.auth()
    data = bytearray.fromhex(''.join(IR_COMMAND))
    device.send_data(data)


main()
