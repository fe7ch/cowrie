from __future__ import annotations
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_etc_init_d(HoneyPotCommand):
    def not_found(self):
        output = "bash: /etc/init.d/iptables: No such file or directory"
        self.write(output + "\n")

    def call(self):
        self.not_found()
        return


commands["/etc/init.d/iptables"] = Command_etc_init_d