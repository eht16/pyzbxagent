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
Base class for items
"""


from pyzbxagent.logger import get_logger
from time import time


########################################################################
class Item(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, config, section):
        self._config = config
        self._section = section
        self._next_process_date = time()
        self._update_interval = None
        self._keys = None
        self._update_results = None
        self._fetch_item_keys()
        self._fetch_update_interval()
        self._logger = get_logger()
        self._logger.debug('Setup item %s' % self.__class__.__name__)

    #----------------------------------------------------------------------
    def _fetch_item_keys(self):
        item_keys = self._config.get(self._section, 'item_keys')
        if item_keys:
            keys = eval(item_keys)
            self._keys = set(keys)
        self._assert_have_keys_attribute()

    #----------------------------------------------------------------------
    def _assert_have_keys_attribute(self):
        if not self._keys:
            message = u'Item %s is enabled but no keys are defined.' % self.__class__.__name__
            raise RuntimeError(message)

    #----------------------------------------------------------------------
    def _fetch_update_interval(self):
        self._update_interval = self._config.getint(self._section, 'update_interval')

    #----------------------------------------------------------------------
    def get_name(self):
        return self.__class__.__name__

    #----------------------------------------------------------------------
    def get_update_interval(self):
        return self._update_interval

    #----------------------------------------------------------------------
    def get_next_update_date(self):
        return self._next_process_date

    #----------------------------------------------------------------------
    def update(self):
        self._reset_update_defaults()
        try:
            self._update()
        except Exception:
            self._reset_update_defaults()
            raise
        else:
            result = self._update_results
            self._reset_update_defaults()
            self._update_next_process_date()
            return result

    #----------------------------------------------------------------------
    def _reset_update_defaults(self):
        self._update_results = dict()

    #----------------------------------------------------------------------
    def _update_next_process_date(self):
        self._next_process_date = time() + self._update_interval

    #----------------------------------------------------------------------
    def _update(self):
        """
        To be overwritten by subclasses to implement item updating, i.e. read
        and/or calculate values.
        """
        raise NotImplementedError

    #----------------------------------------------------------------------
    def _read_file(self, path):
        file_ = None
        try:
            file_ = open(path)
            value = file_.read()
            return value
        finally:
            if file_:
                file_.close()

    #----------------------------------------------------------------------
    def _handle_key(self, key, callback=None, value=None):
        """
        Convenience method to handle optional keys.
        It checks whether key is one of the enabled keys for this item and if so,
        it either executes callback and adds its return value to self._update_results for the key
        or if callback is None, it adds value to self._update_results.
        """
        if not hasattr(callback, '__call__') and not value:
            raise ValueError(u'Either callback or value must be set')

        if key in self._keys:
            if callback:
                value = callback()
            self._update_results[key] = value
