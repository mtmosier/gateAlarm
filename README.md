gateAlarm
=========

Use sensors to detect a gate left open and message your phone.  Also can be used with a doorbell.  Messsages can be sent via sms (Google Voice and Twilio supported) and/or push messages (Pushover).


History
=======

We often have problems with our gates being left open by accident.  When that happens our pitbull likes to go exploring the neighborhood.  To fix the problem I set up a raspberry pi with simple contact switches to detect a gate left open and message my phone to let me know.  Since we also lacked a doorbell, I went ahead and added support for that as well.

For google voice support I used the google voice lib found at https://github.com/korylprince/pygvoicelib.  I updated it for use with python 3 and included it in this library.  I should note that google voice appears to limit the messages I can send to a very small amount, so I added twilio support as a backup (used when google voice fails).  I also added support for pushover to do push messages and avoid sms altogether.  Each of these three is optional.  Omit the sections for the ones you do not want to use from the config file in order to disable them.


Prerequisites
=============

You must install WiringPi2 and WiringPi2-Python separately.  Please note I included patches for both.  Download the source for each, apply the patch (cd into the directory and do patch -p1 < /path/to/patch/wiringPi.patch, then normal build instructions) for each.  The patches are to allow callbacks with arguments.  I used wiringPi instead of RPi.GPIO because, last I checked, I could not drop root privileges with RPi.GPIO and still make use of it.  WiringPi allows dropping root privileges after setup.

Alternatively, you can pull each from my own forks of the projects, which already have the patches applied.  Please note that they may not be completely up to date with changes in the parent projects.

```
https://github.com/mtmosier/wiringPi
https://github.com/mtmosier/WiringPi2-Python
```


Hardware
========

The hardware setup is really nothing but pulldown resistors and contact switches (and optionally the doorbell).  Check the [schematic](schematic.png) if you want to see what I used.


Installation
============

Basic installation is simply:

```
cd gateAlarm
python3 setup.py install
```

That gets you the library installed.  Next you want to copy gateAlarm.conf.example to /etc/gateAlarm.conf and edit it with the settings appropriate for your installation.  In the system directory are the files I use to make it start at boot.  Copy system/gateAlarm to /etc/init.d/gateAlarm and system/startGateAlarm.py to /usr/local/sbin/startGateAlarm.py.  Make sure both are executable, then from a command line run

```
update-rc.d gateAlarm defaults
```


Copyright Information
=====================

All code contained is licensed as GPLv3.

The pygvoicelib code is Copyright 2010, TELTUB Inc, author Ehsan Foroughi.

The pygvoicelib.py was modified by Kory Prince (korylprince at gmail dot com) and Michael T. Mosier.  All other code is Copyright 2014, Michael T. Mosier (mtmosier at gmail dot com).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
