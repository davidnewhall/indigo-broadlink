# Indigo Plugin: Broadlink Devices

This plugin allows you to control the Broadlink IR blaster products with [Indigo](https://www.indigodomo.com/).
Hit me up if you need help adding support for newer/different devices. I
currently only own a RM Pro+ because [oceanplexian](https://github.com/oceanplexian)
purchased it for me and asked me to make a plugin. Support for the RM3 Mini was added
by [Colorado Four Wheeler](https://github.com/colorado4wheeler).

## Devices

- [RM Pro+](https://www.amazon.com/Broadlink-RM33-RM-Pro-Automation/dp/B078W1JVYK)
- [RM3 Mini3](https://www.amazon.com/Broadlink-RM33-RM-Pro-Automation/dp/B078BCMZH6)

## Future

- [A1 Environment Sensors](http://www.ibroadlink.com/a1/)
- [SP2/3 Smart Plugs](http://www.ibroadlink.com/sp3/)

## Usage

1. [Download the latest release](https://github.com/davidnewhall/indigo-broadlink/archive/latest.zip) or clone this repo.
2. Double-click the included plugin file.
3. Install and Enable the Plugin.
4. Add a New Device, Select `Broadlink Devices`, then `RM Universal Remote`.
5. Choose a device type: `RM Pro+`, `RM3 Mini`
6. Click Discover. If it fails, enter the IP for the RM device manually.
7. Click Learn Command. Point your remote and press a button.
8. Give it a name and Click Add Command.
9. Save.
10. Use the Commands in Action Groups or Triggers, etc.

## Licenses

#### This Plugin

- [GPLv2](https://www.gnu.org/licenses/gpl-2.0.txt): See [LICENSE](LICENSE) File

#### Dependencies

- [broadlink library](https://github.com/mjg59/python-broadlink): [MIT](https://github.com/mjg59/python-broadlink/blob/master/LICENSE)
- [pyaes](https://github.com/ricmoo/pyaes/): [MIT](https://github.com/ricmoo/pyaes/blob/master/LICENSE.txt)
- [PyCRC](https://github.com/alexbutirskiy/PyCRC): [GPLv3](https://github.com/alexbutirskiy/PyCRC/blob/master/LICENSE)
