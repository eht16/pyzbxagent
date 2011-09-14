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

    _name = None
    _keys = None

    #----------------------------------------------------------------------
    def __init__(self, config, section):
        self._config = config
        self._section = section
        self._update_interval = None
        self._next_process_date = time()
        self._assert_have_keys_attribute()
        self._fetch_update_interval(config, section)
        self._logger = get_logger()
        self._logger.debug('Setup item %s' % self.__class__.__name__)

    #----------------------------------------------------------------------
    def _assert_have_keys_attribute(self):
        if not self._keys:
            message = u'Subclasses of Item must set the _keys attribute with the item\'s keys'
            raise AttributeError(message)

    #----------------------------------------------------------------------
    def _fetch_update_interval(self, config, section):
        self._update_interval = config.getint(section, 'update_interval')

    #----------------------------------------------------------------------
    def get_key(self):
        return self._name

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
        try:
            result = self._update()
        except Exception, e:
            raise
        else:
            self._update_next_process_date()
            return result

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

