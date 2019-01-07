# Indigo Plugin: Broadlink Devices

![Broadlink Plugin Logo](https://github.com/davidnewhall/indigo-broadlink/raw/master/broadlink.png)

This plugin allows you to read sensors for a Broadlink A1, and control the Broadlink
IR blaster, SP Smart Plug and SC Smart Switch products with [Indigo](https://www.indigodomo.com/).
Hit me up if you need help adding support for newer/different devices. I
currently only own a RM Pro+ because [oceanplexian](https://github.com/oceanplexian)
purchased it for me and asked me to make a plugin. Support for the RM3 Mini was added
by [Colorado Four Wheeler](https://github.com/colorado4wheeler). Support for other
devices has been added slowly as they become available for testing.

## Tested Devices

- [RM Pro+ IR Blaster](https://www.amazon.com/Broadlink-RM33-RM-Pro-Automation/dp/B078W1JVYK)
- [RM3 Mini3 IR Blaster](https://www.amazon.com/Broadlink-RM33-RM-Pro-Automation/dp/B078BCMZH6)
- [SP3 Smart Plug](https://www.amazon.com/BroadLink-Required-Control-Occupies-Assistant/dp/B01FDGO948)
- [SC1 Smart Switch](https://www.amazon.com/Broadlink-Controlled-Intelligent-Housewhole-Appliances/dp/B071VT5594)
- [A1 Environment Sensor](https://www.amazon.com/Broadlink-Environment-Intelligent-Evironment-Freshener/dp/B00ZPF9RAE)

Other IR and SP devices may work. Let me know!

**This plugin does not expose any of the [RF capabilities](https://github.com/mjg59/python-broadlink/issues/87)
of the RM Pro devices.** *If you would like these features, help me figure it out.
I don't have any RF equipment.*

## Usage

1. [Download the latest release](https://github.com/davidnewhall/indigo-broadlink/archive/latest.zip) or clone this repo.
1. Double-click the included plugin file.
1. Install and Enable the Plugin.
1. Add a New Device, Select `Broadlink Devices`, then `RM Universal Remote` or `Smart Plug`.
1. Click `Discover`. If it fails, enter the `IP` and `Model` for the device manually.
    - Check Indigo server logs after discovery for discovery details.

#### RM Universal Remote

1. Click `Learn Command`. Point your remote and press a button.
1. Give it a name and Click `Add Command`. << *Important*
1. Click `Save`.
1. Use the Commands in Action Groups, Triggers or Schedules.

#### Smart Plugs & Smart Switches

These devices have no special states. Select an update interval in the plugin
configuration; this ensures local state changes are reported as expected.
Control these devices with On/Off commands as you would any other relay device.

#### A1 Environmental Sensor

All five sensors are exposed as custom device states on a single device. We'd break
them out into individual devices, but it would require a dedicated plugin due to
limitations in the device architecture for Indigo plugins. Once you add the device
you can see the device states in the bottom pane of Indigo. Just grab the slider
dot at the bottom and drag it up. You can create triggers against the device states
and add them to control pages.

## Licenses

#### This Plugin

- [GPLv2](https://www.gnu.org/licenses/gpl-2.0.txt): See [LICENSE](LICENSE) File

#### Dependencies

- [broadlink library](https://github.com/mjg59/python-broadlink): [MIT](https://github.com/mjg59/python-broadlink/blob/master/LICENSE)
- [pyaes](https://github.com/ricmoo/pyaes/): [MIT](https://github.com/ricmoo/pyaes/blob/master/LICENSE.txt)
- [PyCRC](https://github.com/alexbutirskiy/PyCRC): [GPLv3](https://github.com/alexbutirskiy/PyCRC/blob/master/LICENSE)
