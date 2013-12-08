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
Self-monitoring

Currently we monitor the file size of our database and the consumed memory
"""

from pyzbxagent import PYZBXAGENT_VERSION
from pyzbxagent.items.base import Item


########################################################################
class AgentVersion(Item):
    """"""

    #----------------------------------------------------------------------
    def _update(self):
        self._handle_key('agent.version', callback=self._get_agent_version)

    #----------------------------------------------------------------------
    def _get_agent_version(self):
        return PYZBXAGENT_VERSION
