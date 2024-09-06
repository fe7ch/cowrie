# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
from __future__ import annotations

import getopt
from typing import Any, Dict, Tuple

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

    MAGNITUDE = ("B", "M", "G", "T", "Z")

    def call(self) -> None:
        "             total       used       free     shared    buffers     cached\n"
        "Mem:    {MemTotal:>10} {MemUsed:>10} {MemFree:>10} {Shmem:>10} {Buffers:>10} {Cached:>10}\n"
        "-/+ buffers/cache  {Buffers:>10} {Cached:>10}\n"
        "Swap:   {SwapTotal:>10} {SwapUsed:>10} {SwapFree:>10}\n"
    )
    OUTPUT_TOTAL_FMT = (
        "Total:  {TotalTotal:>10} {TotalUsed:>10} {TotalFree:>10}\n"
    )

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self._help = False
        self._version = False
        self._total = False
        self._human = False
        self._fmt = "kilo"

    def call(self) -> None:
        try:
            opts, args = getopt.getopt(
                self.args, "hbkmgVt", ["human", "bytes", "kilo", "mega", "giga", "tera", "help", "version", "total"])
        except getopt.GetoptError as e:
            self.errorWrite("free: invalid option -- {}\n".format(e.opt))
            self._show_help()
            return

        n_fmts = 0

        for opt, _ in opts:
            if opt == "--help":
                self._show_help() if n_fmts <= 1 else self._show_incompatible_formats_error()
                return
            if opt in ("--version", "-V"):
                self._show_version() if n_fmts <= 1 else self._show_incompatible_formats_error()
                return

            if opt in ("--total", "-t"):
                self._total = True
            elif opt in ("--human", "-h"):
                self._human = True

            elif opt in ("--bytes", "-b"):
                self._fmt = "bytes"
                n_fmts += 1
            elif opt in ("--kilo", "-k"):
                n_fmts += 1
            elif opt in ("--mega", "-m"):
                self._fmt = "mega"
                n_fmts += 1
            elif opt in ("--giga", "-g"):
                self._fmt = "giga"
                n_fmts += 1
            elif opt in ("--tera", "-t"):
                self._fmt = "tera"
                n_fmts += 1

        if n_fmts <= 1:
            meminfo = self._read_meminfo()
            if self._human:
                self._human_format(meminfo)
            else:
                self._magnitude_format(meminfo)
        else:
            self._show_incompatible_formats_error()

    def _read_meminfo(self) -> Dict[str, int]:
        r: Dict[str, int] = {}
        data = self.fs.file_contents("/proc/meminfo")
        for line in data.decode().splitlines():
            key, value = line.split(":")
            if key in Command_free.MEMINFO_KEYS:
                r[key] = int(value[:value.rfind(" ")])
        r["MemUsed"] = r["MemTotal"] - r["MemFree"]
        r["SwapUsed"] = r["SwapTotal"] - r["SwapFree"]
        if self._total:
            r["TotalTotal"] = r["MemTotal"] + r["SwapTotal"]
            r["TotalUsed"] = r["MemUsed"] + r["SwapUsed"]
            r["TotalFree"] = r["MemFree"] + r["SwapFree"]
        return r

    def _human_format(self, meminfo: Dict[str, int]) -> None:
        tmp: Dict[str, str] = {}
        for key in meminfo:
            value = float(meminfo[key])
            i = 0
            while value >= 1024 and i < len(Command_free.MAGNITUDE):
                value /= 1024
                i += 1
            tmp[key] = "{:g}{}".format(round(value, 1), Command_free.MAGNITUDE[i])
        self._print_output(tmp)

    def _magnitude_format(self, meminfo: Dict[str, int]) -> None:
        tmp: Dict[str, str] = {}
        if self._fmt == "bytes":
            for key, value in meminfo.items():
                tmp[key] = str(value * 1024)
        elif self._fmt == "kilo":
            for key, value in meminfo.items():
                tmp[key] = str(value)
        elif self._fmt == "mega":
            for key, value in meminfo.items():
                tmp[key] = str(value // 1024)
        elif self._fmt == "giga":
            for key, value in meminfo.items():
                tmp[key] = str((value // 1024) // 1024)
        elif self._fmt == "tera":
            for key, value in meminfo.items():
                tmp[key] = str(((value // 1024) // 1024) // 1024)
        self._print_output(tmp)

    def _print_output(self, meminfo: Dict[str, str]) -> None:
        self.write(Command_free.OUTPUT_FMT.format(**meminfo))
        if self._total:
            self.write(Command_free.OUTPUT_TOTAL_FMT.format(**meminfo))

    def _show_help(self) -> None:
        self.write(Command_free.HELP)

    def _show_version(self) -> None:
        self.write(Command_free.VERSION)

    def _show_incompatible_formats_error(self) -> None:
        self.errorWrite("free: Multiple unit options doesn't make sense.\n")


commands = {
    "free": Command_free,
    "/usr/bin/free": Command_free,
}
