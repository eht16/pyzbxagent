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
from pyzbxagent.process import ItemProcessor
from time import time


########################################################################
class ItemProcessingController(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, shutdown_event, items, database, sender):
        self._database = database
        self._items = items
        self._sender = sender
        self._shutdown_event = shutdown_event
        self._item = None
        self._process_date = None
        self._item_processor = None
        self._update_interval = None
        self._logger = get_logger()

    #----------------------------------------------------------------------
    def start(self):
        self._setup_update_interval()
        self._item_processor = ItemProcessor(self._items, self._database)
        self._process_until_shutdown()

    #----------------------------------------------------------------------
    def _setup_update_interval(self):
        minimum_update_interval = 3600
        for item in self._items:
            interval = item.get_update_interval()
            minimum_update_interval = min(minimum_update_interval, interval)

        self._update_interval = minimum_update_interval

    #----------------------------------------------------------------------
    def _process_until_shutdown(self):
        while not self._shutdown_event.isSet():
            self._store_process_date()
            # process items and collect new values
            self._item_processor.process()
            # send previously collected item values to the Zabbix server
            self._sender.send(process_date=self._process_date)
            self._sleep()

    #----------------------------------------------------------------------
    def _store_process_date(self):
        self._process_date = time()

    #----------------------------------------------------------------------
    def _sleep(self):
        next_processdate = self._process_date + self._update_interval
        sleep_seconds = next_processdate - time()
        self._logger.debug('Sleep for %s seconds' % (sleep_seconds))
        self._shutdown_event.wait(sleep_seconds)
