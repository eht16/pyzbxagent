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
Retrieve system load
"""


from pyzbxagent.items.base import Item
try:
    from os import getloadavg
except ImportError:
    # some systems don't provide getloadavg, try reading /proc/loadavg directly as fallback
    LOADAVG_PATH = '/proc/loadavg'
    def getloadavg():
        loadavg_file = open(LOADAVG_PATH)
        content = loadavg_file.read()
        loadavg = content.split()
        loadavg_file.close()
        return map(float, loadavg[:3])



########################################################################
class Load(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        keys = ('system.cpu.load[,avg1]', 'system.cpu.load[,avg5]', 'system.cpu.load[,avg15]')
        if self._keys.intersection(keys):
            load1, load5, load15 = getloadavg()
            self._handle_key('system.cpu.load[,avg1]', value=load1)
            self._handle_key('system.cpu.load[,avg5]', value=load5)
            self._handle_key('system.cpu.load[,avg15]', value=load15)
