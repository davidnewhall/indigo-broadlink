#!/usr/bin/env python

import broadlink


DEVICE_IP = "192.168.1.235"
IR_COMMAND = "2600500000012695121411391114113912381238123911141139121312381214111410151114123812391139111411391238121411141114111411141139121312141139113911391200051e0001274b11000d050000000000000000"

RM_PRO_PLUS_DEV = "0x2712"


def main():
    """ Send a command. """
    rm_pro_dev = broadlink.gendevice(int(RM_PRO_PLUS_DEV, 0), (DEVICE_IP, 80), "000000000000")
    print "sending command to " + DEVICE_IP
    rm_pro_dev.auth()

    data = bytearray.fromhex(''.join(IR_COMMAND))
    rm_pro_dev.send_data(data)


main()
