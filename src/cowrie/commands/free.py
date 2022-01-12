# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
from __future__ import annotations

import getopt
from typing import Dict

from cowrie.shell.command import HoneyPotCommand


class Command_free(HoneyPotCommand):
    HELP = (
        "\n"
        "Usage:\n"
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
    )
    VERSION = "free from procps-ng 3.3.9\n"

    MEMINFO_KEYS = ("MemTotal", "MemFree", "Shmem", "Buffers", "Cached", "SwapTotal", "SwapFree")

    OUTPUT_FMT = (
        "             total       used       free     shared    buffers     cached\n"
        "Mem:    {MemTotal:>10} {MemUsed:>10} {MemFree:>10} {Shmem:>10} {Buffers:>10} {Cached:>10}\n"
        "-/+ buffers/cache  {Buffers:>10} {Cached:>10}\n"
        "Swap:   {SwapTotal:>10} {SwapUsed:>10} {SwapFree:>10}\n"
    )
    OUTPUT_TOTAL_FMT = (
        "Total:  {TotalTotal:>10} {TotalUsed:>10} {TotalFree:>10}\n"
    )
    MAGNITUDE = ("B", "M", "G", "T", "Z")

    def call(self) -> None:
        try:
            opts, args = getopt.getopt(
                self.args, "hbkmgVt", ["human", "bytes", "kilo", "mega", "giga", "tera", "help", "version", "total"])
        except getopt.GetoptError as e:
            self.errorWrite("free: invalid option -- {}\n".format(e.opt))
            self._help()
            return

        meminfo = self._read_meminfo()

        tmp = [oa[0] for oa in opts]
        if not tmp:
            self._magnitude_format(meminfo)
            return

        total = "--total" in tmp or "-t" in tmp
        if "--help" in tmp:
            self._help()
            return
        if "--version" in tmp or "-V" in tmp:
            self._version()
            return
        if "--human" in tmp or "-h" in tmp:
            self._human_format(meminfo, total=total)
            return

        for opt, arg in opts:
            if opt in ("-b", "--bytes"):
                self._magnitude_format(meminfo, fmt="bytes", total=total)
                break
            if opt in ("-m", "--mega"):
                self._magnitude_format(meminfo, fmt="mega", total=total)
                break
            if opt in ("-g", "--giga"):
                self._magnitude_format(meminfo, fmt="giga", total=total)
                break
            if opt in ("-k", "--kilo"):
                self._magnitude_format(meminfo, total=total)
                break
            if opt == "--tera":
                self._magnitude_format(meminfo, fmt="tera", total=total)
                break

    def _magnitude_format(self, meminfo: Dict[str, int], fmt: str = "kilo", total: bool = False) -> None:
        if fmt == "bytes":
            for key, value in meminfo.items():
                meminfo[key] = value * 1024
        # elif fmt == "kilo":
        #     for key, value in meminfo.items():
        #         meminfo[key] = value
        elif fmt == "mega":
            for key, value in meminfo.items():
                meminfo[key] = value // 1024
        elif fmt == "giga":
            for key, value in meminfo.items():
                meminfo[key] = (value // 1024) // 1024
        elif fmt == "tera":
            for key, value in meminfo.items():
                meminfo[key] = ((value // 1024) // 1024) // 1024
        self._print_output(meminfo, total)

    def _human_format(self, meminfo: Dict[str, int], total: bool = False) -> None:
        tmp: Dict[str, str] = {}
        for key in meminfo:
            index = 0
            value = float(meminfo[key])
            while value >= 1024 and index < len(Command_free.MAGNITUDE):
                value /= 1024
                index += 1
            tmp[key] = "{:g}{}".format(round(value, 1), Command_free.MAGNITUDE[index])
        self._print_output(tmp, total)

    def _read_meminfo(self) -> Dict[str, int]:
        r = {}
        data = self.fs.file_contents("/proc/meminfo")
        for line in data.decode().splitlines():
            key, value = line.split(":")
            if key in Command_free.MEMINFO_KEYS:
                r[key] = int(value[:value.rfind(" ")])
        r["MemUsed"] = r["MemTotal"] - r["MemFree"]
        r["SwapUsed"] = r["SwapTotal"] - r["SwapFree"]
        r["TotalTotal"] = r["MemTotal"] + r["SwapTotal"]
        r["TotalUsed"] = r["MemUsed"] + r["SwapUsed"]
        r["TotalFree"] = r["MemFree"] + r["SwapFree"]
        return r

    def _print_output(self, meminfo: Dict[str, str], total: bool = False) -> None:
        self.write(Command_free.OUTPUT_FMT.format(**meminfo))
        if total:
            self.write(Command_free.OUTPUT_TOTAL_FMT.format(**meminfo))

    def _help(self) -> None:
        self.write(Command_free.HELP)

    def _version(self) -> None:
        self.write(Command_free.VERSION)


commands = {
    "free": Command_free,
    "/usr/bin/free": Command_free,
}
