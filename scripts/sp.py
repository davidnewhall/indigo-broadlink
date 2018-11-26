#!/usr/bin/env python2.7
""" Check that things work on an SP2/SP3/SP3S/SPmini device. """

import time
import broadlink

DEVICE_IP = "192.168.1.201"  # This is important. Find it with discover.py.
DEVICE_ID = "0x2711"  # This probably makes no difference.
#            0x2711,                          # SP2
#            0x2719, 0x7919, 0x271a, 0x791a,  # Honeywell SP2
#            0x2720,                          # SPMini
#            0x753e,                          # SP3
#            0x7D00,                          # OEM branded SP3
#            0x947a, 0x9479,                  # SP3S
#            0x2728,                          # SPMini2
#            0x2733, 0x273e,                  # OEM branded SPMini
#            0x7530, 0x7918,                  # OEM branded SPMini2
#            0x2736                           # SPMiniPlus


def main():
    """ Read Device State. """
    device = broadlink.gendevice(int(DEVICE_ID, 0), (DEVICE_IP, 80), "000000000000")
    print("Checking State: {}".format(DEVICE_IP))
    # Not sure why this fails on python 3.7
    device.auth()

    state = device.check_power()
    print("Current State: {}".format(state))
    try:
        energy = device.get_energy()
        print("Energy State: {}".format(energy))
    except ValueError:
        # May not support energy metering.
        pass

    print("Turning device off.")
    device.set_power(False)
    print("Sleeping 5 seconds.")
    time.sleep(5)
    print("Turning device on.")
    device.set_power(True)


main()
