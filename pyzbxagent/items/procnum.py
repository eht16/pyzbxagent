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
Retrieve system uptime
"""

from pyzbxagent.items.base import Item
from os import listdir
from os.path import isdir, join


########################################################################
class NumberOfProcesses(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        self._handle_key('proc.num[]', callback=self._get_proc_num)

    #----------------------------------------------------------------------
    def _get_proc_num(self):
        result = 0
        for name in listdir('/proc'):
            path = join('/proc', name)
            if isdir(path) and name.isdigit():
                result += 1
        return result
