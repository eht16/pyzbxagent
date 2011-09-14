#!/usr/bin/env python
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
A very simple Zabbix Agent implementation.

Strictly this is not a real Agent but just a daemon to
periodically send data to a Zabbix server (similar to zabbix_sender).
It is intended to be used on Maemo to enable basic monitoring,
in particular performance monitoring.
"""


from ConfigParser import SafeConfigParser
from optparse import OptionParser
from pyzbxagent.controller import ItemProcessingController
from pyzbxagent.database import Database
from pyzbxagent.sender import Sender
from signal import signal, SIGINT, SIGTERM
from thirdparty import daemon
from threading import Event
import errno
import logging
import logging.config
import os
import pwd


########################################################################
class PyZabbixAgentApp(object):
    """Base setups necessary for the service to run"""

    #----------------------------------------------------------------------
    def __init__(self):
        self._base_dir = None
        self._config_files = None
        self._database = None
        self._items = None
        self._logger = None
        self._options = None
        self._pid_file_path = None
        self._sender = None
        self._shutdown_event = Event()
        self._config = SafeConfigParser()

    #----------------------------------------------------------------------
    def setup(self):
        self._setup_basedir()
        self._setup_options()
        self._setup_config()
        self._set_uid()
        self._setup_pidfile_path()
        self._daemonize()
        self._check_already_running()
        self._write_pidfile()
        self._setup_logging()
        self._setup_signal_handler()
        self._setup_database()
        self._setup_sender()
        self._setup_items()

    #----------------------------------------------------------------------
    def _setup_basedir(self):
        self._base_dir = os.path.abspath(os.path.dirname(__file__))
        os.chdir(self._base_dir)

    #----------------------------------------------------------------------
    def _setup_options(self):
        """
        Set up options and defaults

        @param parser (optparse.OptionParser())
        """
        option_parser = OptionParser()
        option_parser.add_option(
            '-c', dest='config',
            default='%s/conf/pyzbxagent.conf' % self._base_dir,
            help=u'configuration file')

        option_parser.add_option(
            '-d', action='store_false',
            dest='daemonize',
            default=False,
            help=u'daemonize')

        self._options = option_parser.parse_args()[0]

    #----------------------------------------------------------------------
    def _setup_config(self):
        if not os.path.exists(self._options.config):
            raise RuntimeError(u'Configuration file does not exist')
        # build filename for local config to override default values
        config_path, config_filename = os.path.split(self._options.config)
        local_config_filename = u'%s-local%s' % os.path.splitext(config_filename)
        local_config_path = os.path.join(config_path, local_config_filename)
        # read config files
        self._config_files = [self._options.config, local_config_path]
        self._config.read(self._config_files)

    #----------------------------------------------------------------------
    def _set_uid(self):
        if self._config.has_option('main', 'user'):
            name = self._config.get('main', 'user')
            if name:
                uid = pwd.getpwnam(name)[2]
                os.setuid(uid)

    #----------------------------------------------------------------------
    def _setup_logging(self):
        logging.config.fileConfig(self._config_files)
        self._logger = logging.getLogger('pyzbxagent')
        self._logger.info('Application starts up')

    #----------------------------------------------------------------------
    def _daemonize(self):
        if self._options.daemonize:
            # here we fork
            daemon.WORKDIR = self._base_dir
            daemon.createDaemon()

    #----------------------------------------------------------------------
    def _setup_pidfile_path(self):
        self._pid_file_path = self._config.get('main', 'pid_file_path')

    #----------------------------------------------------------------------
    def _check_already_running(self):
        if self._is_service_running():
            raise RuntimeError(u'Already running')

    #----------------------------------------------------------------------
    def _is_service_running(self):
        """
        Check whether the service is already running
        """
        if os.path.exists(self._pid_file_path):
            pid_file = open(self._pid_file_path, 'r')
            pid = pid_file.read().strip()
            pid_file.close()
            if pid:
                try:
                    pid = int(pid)
                except ValueError:
                    return False
                # sending signal 0 fails if the process doesn't exist (anymore)
                # and won't do anything if the process is running
                try:
                    os.kill(pid, 0)
                except OSError, e:
                    if e.errno == errno.ESRCH:
                        return False
            return True
        return False

    #----------------------------------------------------------------------
    def _write_pidfile(self):
        pid = os.getpid()
        pid_file = open(self._pid_file_path, 'w')
        pid_file.write(str(pid))
        pid_file.close()

    #----------------------------------------------------------------------
    def _setup_signal_handler(self):
        signal(SIGINT,  self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    #----------------------------------------------------------------------
    def _signal_handler(self, signum, frame):
        self._logger.info(u'Received signal %s' % signum)
        if signum in (SIGINT, SIGTERM):
            self.shutdown()
        else:
            raise RuntimeError(u'Unhandled signal received')

    #----------------------------------------------------------------------
    def shutdown(self):
        self._logger.info(u'Initiating shutdown')
        self._shutdown_event.set()

    #----------------------------------------------------------------------
    def _setup_database(self):
        database_name = self._config.get('database', 'name')
        self._database = Database(database_name)
        self._database.open()

    #----------------------------------------------------------------------
    def _setup_sender(self):
        server = self._config.get('zabbix', 'server')
        port = self._config.getint('zabbix', 'port')
        socket_timeout = self._config.getint('zabbix', 'socket_timeout')
        send_interval = self._config.getint('zabbix', 'send_interval')
        simulate = self._config.getboolean('zabbix', 'simulate')
        self._sender = Sender(server, port, socket_timeout, send_interval, simulate, self._database)

    #----------------------------------------------------------------------
    def _setup_items(self):
        self._items = list()
        sections = self._config.sections()
        for section in sections:
            if section.startswith('item_'):
                self._setup_item(section)

    #----------------------------------------------------------------------
    def _setup_item(self, section):
        enable = self._config.getboolean(section, 'enable')
        class_name = self._config.get(section, 'class')
        if enable:
            item_name = section[5:]
            item = self._factor_item(item_name, class_name, section)
            self._items.append(item)

    #----------------------------------------------------------------------
    def _factor_item(self, item_name, class_name, section):
        module_name = 'pyzbxagent.items.%s' % item_name
        module = __import__(module_name, globals(), locals(), ['items'], 0)
        item_class = getattr(module, class_name)
        return item_class(self._config, section)

    #----------------------------------------------------------------------
    def start(self):
        try:
            self._try_to_start()
        except Exception, e:
            self._logger.error(u'An error occurred: %s' % e, exc_info=True)
            # try to shutdown ourselves as clean as possible and just see how far it goes
            try:
                self.shutdown()
            except:
                pass
            return 1
        else:
            return 0

    #----------------------------------------------------------------------
    def _try_to_start(self):
        item_processing_controller = ItemProcessingController(
            self._shutdown_event, self._items, self._database, self._sender)

        item_processing_controller.start()

        # bye bye
        self._teardown()

    #----------------------------------------------------------------------
    def _teardown(self):
        self._shutdown_sender()
        self._shutdown_database()
        self._shutdown_logging()

    #----------------------------------------------------------------------
    def _shutdown_database(self):
        self._database.close()

    #----------------------------------------------------------------------
    def _shutdown_sender(self):
        # try to send pending data finally
        self._sender.send(process_date=None, force=True)

    #----------------------------------------------------------------------
    def _shutdown_logging(self):
        self._logger.info(u'Shutdown')
        logging.shutdown()


#----------------------------------------------------------------------
def main():
    app = PyZabbixAgentApp()
    app.setup()

    exit_code = app.start()

    exit(exit_code)


if __name__ == "__main__":
    main()
