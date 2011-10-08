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
Retrieve the core temperature.
For now, we query two values, the temperature in degree centigrade and in some
weird raw value which probably is the value of a resistor, indicating the temperature.
Not yet sure which value is more reliable.
"""

from pyzbxagent.items.base import Item


TEMP_PATH = '/sys/devices/platform/omap34xx_temp/temp1_input'
TEMP_RAW_PATH = '/sys/devices/platform/omap34xx_temp/temp1_input_raw'


########################################################################
class MaemoTemperature(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        self._handle_key('maemo.temperature[temp]', callback=self._get_temperature)
        self._handle_key('maemo.temperature[raw]', callback=self._get_temperature_raw)

    #----------------------------------------------------------------------
    def _get_temperature(self):
        return self._read_file(TEMP_PATH)

    #----------------------------------------------------------------------
    def _get_temperature_raw(self):
        return self._read_file(TEMP_RAW_PATH)
