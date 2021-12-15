from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.honeypot import HoneyPotShell

commands = {}

class Command_etc_init_d(HoneyPotCommand, HoneyPotShell):


    def not_found(self):
        output = "bash: /etc/init.d/iptables: No such file or directory"
        self.write(output + "\n")

    def call(self):
        self.not_found()
        return



commands["/etc/init.d/iptables"] = Command_etc_init_d

