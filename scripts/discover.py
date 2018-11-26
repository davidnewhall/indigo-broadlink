#!/usr/bin/env python2.7
""" Broadlink Device Discovery Script """

import broadlink


def main():
    """ Discover things. """
    print("Discovering! please wait a moment...")
    devices = broadlink.discover(timeout=8)
    print("Found: {} devices".format(len(devices)))

    for device in devices:
        print("HEX Type: {} - IP Address: {}".format(hex(device.devtype), device.host[0]))
        if not device.auth():
            print("Error communicating with device: {}".format(device.host))


main()
