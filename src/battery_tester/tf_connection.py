#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_voltage_current_v2 import BrickletVoltageCurrentV2

import logging

# This class will use any Voltage Current Bricklet that is connected to
# the PC since the UID used for the connection is taken from the enumeration
# process.
#
# The program should stay stable if Bricks are connected/disconnected,
# if the Brick Daemon is restarted or if a Wi-Fi/RS485 connection is lost.
# It will also keep working if you exchange the Master or one of the
# Bricklets by a new one of the same type.
#
# If a Brick or Bricklet loses its state (e.g. callback configuration)
# while the connection was lost, it will automatically be reconfigured
# accordingly.
class TFIPConnection:
    HOST = "localhost"
    PORT = 4223

    @property
    def is_ready(self):
        return self.voltage_current_v2 is not None

    def __init__(self):
        self.voltage_current_v2 = None

        self.ipcon = IPConnection()

        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self._cb_connected)

        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self._cb_enumerate)

        # Connect to brickd, will trigger cb_connected
        self.ipcon.connect(TFIPConnection.HOST, TFIPConnection.PORT)

        # self.ipcon.enumerate()


    # Callback handles reconnection of IP Connection
    def _cb_connected(self, connected_reason):
        # Enumerate devices again. If we reconnected, the Bricks/Bricklets
        # may have been offline and the configuration may be lost.
        # In this case we don't care for the reason of the connection.
        self.ipcon.enumerate()

    # Callback handles device connections and configures possibly lost
    # configuration of bricklet callbacks, settings etc.
    # TODO: Bricklet spezifische Funktionen auslagern
    def _cb_enumerate(self, uid, connected_uid, position, hardware_version,
                     firmware_version, device_identifier, enumeration_type):

        if (enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED \
            or enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE):

            # Enumeration is for Voltage Current V2 Bricklet
            if device_identifier == BrickletVoltageCurrentV2.DEVICE_IDENTIFIER:

                self.voltage_current_v2 = BrickletVoltageCurrentV2(uid, self.ipcon)

                # self.voltage_current_v2.register_callback(
                #     self.voltage_current_v2.CALLBACK_CURRENT,
                #     self.cb_vcv2_current
                # )
                # self.voltage_current_v2.register_callback(
                #     self.voltage_current_v2.CALLBACK_VOLTAGE,
                #     self.cb_vcv2_voltage
                # )

                # self.voltage_current_v2.set_current_callback_configuration(1000, False, "x", 0, 0)
                # self.voltage_current_v2.set_voltage_callback_configuration(1000, False, "x", 0, 0)

    # BrickletVoltageCurrentV2.CALLBACK_CURRENT
    def _cb_vcv2_current(self, current_mA):
         #print(f"Current: {(current_mA / 1000):.2f} A")
         logging.debug(f"Current: {(current_mA / 1000):.2f} A")

    # BrickletVoltageCurrentV2.CALLBACK_VOLTAGE
    def _cb_vcv2_voltage(self, voltage_mV):
         #print(f"Voltage: {(voltage_mV / 1000):.2f} V")
         logging.debug(f"Voltage: {(voltage_mV / 1000):.2f} V")
