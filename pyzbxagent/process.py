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


from pyzbxagent.logger import get_logger
from time import time


########################################################################
class ItemProcessor(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, items, database):
        self._database = database
        self._item = None
        self._items = items
        self._logger = get_logger()
        self._process_date = None

    #----------------------------------------------------------------------
    def process(self):
        self._process_date = time()
        for self._item in self._items:
            self._try_to_process_item()

    #----------------------------------------------------------------------
    def _try_to_process_item(self):
        try:
            self._process_item()
        except Exception, e:
            self._logger.warn(u'An error occurred while processing item "%s": %s' % \
                (self._item.get_name(), e), exc_info=True)

    #----------------------------------------------------------------------
    def _process_item(self):
        if self._item_needs_update():
            #~ self._logger.debug(u'Processing item "%s"' % self._item.get_name())
            item_values = self._item.update()
            self._write_item_values_to_database(item_values)

    #----------------------------------------------------------------------
    def _item_needs_update(self):
        item_next_update_date = self._item.get_next_update_date()
        return self._process_date >= item_next_update_date

    #----------------------------------------------------------------------
    def _write_item_values_to_database(self, item_values):
        self._database.insert_values(self._process_date, item_values)
