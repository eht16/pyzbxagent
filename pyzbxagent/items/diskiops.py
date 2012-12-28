# -*- coding: utf-8 -*-
#
# Copyright 2012 Enrico Tröger <enrico(dot)troeger(at)uvena(dot)de>
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
Disk operations monitoring
"""

from pyzbxagent.items.base import Item
from os.path import exists
import re


DISKSTATS_PATH = '/sys/block/%s/stat'
DISKSPACE_REGEXP = re.compile(r'vfs.dev.(?P<mode>read|write)\[(?P<path>/.*),ops\]')


########################################################################
class DiskIOps(Item):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(DiskIOps, self).__init__(*args, **kwargs)
        self._devices = self._get_devices()
        self._last_values = dict()

    #----------------------------------------------------------------------
    def _get_devices(self):
        devices = dict()
        for key in self._keys:
            device, mode = self._get_parameters_from_key(key)
            if device in devices:
                devices[device].add(mode)
            else:
                devices[device] = set((mode,))

        return devices

    #----------------------------------------------------------------------
    def _get_parameters_from_key(self, key):
        match = DISKSPACE_REGEXP.match(key)
        if not match:
            raise RuntimeError(
            u'Invalid key "%s". Either the path is incorrect or an invalid mode was specified.' % \
            key)
        mode, path = match.groups()
        if not exists(path):
            raise RuntimeError(u'Invalid key "%s". The path "%s" does not exist.' % (key, path))

        return path, mode

    #----------------------------------------------------------------------
    def _update(self):
        for device in self._devices:
            self._update_device(device)

    #----------------------------------------------------------------------
    def _update_device(self, device):
        previous_values = bool(self._last_values.get(device, None))
        operations_read, operations_write = self._parse_diskstats(device)

        # build delta only if we have already previous values
        if previous_values:
            delta_read = operations_read - self._last_values[device][0]
            key = self._get_key_from_parameters(device, 'read')
            iops_read = self._calculate_ops_from_delta(delta_read)
            self._handle_key(key, value=iops_read)

            delta_write = operations_write - self._last_values[device][1]
            iops_write = self._calculate_ops_from_delta(delta_write)
            key = self._get_key_from_parameters(device, 'write')
            self._handle_key(key, value=iops_write)

        # remember those values for the next run to build a delta
        self._last_values[device] = (operations_read, operations_write)

    #----------------------------------------------------------------------
    def _parse_diskstats(self, device):
        device = device.replace('/dev/', '')
        diskstats_file = open(DISKSTATS_PATH % device)
        diskstats_raw = diskstats_file.read()
        diskstats_file.close()

        fields = diskstats_raw.split()
        return long(fields[0]), long(fields[4])

    #----------------------------------------------------------------------
    def _get_key_from_parameters(self, device, mode):
        return 'vfs.dev.%s[%s,ops]' % (mode, device)

    #----------------------------------------------------------------------
    def _calculate_ops_from_delta(self, delta):
        return delta / float(self._update_interval)
