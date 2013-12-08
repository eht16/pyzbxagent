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
Send kernel version
"""

from pyzbxagent.items.base import Item

KERNEL_VERSION_PATH = '/proc/sys/kernel/osrelease'


########################################################################
class KernelVersion(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        self._handle_key('system.kernel.version', callback=self._get_kernel_version)

    #----------------------------------------------------------------------
    def _get_kernel_version(self):
        kernel_version_file = open(KERNEL_VERSION_PATH)
        kernel_version = kernel_version_file.read().strip()
        kernel_version_file.close()
        return kernel_version
