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
Self-monitoring

Currently we monitor the file size of our database and the consumed memory
"""

from pyzbxagent.items.base import Item
from os.path import getsize
from os import getpid


########################################################################
class PyZbxAgent(Item):
    """"""

    _keys = ['vfs.file.size[pyzbxagent.db]', 'proc.mem[pyzbxagent]']

    #----------------------------------------------------------------------
    def _update(self):
        database_file_size = self._get_database_file_size()
        rss = self._get_memory_rss()

        return {
            'vfs.file.size[pyzbxagent.db]': database_file_size,
            'proc.mem[pyzbxagent]': rss}

    #----------------------------------------------------------------------
    def _get_database_file_size(self):
        path = self._config.get('database', 'name')
        return getsize(path)

    #----------------------------------------------------------------------
    def _get_memory_rss(self):
        proc_status = '/proc/%d/status' % getpid()
        try:
            file_h = open(proc_status)
            content = file_h.read()
            file_h.close()
        except IOError:
            return 0.0
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('VmRSS:'):
                values = line.split(':')
                vmrss = values[1].strip()
                try:
                    vmrss = vmrss.split()[0]
                    vmrss = vmrss.strip()
                    return float(vmrss) * 1024
                except IndexError:
                    return 0.0

        return 0.0
