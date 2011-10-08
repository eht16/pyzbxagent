# -*- coding: utf-8 -*-
#
# Copyright 2011 Enrico Tröger <enrico(dot)troeger(at)uvena(dot)de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
Retrieve battery charge level percentage for the N900 BME battery.
It seems without the power kernel or other non-standard patches,
the only way to retrieve the information is via DBus :(.
"""

from pyzbxagent.items.base import Item
import dbus


BME_PATH = '/org/freedesktop/Hal/devices/bme'
HAL_DEVICE_IFACE = 'org.freedesktop.Hal.Device'
HAL_IFACE = 'org.freedesktop.Hal'
PROPERTY_CHARGE_LEVEL_PERCENTAGE = 'battery.charge_level.percentage'
PROPERTY_RECHARGEABLE_CHARGING_STATUS = 'maemo.rechargeable.charging_status'
PROPERTY_VOLTAGE_CURRENT = 'battery.voltage.current'
PROPERTY_VOLTAGE_DESIGN = 'battery.voltage.design'


########################################################################
class MaemoBMEBattery(Item):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(MaemoBMEBattery, self).__init__(*args, **kwargs)
        self._get_property_method = None

    #----------------------------------------------------------------------
    def _init_dbus_if_necessary(self):
        if not self._get_property_method:
            # TODO not sure whether the connection to the system bus can be lost, if so,
            # we would need to establish in _update() or better detect the connection loss
            # and reconnect instantly
            system_bus = dbus.SystemBus()
            service = system_bus.get_object(HAL_IFACE, BME_PATH)
            self._get_property_method = service.get_dbus_method('GetProperty', HAL_DEVICE_IFACE)

    #----------------------------------------------------------------------
    def _update(self):
        self._init_dbus_if_necessary()
        # battery percentage
        self._handle_key('maemo.battery.percentage', callback=self._get_charge_level)
        # voltage
        self._handle_key('maemo.battery.voltage[current]', callback=self._get_voltage_current)
        self._handle_key('maemo.battery.voltage[design]', callback=self._get_voltage_design)

    #----------------------------------------------------------------------
    def _get_charge_level(self):
        charging_status = self._get_property_method(PROPERTY_RECHARGEABLE_CHARGING_STATUS)
        # while charging, 'battery.charge_level.percentage' is always 0, so use fix values
        if charging_status == 'full':
            charge_level_percentage = 100
        elif charging_status == 'on':
            charge_level_percentage = 10
        else:
            charge_level_percentage = self._get_property_method(PROPERTY_CHARGE_LEVEL_PERCENTAGE)

        return charge_level_percentage

    #----------------------------------------------------------------------
    def _get_voltage_current(self):
        voltage_current = self._get_property_method(PROPERTY_VOLTAGE_CURRENT)
        return voltage_current

    #----------------------------------------------------------------------
    def _get_voltage_design(self):
        voltage_design = self._get_property_method(PROPERTY_VOLTAGE_DESIGN)
        return voltage_design
