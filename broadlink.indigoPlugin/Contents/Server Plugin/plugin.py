""" Broadlink RM Pro+ Plugin for Indigo.
    First Release Date: Feb 5, 2018 (v0.2.1)
    Author: David Newhall II
    Version: 1.0.0 (Nov 23, 2018)
    License: GPLv2
"""

import json
import time
import indigo
import broadlink

# This dict constant is used to map IDs to a human name.
MODELS = {
    # Magic broadlink device IDs (taken from broadlink/__init__.py).
    "0x2712": "RM Pro+",
    "0x2737": "RM Mini",
    "0x273d": "RM Pro Phicomm",
    "0x2783": "RM2 Home Plus",
    "0x277c": "RM2 Home Plus GDT",
    "0x272a": "RM2 Pro Plus",
    "0x2787": "RM2 Pro Plus2",
    "0x279d": "RM2 Pro Plus3",
    "0x27a9": "RM2 Pro Plus_300",
    "0x278b": "RM2 Pro Plus BL",
    "0x2797": "RM2 Pro Plus HYC",
    "0x27a1": "RM2 Pro Plus R1",
    "0x27a6": "RM2 Pro PP",
    "0x278f": "RM Mini Shate",
    "0x2714": "A1 Environment Sensor",
    "0x2711": "SP2",
    "0x2719": "Honeywell SP2",
    "0x7919": "Honeywell SP2",
    "0x271a": "Honeywell SP2",
    "0x791a": "Honeywell SP2",
    "0x2720": "SPMini",
    "0x753e": "SP3",
    "0x7D00": "OEM branded SP3",
    "0x947a": "SP3S",
    "0x9479": "SP3S",
    "0x2728": "SPMini2",
    "0x2733": "OEM branded SPMini",
    "0x273e": "OEM branded SPMini",
    "0x7530": "OEM branded SPMini2",
    "0x7918": "OEM branded SPMini2",
    "0x2736": "SPMiniPlus",
}

class Plugin(indigo.PluginBase):
    """ Indigo Plugin Class for Broadlink Devices """

    def __init__(self, pid, name, version, prefs):
        """ Initialize Plugin. """
        indigo.PluginBase.__init__(self, pid, name, version, prefs)
        self.debug = True

    def _discover_device(self, values, type_id, did):
        """ Devices.xml Callback Method to discover a Broadlink device. """
        values["address"] = "- discovery failed -"
        try:
            devices = broadlink.discover(timeout=9)
        except Exception as err:
            indigo.server.log(u"Error Discovering Devices! {1}".format(err), isError=True)
            return values
        dev = indigo.devices[did]
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"Discovering Devices.")
        for device in devices:
            values["address"] = "- dev err {} -".format(device.host)
            if device.auth():
                values["address"] = device.host[0]
            return values  # only grab the first one.
        return values

    def _get_saved_commands_list(self, dev_filter, values, type_id, did):
        """ Devices.xml Callback Method to return saved commands for this device. """
        dev = indigo.devices[did]
        if "commands" not in dev.pluginProps:
            return [("none", "- none -")]
        return json.loads(dev.pluginProps["commands"])

    def _delete_saved_commands(self, values, type_id, did):
        """ Devices.xml Callback Method to delete saved commands. """
        if values["savedCommandList"]:
            dev = indigo.devices[did]
            props = dev.pluginProps
            model = values.get("model", props.get("model", "0x2712"))
            saved_cmds = json.loads(props.get("commands", "[]"))
            if dev.pluginProps.get("logChanges", True):
                for i in values["savedCommandList"]:
                    indigo.server.log(u"{0}, Removed command from {1}: {2}"
                                      .format(MODELS[model], dev.name, i))
            saved_cmds = [i for i in saved_cmds if i[0] not in values["savedCommandList"]]
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            values["savedCommandList"] = ""
            values["commands"] = props["commands"]
        return values

    def _learn_new_command(self, values, type_id, did):
        """ Devices.xml Callback Method to learn a new command. """
        dev = indigo.devices[did]
        # If an address was provided, use it, otherwise, get it from the props.
        addr = values.get("address", dev.pluginProps.get("address", "127.0.0.1"))
        model = values.get("model", dev.pluginProps.get("model", "0x2712"))
        values['rawCommand'] = "- learn failed -"
        try:
            # Magic.
            bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
            bl_device.auth()
            bl_device.enter_learning()
        except Exception as err:
            indigo.server.log(u"{0}, Error connecting to {1} ({2}): {3}"
                              .format(MODELS[model], dev.name, addr, err), isError=True)
            return values
        timeout = 9
        data = None
        while data is None and timeout > 0:
            time.sleep(1)
            timeout -= 1
            data = bl_device.check_data()
        if data:
            values['rawCommand'] = ''.join(format(x, '02x') for x in bytearray(data))
        return values

    def _reset_command_counter(self, action, dev):
        """ Set the command count for a device back to zero. """
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        dev.updateStateOnServer("commandCounter", 0)
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Reset Command Counter for {1} ({2})"
                              .format(MODELS[model], dev.name, addr))

    def _save_new_command(self, values, type_id, did):
        """ Devices.xml Callback Method to add a new command. """
        if values["commandName"] and values["rawCommand"]:
            dev = indigo.devices[did]
            model = dev.pluginProps.get("model", "0x2712")
            props = dev.pluginProps
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds.append((values["rawCommand"], values["commandName"]))
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            if dev.pluginProps.get("logChanges", True):
                indigo.server.log(u"{0}, Saved New Command for {1}: {2}"
                                  .format(MODELS[model], dev.name, values["commandName"]))
            values["commands"] = props["commands"]
            values["commandName"], values["rawCommand"] = "", ""
        return values

    def _send_command(self, action, dev):
        """ Actions.xml Callback: Send a Command. """
        cmd = action.props.get("rawCommand", "")
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        cmd_name = cmd
        if cmd == "" or addr == "":
            return
        # Try to match the raw command to a stored name.
        for raw_cmd, _name in json.loads(dev.pluginProps.get("commands", "[]")):
            if raw_cmd == cmd:
                cmd_name = _name
                break
        try:
            bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
            bl_device.auth()
            data = bytearray.fromhex(''.join(cmd))
            bl_device.send_data(data)
        except Exception as err:
            indigo.server.log(u"{0}, Error connecting to {1} ({2}): {3}"
                              .format(MODELS[model], dev.name, addr, err), isError=True)
            return

        dev.updateStateOnServer("commandCounter", dev.states.get("commandCounter", 0) + 1)
        if cmd_name == cmd:
            dev.updateStateOnServer("lastRawCommand", cmd)
        else:
            dev.updateStateOnServer("lastSavedCommand", cmd_name)
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Sent {1} Command to: {2} ({3}): {4}"
                              .format(MODELS[model], "Raw" if cmd_name == cmd else "Saved",
                                      dev.name, addr, cmd_name))
