""" Broadlink RM Pro+ Plugin for Indigo.
    First Release Date: Feb 5, 2018
    Author: David Newhall II
    License: GPLv2
"""

import json
import time
import indigo
from broadlink import broadlink

# Magic broadlink device ID for a RM Pro+
#RM_PRO_PLUS_DEV = "0x2712"
#RM_PRO_PLUS_DEV = "0x2737"

class Plugin(indigo.PluginBase):
    """ Indigo Plugin """

    def __init__(self, pid, name, version, prefs):
        """ Initialize Plugin. """
        indigo.PluginBase.__init__(self, pid, name, version, prefs)
        self.debug = True
        

    def _discover_device(self, values, type_id, did):
        """ Devices.xml Callback Method to discover a RM Pro device. """
        devices = broadlink.discover(timeout=9)
        values["address"] = "- discovery failed -"
        for device in devices:
            values["address"] = device.host[0] if device.auth() else "- dev err {} -".format(device.host)
            return values  # only grab the first one.
        return values

    def _get_saved_commands_list(self, filter, values, type_id, did):
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
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds = [i for i in saved_cmds if i[1] != values["savedCommandList"]]
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            values["savedCommandList"] = ""
            values["commands"] = props["commands"]
        return values

    def _learn_new_command(self, values, type_id, did):
        """ Devices.xml Callback Method to learn a new command. """
        # If an address was provided, use it, otherwise, get it from the props.
        addr = values.get("address", indigo.devices[did].pluginProps.get("address", "127.0.0.1"))
        model = values.get("model", indigo.devices[did].pluginProps.get("model", "0x2712"))
        # Magic.
        rm_pro_dev = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
        rm_pro_dev.auth()
        rm_pro_dev.enter_learning()
        values['rawCommand'] = "- learn failed -"
        timeout = 9
        data = None
        while data is None and timeout > 0:
            time.sleep(2)
            timeout -= 2
            data = rm_pro_dev.check_data()
        if data:
            values['rawCommand'] = ''.join(format(x, '02x') for x in bytearray(data))
        return values

    def _reset_command_counter(self, action, dev):
        """ Set the command count for a device back to zero. """
        dev.updateStateOnServer("commandCounter", 0)
        return

    def _save_new_command(self, values, type_id, did):
        """ Devices.xml Callback Method to add a new command. """
        if values["commandName"] and values["rawCommand"]:
            dev = indigo.devices[did]
            props = dev.pluginProps
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds.append((values["rawCommand"], values["commandName"]))
            props["commands"] = json.dumps(saved_cmds)
            values["commands"] = props["commands"]
            values["commandName"], values["rawCommand"] = "", ""
            dev.replacePluginPropsOnServer(props)
        return values

    def _send_command(self, action, dev):
        """ Actions.xml Callback: Send a Command. """
        cmd = action.props.get("rawCommand", "")
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", ""))
        cmd_name = cmd
        if cmd == "" or addr == "":
            return
        for raw_cmd, _name in json.loads(dev.pluginProps.get("commands", "[]")):
            if raw_cmd == cmd:
                cmd_name = _name
                break
        if not dev.pluginProps.get("hideCommandLog", False):
            indigo.server.log(u"RM Pro+, Sending Command to: {} ({}): {}".format(dev.name, addr, cmd_name))
        rm_pro_dev = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
        rm_pro_dev.auth()
        data = bytearray.fromhex(''.join(cmd))
        rm_pro_dev.send_data(data)
        dev.updateStateOnServer("commandCounter", dev.states.get("commandCounter", 0) + 1)
        if cmd_name == raw_cmd:
            dev.updateStateOnServer("lastRawCommand", raw_cmd)
        else:
            dev.updateStateOnServer("lastSavedCommand", cmd_name)
