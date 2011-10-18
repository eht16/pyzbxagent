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
Disk space monitoring
"""

from pyzbxagent.items.base import Item
from os import statvfs
from os.path import exists
import re


diskspace_regexp = re.compile(r'vfs.fs.size\[(?P<path>/.*),(?P<mode>total|used)\]')


########################################################################
class DiskSpace(Item):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(DiskSpace, self).__init__(*args, **kwargs)
        self._filesystems = self._get_filesystems()

    #----------------------------------------------------------------------
    def _get_filesystems(self):
        filesystems = dict()
        for key in self._keys:
            filesystem, mode = self._get_parameters_from_key(key)
            if filesystem in filesystems:
                filesystems[filesystem].add(mode)
            else:
                filesystems[filesystem] = set((mode,))

        return filesystems

    #----------------------------------------------------------------------
    def _get_parameters_from_key(self, key):
        match = diskspace_regexp.match(key)
        if not match:
            raise RuntimeError(
            u'Invalid key "%s". Either the path is incorrect or an invalid mode was specified.' % \
            key)
        path, mode = match.groups()
        if not exists(path):
            raise RuntimeError(u'Invalid key "%s". The path "%s" does not exist.' % (key, path))

        return path, mode

    #----------------------------------------------------------------------
    def _update(self):
        for filesystem in self._filesystems:
            self._update_filesystem(filesystem)

    #----------------------------------------------------------------------
    def _update_filesystem(self, filesystem):
        stat = statvfs(filesystem)
        modes = self._filesystems[filesystem]
        if 'total' in modes:
            total = stat.f_blocks * stat.f_bsize
            key = self._get_key_from_parameters(filesystem, 'total')
            self._handle_key(key, value=total)
        if 'used' in modes:
            total = stat.f_blocks
            available = stat.f_bavail
            used = (total - available) * stat.f_bsize
            key = self._get_key_from_parameters(filesystem, 'used')
            self._handle_key(key, value=used)

    #----------------------------------------------------------------------
    def _get_key_from_parameters(self, filesystem, mode):
        return 'vfs.fs.size[%s,%s]' % (filesystem, mode)

