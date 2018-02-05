# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import division, absolute_import

import time
import random

from cowrie.shell.honeypot import HoneyPotCommand
from cowrie.core import utils

commands = {}


class command_uptime(HoneyPotCommand):
    """
    """
    def call(self):
        """
        """

        upt = '%d days, %d mins' % (random.randrange(1, 30), random.randrange(1, 60))

        self.write('%s  up %s,  1 user,  load average: 0.0%d, 0.0%d, 0.0%d\n' %
                   (time.strftime('%H:%M:%S'), upt, random.randrange(0, 9), random.randrange(0, 9),
                    random.randrange(0, 9)))

commands['/usr/bin/uptime'] = command_uptime

