# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module ...
"""

from __future__ import division, absolute_import

import getopt

from cowrie.core.honeypot import HoneyPotCommand

commands = {}

FREE_BYTES="""             total       used       free     shared    buffers     cached
Mem:       8069256    7872920     196336          0     410340    5295748
-/+ buffers/cache:    2166832    5902424
Swap:      3764220     133080    3631140"""

FREE_MEGA="""             total       used       free     shared    buffers     cached
Mem:          29.5       25        3          0        0.8       5
-/+ buffers/cache:       2       5
Swap:         3        0.1       3"""

FREE_HUMAN="""             total       used       free     shared    buffers     cached
Mem:          7.7G       7.5G       189M         0B       400M       5.1G
-/+ buffers/cache:       2.1G       5.6G
Swap:         3.6G       129M       3.5G"""

class command_free(HoneyPotCommand):
    """
    free
    """
    def call(self):
        """
        """
        # Parse options or display no files
        try:
            opts, args = getopt.getopt(self.args, 'mh')
        except getopt.GetoptError as err:
            self.do_free()
            return

        # Parse options
        for o, a in opts:
            if o in ('-h'):
                self.do_free(fmt='human')
                return
            elif o in ('-m'):
                self.do_free(fmt='megabytes')
                return
        self.do_free()


    def do_free(self, fmt='bytes'):
        """
        print free statistics
        """
        if fmt=='bytes':
            self.write(FREE_BYTES+'\n')
        elif fmt=='megabytes':
            self.write(FREE_MEGA+'\n')
        elif fmt=='human':
            self.write(FREE_HUMAN+'\n')

commands['/usr/bin/free'] = command_free

