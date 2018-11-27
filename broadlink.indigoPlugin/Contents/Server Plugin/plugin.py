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
    "IR": {
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
    },
    "ES": {
        "0x2714": "A1 Environment Sensor",
    },
    "SP": {
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
}


class Plugin(indigo.PluginBase):
    """ Indigo Plugin Class for Broadlink Devices """

    def __init__(self, pid, name, version, prefs):
        """ Initialize Plugin. """
        indigo.PluginBase.__init__(self, pid, name, version, prefs)
        self.debug = True

    def _discover_device(self, values, type_id, did):
        """ Devices.xml Callback Method to discover a Broadlink device. """
        # When discovering, avoid reporting IPs belonging to established devices.
        exclude = [d.address for d in indigo.devices.itervalues("self")
                   if d.address != values["address"]]
        values["address"] = "- discovery failed -"
        indigo.server.log(u"Discovering Devices. This takes 10 seconds.")
        try:
            devices = broadlink.discover(timeout=int(indigo.activePlugin.pluginPrefs.get("timeout", 8)))
        except Exception as err:
            indigo.server.log(u"Error Discovering Devices! {0}".format(err), isError=True)
            return values
        values["address"] = "0 discovered, try again!"
        indigo.server.log((u"{0} Device(s) Discovered! If you did not receive the device " +
                           "you're looking for, enter the data manually.").format(len(devices)),
                          isError=(len(devices) > 1 or len(devices) == 0))

        return_values = None
        for device in devices:
            values["model"] = hex(device.devtype)
            values["address"] = "dev err {0}".format(device.host)
            model_name, model_cat = "UNKNOWN", "UNKNOWN"
            for cat in MODELS:
                if values["model"] in MODELS[cat]:
                    model_name = MODELS[cat][values["model"]]
                    model_cat = cat
                    break
            device.timeout = 3
            if device.auth():
                values["address"] = device.host[0]
            # If there's more than one discovered device, only one is populated
            # in the UI, but all of them are printed into the log file, in red.
            indigo.server.log(
                u"Discovered Device: {0}|{1} - type: {2}, IP: {3}, Auth: {4}".format(
                    model_cat, model_name, values["model"], device.host[0],
                    values["address"] == device.host[0]),
                isError=(len(devices) > 1))
            if values.get("category", model_cat) == model_cat and device.host[0] not in exclude:
                # If we find a device with a new IP in the same category, use it.
                return_values = (values["model"], values["address"])
        # return the special one, or the last one found
        if return_values is not None:
            (values["model"], values["address"]) = return_values
        return values

    def _get_saved_IR_commands_list(self, dev_filter, values, type_id, did):
        """ Devices.xml Callback Method to return saved commands for this device. """
        dev = indigo.devices[did]
        if "commands" not in dev.pluginProps:
            return [("none", "- none -")]
        return json.loads(dev.pluginProps["commands"])

    def _delete_saved_IR_commands(self, values, type_id, did):
        """ Devices.xml Callback Method to delete saved commands. """
        if values["savedCommandList"]:
            dev = indigo.devices[did]
            props = dev.pluginProps
            model = values.get("model", props.get("model", "0x2712"))
            cat = values.get("category", props.get("category", "IR"))
            saved_cmds = json.loads(props.get("commands", "[]"))
            if dev.pluginProps.get("logChanges", True):
                for i in values["savedCommandList"]:
                    indigo.server.log(u"{0}, Removed command from {1}: {2}"
                                      .format(MODELS[cat][model], dev.name, i))
            saved_cmds = [i for i in saved_cmds if i[0] not in values["savedCommandList"]]
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            values["savedCommandList"] = ""
            values["commands"] = props["commands"]
        return values

    def _learn_new_IR_command(self, values, type_id, did):
        """ Devices.xml Callback Method to learn a new command. """
        dev = indigo.devices[did]
        # If an address was provided, use it, otherwise, get it from the props.
        addr = values.get("address", dev.pluginProps.get("address", "127.0.0.1"))
        model = values.get("model", dev.pluginProps.get("model", "0x2712"))
        cat = values.get("category", dev.pluginProps.get("category", "IR"))
        values['rawCommand'] = "- learn failed -"
        try:
            # Magic.
            bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
            bl_device.auth()
            bl_device.enter_learning()
        except Exception as err:
            indigo.server.log(u"{0}, Error connecting to {1} ({2}): {3}"
                              .format(MODELS[cat][model], dev.name, addr, err), isError=True)
            return values
        timeout = int(indigo.activePlugin.pluginPrefs.get("timeout", 8))
        data = None
        while data is None and timeout > 0:
            time.sleep(1)
            timeout -= 1
            data = bl_device.check_data()
        if data:
            values['rawCommand'] = ''.join(format(x, '02x') for x in bytearray(data))
        return values

    def _reset_IR_command_counter(self, action, dev):
        """ Set the command count for a device back to zero. """
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        cat = dev.pluginProps.get("category", action.props.get("category", "IR"))
        dev.updateStateOnServer("commandCounter", 0)
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Reset Command Counter for {1} ({2})"
                              .format(MODELS[cat][model], dev.name, addr))

    def _save_new_IR_command(self, values, type_id, did):
        """ Devices.xml Callback Method to add a new command. """
        if values["commandName"] and values["rawCommand"]:
            dev = indigo.devices[did]
            model = dev.pluginProps.get("model", "0x2712")
            cat = dev.pluginProps.get("category", "IR")
            props = dev.pluginProps
            saved_cmds = json.loads(props.get("commands", "[]"))
            saved_cmds.append((values["rawCommand"], values["commandName"]))
            props["commands"] = json.dumps(saved_cmds)
            dev.replacePluginPropsOnServer(props)
            if dev.pluginProps.get("logChanges", True):
                indigo.server.log(u"{0}, Saved New Command for {1}: {2}"
                                  .format(MODELS[cat][model], dev.name, values["commandName"]))
            values["commands"] = props["commands"]
            values["commandName"], values["rawCommand"] = "", ""
        return values

    def _send_IR_command(self, action, dev):
        """ Actions.xml Callback: Send a Command. """
        cmd = action.props.get("rawCommand", "")
        addr = dev.pluginProps.get("address", action.props.get("address", ""))
        model = dev.pluginProps.get("model", action.props.get("model", "0x2712"))
        cat = dev.pluginProps.get("category", action.props.get("category", "IR"))

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
                              .format(MODELS[cat][model], dev.name, addr, err), isError=True)
            return

        dev.updateStateOnServer("commandCounter", dev.states.get("commandCounter", 0) + 1)
        if cmd_name == cmd:
            dev.updateStateOnServer("lastRawCommand", cmd)
        else:
            dev.updateStateOnServer("lastSavedCommand", cmd_name)
        if dev.pluginProps.get("logChanges", True):
            indigo.server.log(u"{0}, Sent {1} Command to: {2} ({3}): {4}"
                              .format(MODELS[cat][model], "Raw" if cmd_name == cmd else "Saved",
                                      dev.name, addr, cmd_name))

    def set_all_device_states(self):
        """ Updates Indigo with current devices' states. """
        addrs, devs = set(), set()
        # Build a list of IPs and devices to poll.
        for dev in indigo.devices.iter("self"):
            if dev.enabled and dev.configured and dev.deviceTypeId == "spDevice":
                addrs.add((dev.pluginProps["address"], dev.pluginProps.get("model", "0x2712"), dev.pluginProps.get("category", "IR")))
                devs.add(dev)
        for (addr, model, cat) in addrs:
            try:
                # Magic.
                bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
                bl_device.auth()
                state = bl_device.check_power()
            except Exception as err:
                for dev in devs:
                    # Update all the sub devices that failed to get queried.
                    if (dev.pluginProps["address"], dev.pluginProps["model"]) == (addr, model):
                        dev.setErrorStateOnServer(u"Comm Error: {} -> {}".format(addr, err))
                        if indigo.activePlugin.pluginPrefs.get("logUpdateErrors", True):
                            indigo.server.log(u"{0}, Error communicating with {1} ({2}): {3}"
                                              .format(MODELS[cat][model], dev.name, addr, err), isError=True)
            else:
                # Match this address back to the device(s) and update the state(s).
                for dev in devs:
                    if (dev.pluginProps["address"], dev.pluginProps["model"]) == (addr, model):
                        dev.updateStateOnServer("onOffState", state)
                        if dev.states["onOffState"] != state and dev.pluginProps.get("logChanges", True):
                            reply = "On" if state else "Off"
                            indigo.server.log(u"Device \"{}\" turned {}".format(dev.name, reply))

    def update_device_states(self, dev):
        """ Used to update a single device's state(s).
            Currently only captures on/off power state.
        """
        addr = dev.pluginProps.get("address", "")
        model = dev.pluginProps.get("model", "0x2712")
        cat = dev.pluginProps.get("category", "SP")
        try:
            # Magic.
            bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
            bl_device.auth()
            state = bl_device.check_power()
        except Exception as err:
            dev.setErrorStateOnServer(u"Comm Error: {}".format(err))
            indigo.server.log(u"{0}, Error connecting to {1} ({2}): {3}"
                              .format(MODELS[cat][model], dev.name, addr, err), isError=True)
        else:
            if dev.pluginProps.get("logActions", True):
                indigo.server.log(u"Updated \"{0}\" on:{1} -> on:{2}"
                                  .format(dev.name, dev.states["onOffState"], state))
            dev.updateStateOnServer("onOffState", state)

    def runConcurrentThread(self):
        """ Poll all configured devices (that support state changes).
            All devices are polled sequentially at the same interval.
            If you have a lot of devices, this might suck. Need to look into alternatives.
        """
        try:
            while True:
                self.set_all_device_states()
                self.sleep(int(indigo.activePlugin.pluginPrefs.get("interval", 30)))
        except self.StopThread:
            pass

    def actionControlDevice(self, action, dev):
        """ Callback Method to Control a SP Device. """
        if action.deviceAction in [indigo.kUniversalAction.RequestStatus,
                                   indigo.kUniversalAction.EnergyUpdate]:
            self.update_device_states(dev)
        addr = dev.pluginProps.get("address", "")
        model = dev.pluginProps.get("model", "0x2711")
        cat = dev.pluginProps.get("category", "SP")
        try:
            # Magic.
            bl_device = broadlink.gendevice(int(model, 0), (addr, 80), "000000000000")
            bl_device.auth()
        except Exception as err:
            indigo.server.log(u"{0}, Error connecting to {1} ({2}): {3}"
                              .format(MODELS[cat][model], dev.name, addr, err), isError=True)
            return
        control_device = False
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            power_state, reply, control_device = True, "On", True
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            power_state, reply, control_device = False, "Off", True
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            # Get current state from device before toggling.
            power_state = not bl_device.check_power()
            reply = "On" if power_state else "Off"
            control_device = True
        elif action.deviceAction == indigo.kDeviceAction.AllLightsOff:
            if dev.pluginProps.get("supportsAllLights", False):
                power_state, reply, control_device = False, "Off", True
        elif action.deviceAction == indigo.kDeviceAction.AllLightsOn:
            if dev.pluginProps.get("supportsAllLights", False):
                power_state, reply, control_device = True, "On", True
        elif action.deviceAction == indigo.kDeviceAction.AllOff:
            if dev.pluginProps.get("supportsAllOff", False):
                power_state, reply, control_device = False, "Off", True

        if control_device:
            bl_device.set_power(power_state)
            dev.updateStateOnServer("onOffState", power_state)
            if dev.pluginProps.get("logActions", True):
                indigo.server.log(u"Sent \"{0}\" {1}".format(dev.name, reply))
