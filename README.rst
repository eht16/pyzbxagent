PyZbxAgent - A very simple Zabbix agent
=======================================


About
-----

PyZbxAgent is a simple tool which poorly tries to imitate a Zabbix agent.
Only a very small subset of items is supported and there is no support
for passive and active checks. All item values are sent to the
Zabbix server directly, so all item on the Zabbix server must be of the
type 'Zabbix Trapper'.

A sample template for Zabbix is included in the doc directory. This template
contains the currently supported items and a few graphs intended for a
Nokia N900 (or more generally a Maemo 5) device.

PyZbxAgent is meant to stay small and simple with a low memory and
CPU cycle footprint. So it also can be used on low-end devices
like a Nokia N900 or a Buffalo LinkStation. This is why I wrote it :).


Configuration
-------------

To configure PyZbxAgent, create a new file named pyzbxagent-local.conf
in the conf/ subdirectory. Do not modify the default pyzbxagent.conf.
Instead all custom configuration should go into the new pyzbxagent-local.conf.
All settings in this file override settings in the default configuration file.

You most probably want to edit the [zabbix] section to configure the Zabbix server
to which the data should be sent. Also you might want to review the various item
section and enable or disable some of them.


Item setup
^^^^^^^^^^

PyZbxAgent comes with a set of items to collect several system information.
The items are configured in the configuration file.

Each item has its own configuration section like the following one:

[item_modulename]
class=ClassName
update_interval=60
enable=true
item_keys=sample_item

The section name must always start with "item_". The following part is the module name
of the Python module containing the code for this item. This is actually the filename or
pathname of the item in the pyzbxagent/items/ subdirectory.

The class option specifies the class name of this item in the module.

The update_interval option specifies the interval in seconds in which the item
should update its data. Basically this means how often the item should get active
and performs its action.

The enable option is a simple boolean to define whether this item is enabled and should
be executed.

The item_keys option specified all item keys which should be processed. It is possible
that an item defines multiple keys but not all should be processed. If no keys
are listed for an item, it is automatically disabled (same effect as enable=false).
The sample configuration lists all possible keys per item. If you are unsure and
want to get a list of available keys, check the source code of the items modules.


Init Script
^^^^^^^^^^^

In the subdirectory conf/init.d there is a sample init script to automatically
startup the service at boot. Link this script into /etc/init.d and then
use insserv or the preferred tool of your distribution to properly install the
script into the system's init system (e.g. update-rc.d pyzbxagent defaults).



License
-------

PyZbxAgent is distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2 of the license.
A copy of this license can be found in the file COPYING included with
the source code of this program.



Ideas, questions, patches and bug reports
-----------------------------------------

If you add something, or fix a bug, find a cool feature missing or
just want to say hello, please tell me. I'm always happy about feedback.


--
2011 by Enrico Tröger
