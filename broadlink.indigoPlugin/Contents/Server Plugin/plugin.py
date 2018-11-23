""" Broadlink RM Pro+ Plugin for Indigo.
    First Release Date: Feb 5, 2018
    Author: David Newhall II
    License: GPLv2
"""

import json
import time
import indigo
from broadlink import broadlink

# This dict constant is used to map IDs to a human name.
MODELS = {
    # Magic broadlink device IDs
    "0x2712": "RM Pro+",
    "0x2737": "RM Mini",
}


class Plugin(indigo.PluginBase):
    """ Indigo Plugin Class for Broadlink Devices """

    def __init__(self, pid, name, version, prefs):
        """ Initialize Plugin. """
        indigo.PluginBase.__init__(self, pid, name, version, prefs)
        self.debug = True

    @staticmethod
    def _discover_device(values, type_id, did):
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

    @staticmethod
    def _get_saved_commands_list(dev_filter, values, type_id, did):
        """ Devices.xml Callback Method to return saved commands for this device. """
        dev = indigo.devices[did]
        if "commands" not in dev.pluginProps:
            return [("none", "- none -")]
        return json.loads(dev.pluginProps["commands"])

    @staticmethod
    def _delete_saved_commands(values, type_id, did):
        """ Devices.xml Callback Method to delete saved commands. """
        if values["savedCommandList"]:
            dev = indigo.devices[did]
            props = dev.pluginProps
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds = [i for i in saved_cmds if i[1] != values["savedCommandList"]]
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            values["savedCommandList"] = ""
            values["commands"] = props["commands"]
        return values

    @staticmethod
    def _learn_new_command(values, type_id, did):
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
            time.sleep(2)
            timeout -= 2
            data = bl_device.check_data()
        if data:
            values['rawCommand'] = ''.join(format(x, '02x') for x in bytearray(data))
        return values

    @staticmethod
    def _reset_command_counter(action, dev):
        """ Set the command count for a device back to zero. """
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        dev.updateStateOnServer("commandCounter", 0)
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Reset Command Counter for {1} ({2})"
                              .format(MODELS[model], dev.name, addr))

    @staticmethod
    def _save_new_command(values, type_id, did):
        """ Devices.xml Callback Method to add a new command. """
        if values["commandName"] and values["rawCommand"]:
            dev = indigo.devices[did]
            model = dev.pluginProps.get("model", "broadlink")
            props = dev.pluginProps
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds.append((values["rawCommand"], values["commandName"]))
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            if dev.pluginProps.get("logChanges", True):
                indigo.server.log(u"{0}, Saved New Command for {1}: {3}"
                                  .format(MODELS[model], dev.name, values["commandName"]))
            values["commands"] = props["commands"]
            values["commandName"], values["rawCommand"] = "", ""
        return values

    @staticmethod
    def _send_command(action, dev):
        """ Actions.xml Callback: Send a Command. """
        cmd = action.props.get("rawCommand", "")
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        cmd_name, raw_cmd = cmd, ""
        if cmd == "" or addr == "":
            return
        # Try to match the raw command to a stored name.
        for raw_cmd, _name in json.loads(dev.pluginProps.get("commands", "[]")):
            if raw_cmd == cmd:
                cmd_name = _name
                break
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Sending Command to: {1} ({2}): {3}"
                              .format(MODELS[model], dev.name, addr, cmd_name))
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
        if cmd_name == raw_cmd:
            dev.updateStateOnServer("lastRawCommand", raw_cmd)
        else:
            dev.updateStateOnServer("lastSavedCommand", cmd_name)
