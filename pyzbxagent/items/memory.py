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

MEMINFO_PATH = '/proc/meminfo'


########################################################################
class Memory(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        keys = ('memory[total]', 'memory[used]', 'system.swap.size[,total]', 'system.swap.size[,used]')
        if self._keys.intersection(keys):
            memory_total, memory_used, swap_total, swap_used = self._get_memory()
            self._handle_key('memory[total]', value=memory_total)
            self._handle_key('memory[used]', value=memory_used)
            self._handle_key('system.swap.size[,total]', value=swap_total)
            self._handle_key('system.swap.size[,used]', value=swap_used)

    #----------------------------------------------------------------------
    def _get_memory(self):
        memory_total = 0
        memory_free = 0
        memory_buffers = 0
        memory_cached = 0
        swap_total = 0
        swap_free = 0
        swap_used = 0

        meminfo_file = open(MEMINFO_PATH)
        for line in meminfo_file:
            if line.startswith('MemTotal'):
                memory_total = self._get_value_from_line(line)
            elif line.startswith('MemFree'):
                memory_free = self._get_value_from_line(line)
            elif line.startswith('Buffers'):
                memory_buffers = self._get_value_from_line(line)
            elif line.startswith('Cached'):
                memory_cached = self._get_value_from_line(line)
            elif line.startswith('SwapTotal'):
                swap_total = self._get_value_from_line(line)
            elif line.startswith('SwapFree'):
                swap_free = self._get_value_from_line(line)

        meminfo_file.close()

        memory_used = memory_total - memory_free - memory_buffers - memory_cached
        swap_used = swap_total - swap_free

        return memory_total, memory_used, swap_total, swap_used

    #----------------------------------------------------------------------
    def _get_value_from_line(self, line):
        value = line.split()[1]
        # conver into int
        value = int(value)
        # convert from kilobytes into bytes
        value = value * 1024
        return value
