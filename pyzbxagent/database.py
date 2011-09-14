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
from sqlite3 import connect


DB_INIT_STATEMENT = '''
    CREATE TABLE IF NOT EXISTS `item_values`
    (
        `id` INTEGER PRIMARY KEY,
        `key` TEXT,
        `value` TEXT,
        `entry_date` INTEGER
    );
'''


########################################################################
class Database(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, database):
        self._conn = None
        self._database = database
        self._logger = get_logger()

    #----------------------------------------------------------------------
    def open(self):
        self._conn = connect(self._database, isolation_level=None)
        cursor = self._conn.cursor()
        cursor.executescript(DB_INIT_STATEMENT)

    #----------------------------------------------------------------------
    def close(self):
        try:
            self._conn.close()
        except Exception, e:
            self._logger.warn(u'An error occurred while closing the database: %s' % e, exc_info=True)

    #----------------------------------------------------------------------
    def insert_values(self, timestamp, values):
        items = list()
        for key, value in values.items():
            item = (key, value, timestamp)
            items.append(item)

        cursor = self._conn.cursor()
        cursor.executemany(
            'INSERT INTO `item_values` (`key`, `value`, `entry_date`) VALUES (?, ?, ?)', items)

    #----------------------------------------------------------------------
    def query_pending_items(self):
        cursor = self._conn.cursor()
        cursor.execute('SELECT `id`, `key`, `value`, `entry_date` FROM `item_values`;')
        result = cursor.fetchall()
        items = list()
        for id_, key, value, entry_date in result:
            #~ value = self._adapt_item_value_type(value)
            item = dict(id=id_, key=key, value=value, entry_date=entry_date)
            items.append(item)
        return items

    #----------------------------------------------------------------------
    def _adapt_item_value_type(self, value):
        try:
            # try int
            new_value = int(value)
        except ValueError:
            try:
                # try float
                new_value = float(value)
            except ValueError:
                # keep it as string
                new_value = value

        return new_value

    #----------------------------------------------------------------------
    def delete_items(self, items):
        item_ids = ','.join(map(lambda x: str(x['id']), items))
        cursor = self._conn.cursor()
        cursor.execute('DELETE FROM `item_values` WHERE `id` IN (%s);' % item_ids)
