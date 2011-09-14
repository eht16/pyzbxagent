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
from os import getloadavg


########################################################################
class Load(Item):
    """"""

    _keys = [
        'system.cpu.load[,avg1]',
        'system.cpu.load[,avg5]',
        'system.cpu.load[,avg15]']

    #----------------------------------------------------------------------
    def _update(self):
        load1, load5, load15 = getloadavg()

        return {'system.cpu.load[,avg1]': load1,
                'system.cpu.load[,avg5]': load5,
                'system.cpu.load[,avg15]': load15}
