"""
MPP Solar Inverter Command Library
library of utility and helpers for MPP Solar PIP-4048MS inverters
mpputils.py
"""

import logging
from .mppcommands import mppCommands
from .mppcommands import NoDeviceError

logger = logging.getLogger()


def getVal(_dict, key, ind=None):
    if key not in _dict:
        return ""
    if ind is None:
        return _dict[key]
    else:
        return _dict[key][ind]


class mppUtils:
    """
    MPP Solar Inverter Utility Library
    """

    def __init__(self, serial_device=None, baud_rate=2400):
        if (serial_device is None):
            raise NoDeviceError("A serial device must be supplied, e.g. /dev/ttyUSB0")
        self.mp = mppCommands(serial_device, baud_rate)
        self._serial_number = None

    def getKnownCommands(self):
        return self.mp.getKnownCommands()

    def getResponseDict(self, cmd):
        return self.mp.execute(cmd).response_dict

    def getResponse(self, cmd):
        return self.mp.execute(cmd).response

    def getSerialNumber(self):
        if self._serial_number is None:
            response = self.mp.execute("QID").response_dict
            self._serial_number = response["serial_number"][0]
        return self._serial_number

    def getFullStatus(self):
        """
        Helper function that returns all the status data
        """
        status = {}
        # serial_number = self.getSerialNumber()
        data = self.mp.execute("Q1").response_dict
        data.update(self.mp.execute("QPIGS").response_dict)  # TODO: check if this actually works...

        # Need to get 'Parallel' info, but dont know what the parallel number for the correct inverter is...
        # parallel_data = self.mp.getResponseDict("QPGS0")
        # This 'hack' only works for 2 inverters in parallel.
        # if parallel_data['serial_number'][0] != self.getSerialNumber():
        #    parallel_data = self.mp.getResponseDict("QPGS1")
        # status_data.update(parallel_data)

        items = ['SCC Flag', 'AllowSccOnFlag', 'ChargeAverageCurrent', 'SCC PWM temperature',
                 'Inverter temperature', 'Battery temperature', 'Transformer temperature',
                 'Fan lock status', 'Fan PWM speed', 'SCC charge power', 'Sync frequency',
                 'Inverter charge status', 'AC Input Voltage', 'AC Input Frequency',
                 'AC Output Voltage', 'AC Output Frequency', 'AC Output Apparent Power',
                 'AC Output Active Power', 'AC Output Load', 'BUS Voltage', 'Battery Voltage',
                 'Battery Charging Current', 'Battery Capacity', 'Inverter Heat Sink Temperature',
                 'PV Input Current for Battery', 'PV Input Voltage', 'Battery Voltage from SCC',
                 'Battery Discharge Current']

        for item in items:
            key = '{}'.format(item).lower().replace(" ", "_")
            status[key] = {"value": data[key][0], "unit": data[key][1]}
        # Still have 'Device Status' from QPIGS
        # Still have QPGSn
        return status

    def getSettings(self):
        """
        Query inverter for all current settings
        """
        # serial_number = self.getSerialNumber()
        default_settings = self.mp.execute("QDI").response_dict
        current_settings = self.mp.execute("QPIRI").response_dict
        flag_settings = self.mp.execute("QFLAG").response_dict
        # current_settings.update(flag_settings)  # Combine current and flag settings dicts

        settings = {}
        # {"Battery Bulk Charge Voltage": {"unit": "V", "default": 56.4, "value": 57.4}}

        items = ["Battery Type", "Output Mode", "Battery Bulk Charge Voltage", "Battery Float Charge Voltage",
                 "Battery Under Voltage", "Battery Redischarge Voltage", "Battery Recharge Voltage", "Input Voltage Range",
                 "Charger Source Priority", "Max AC Charging Current", "Max Charging Current", "Output Source Priority",
                 "AC Output Voltage", "AC Output Frequency", "PV OK Condition", "PV Power Balance",
                 "Buzzer", "Power Saving", "Overload Restart", "Over Temperature Restart", "LCD Backlight", "Primary Source Interrupt Alarm",
                 "Record Fault Code", "Overload Bypass", "LCD Reset to Default", "Machine Type", "AC Input Voltage", "AC Input Current",
                 "AC Output Current", "AC Output Apparent Power", "AC Output Active Power", "Battery Voltage", "Max Parallel Units"]

        for item in items:
            key = '{}'.format(item).lower().replace(" ", "_")
            settings[key] = {"value": getVal(current_settings, key, 0),
                             "unit": getVal(current_settings, key, 1),
                             "default": getVal(default_settings, key, 0)}
        for key in flag_settings:
            _key = '{}'.format(key).lower().replace(" ", "_")
            settings[_key]['value'] = getVal(flag_settings, key, 0)
        return settings
