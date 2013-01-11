# -*- coding: utf-8 -*-
#
# Copyright 2013 Enrico Tröger <enrico(dot)troeger(at)uvena(dot)de>
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
Disk temperature monitoring using smartctl
"""

from os.path import exists
from pyzbxagent.items.base import Item
from subprocess import Popen, PIPE
import re


DISKTEMP_REGEXP = re.compile(r'hdd.temp\[(?P<path>[a-zA-Z0-9/]*)(,?(?P<device_type>.*))\]')
SMARTCTL_TEMPERATURE_ID = '194'


########################################################################
class DiskTemperature(Item):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(DiskTemperature, self).__init__(*args, **kwargs)
        self._devices = self._get_devices()

    #----------------------------------------------------------------------
    def _get_devices(self):
        devices = dict()
        for key in self._keys:
            device, device_type = self._get_parameters_from_key(key)
            devices[device] = device_type

        return devices

    #----------------------------------------------------------------------
    def _get_parameters_from_key(self, key):
        match = DISKTEMP_REGEXP.match(key)
        if not match:
            raise RuntimeError(
            u'Invalid key "%s". Either the path is incorrect or an invalid mode was specified.' % \
            key)
        path = match.groupdict()['path']
        device_type = match.groupdict().get('device_type', None)
        if not exists(path):
            raise RuntimeError(u'Invalid key "%s". The path "%s" does not exist.' % (key, path))

        return path, device_type

    #----------------------------------------------------------------------
    def _update(self):
        for device in self._devices:
            self._update_device(device)

    #----------------------------------------------------------------------
    def _update_device(self, device):
        device_type = self._devices[device]
        cmdline = ['smartctl', '-A', device]
        if device_type:
            cmdline.append('-d')
            cmdline.append(device_type)

        output = self._execute_smartctl(cmdline)
        value = self._parse_output(output)
        key = self._get_key_from_parameters(device)
        self._handle_key(key, value=value)

    #----------------------------------------------------------------------
    def _execute_smartctl(self, cmdline):
        process = Popen(cmdline, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode:
            raise RuntimeError(u'"%s" exited with code %s\nStdout:\n%s\nStderr:\n%s' % (
                u' '.join(cmdline), process.returncode, stdout, stderr))
        return stdout

    #----------------------------------------------------------------------
    def _parse_output(self, output):
        for line in output.splitlines():
            if line.startswith(SMARTCTL_TEMPERATURE_ID):
                parts = line.split()
                return int(parts[-1])

    #----------------------------------------------------------------------
    def _get_key_from_parameters(self, device):
        device_type = self._devices[device]
        if device_type:
            return 'hdd.temp[%s,%s]' % (device, device_type)
        else:
            return 'hdd.temp[%s]' % (device,)
