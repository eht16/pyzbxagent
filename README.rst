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
contains the currently supported items and a few graphs.

PyZbxAgent is meant to stay small and simple with a low memory and
CPU cycle footprint. So it also can be used on low-end devices
like a Nokia N900.This is why I wrote it :).




License
-------
PyZbxAgent is distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2 of the license.
A copy of this license can be found in the file COPYING included with
the source code of this program.



Ideas, questions, patches and bug reports
-----------------------------------------
If you add something, or fix a bug, find a cool feature missing or just want to say hello,
please tell me. I'm always happy about feedback.


--
2011 by Enrico Tröger
