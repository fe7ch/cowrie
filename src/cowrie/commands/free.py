# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
from __future__ import absolute_import, division

import getopt
from typing import Dict

from cowrie.shell.command import HoneyPotCommand


class FreeCmd(HoneyPotCommand):
    """/usr/bin/free"""
    VERSION = "free from procps-ng 3.3.9\n"

    HELP = ("\nUsage:\n"
            " free [options]\n"
            "\n"
            "Options:\n"
            " -b, --bytes         show output in bytes\n"
            " -k, --kilo          show output in kilobytes\n"
            " -m, --mega          show output in megabytes\n"
            " -g, --giga          show output in gigabytes\n"
            "     --tera          show output in terabytes\n"
            " -h, --human         show human-readable output\n"
            "     --si            use powers of 1000 not 1024\n"
            " -l, --lohi          show detailed low and high memory statistics\n"
            " -o, --old           use old format (without -/+buffers/cache line)\n"
            " -t, --total         show total for RAM + swap\n"
            " -s N, --seconds N   repeat printing every N seconds\n"
            " -c N, --count N     repeat printing N times, then exit\n"
            "\n"
            "     --help     display this help and exit\n"
            " -V, --version  output version information and exit\n"
            "\n"
            "For more details see free(1).\n"
            "You have new mail in /var/mail/root\n")

    MAGNITUDE = ("B", "M", "G", "T", "Z")

    MEMINFO_KEYS = ("MemTotal", "MemFree", "Shmem", "Buffers", "Cached", "SwapTotal", "SwapFree")

    OUTPUT_FMT = ("             total       used       free     shared    buffers     cached\n"
                  "Mem:    {MemTotal:>10} {MemUsed:>10} {MemFree:>10} {Shmem:>10} {Buffers:>10} {Cached:>10}\n"
                  "Swap:   {SwapTotal:>10} {SwapUsed:>10} {SwapFree:>10}\n")

    def call(self):
        try:
            opts, args = getopt.getopt(
                self.args, "hbkmgV", ["human", "bytes", "kilo", "mega", "giga", "tera", "help", "version"])
        except getopt.GetoptError as e:
            self.errorWrite("free: invalid option -- {}\n".format(e.opt))
            self._help()
            return

        meminfo = self._read_meminfo()

        tmp = [oa[0] for oa in opts]
        if not tmp:
            self._print_stats(meminfo)
            return

        if "--help" in tmp:
            self._help()
            return
        if "--version" in tmp or "-V" in tmp:
            self._version()
            return
        if "--human" in tmp or "-h" in tmp:
            self._print_stats_for_human(meminfo)
            return

        for opt, arg in opts:
            if opt in ("-b", "--bytes"):
                self._print_stats(meminfo, fmt="bytes")
                break
            if opt in ("-k", "--kilo"):
                self._print_stats(meminfo, fmt="kilo")
                break
            if opt in ("-m", "--mega"):
                self._print_stats(meminfo, fmt="mega")
                break
            if opt in ("-g", "--giga"):
                self._print_stats(meminfo, fmt="giga")
                break
            if opt == "--tera":
                self._print_stats(meminfo, fmt="tera")
                break

    def _print_stats(self, meminfo: Dict[str, float], fmt: str = "kilo") -> None:
        if fmt == "bytes":
            for key, value in meminfo.items():
                meminfo[key] = value * 1024
        # elif fmt == "kilo":  # by default
        elif fmt == "mega":
            for key, value in meminfo.items():
                meminfo[key] = value // 1024
        elif fmt == "giga":
            for key, value in meminfo.items():
                meminfo[key] = (value // 1024) // 1024
        elif fmt == "tera":
            for key, value in meminfo.items():
                meminfo[key] = ((value // 1024) // 1024) // 1024
        self.write(FreeCmd.OUTPUT_FMT.format(**meminfo))

    def _print_stats_for_human(self, meminfo: Dict[str, float]) -> None:
        tmp = {}
        for key, value in meminfo.items():
            index = 0
            while value >= 1024 and index < len(FreeCmd.MAGNITUDE):
                value /= 1024
                index += 1
            tmp[key] = "{:g}{}".format(round(value, 1), FreeCmd.MAGNITUDE[index])
        self.write(FreeCmd.OUTPUT_FMT.format(**tmp))

    def _read_meminfo(self) -> Dict[str, float]:
        r = {}
        data = self.fs.file_contents("/proc/meminfo")
        for line in data.decode().splitlines():
            key, value = line.split(":")
            if key in FreeCmd.MEMINFO_KEYS:
                r[key] = float(value[:value.rfind(" ")])
        r["MemUsed"] = r["MemTotal"] - r["MemFree"]
        r["SwapUsed"] = r["SwapTotal"] - r["SwapFree"]
        return r

    def _help(self) -> None:
        self.write(FreeCmd.HELP)

    def _version(self) -> None:
        self.write(FreeCmd.VERSION)


commands = {
    "free": FreeCmd,
    "/usr/bin/free": FreeCmd,
}
