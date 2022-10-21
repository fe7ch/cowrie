import getopt

from cowrie.shell.command import HoneyPotCommand


class Command_nproc(HoneyPotCommand):
    HELP = ("Usage: nproc [OPTION]...\n"
            "Print the number of processing units available to the current process,\n"
            "which may be less than the number of online processors\n"
            "\n"
            "      --all      print the number of installed processors\n"
            "      --ignore=N  if possible, exclude N processing units\n"
            "      --help     display this help and exit\n"
            "      --version  output version information and exit\n"
            "\n"
            "GNU coreutils online help: <https://www.gnu.org/software/coreutils/>\n"
            "Full documentation <https://www.gnu.org/software/coreutils/nproc>\n"
            "or available locally via: info '(coreutils) nproc invocation'\n")

    VERSION = ("nproc (GNU coreutils) 8.32\n"
               "Copyright (C) 2020 Free Software Foundation, Inc.\n"
               "License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.\n"
               "This is free software: you are free to change and redistribute it.\n"
               "There is NO WARRANTY, to the extent permitted by law.\n"
               "\n"
               "Written by Giuseppe Scrivano.\n")

    def call(self) -> None:
        try:
            opts, args = getopt.getopt(self.args, "", ["all", "ignore=", "help", "version"])
        except getopt.GetoptError as e:
            if e.msg.endswith("requires argument"):
                self._print_error("nproc: nproc: option '--{}' requires an argument\n".format(e.opt))
            if e.msg.endswith("not recognized"):
                if e.msg.startswith("option --"):
                    self._print_error("nproc: unrecognized option '--{}'\n".format(e.opt))
                else:  # "option -"
                    self._print_error("nproc: invalid option -- '{}'\n".format(e.opt))
            return

        tmp = [oa[0] for oa in opts]
        if not tmp:
            self._print_cpu_count()
            return

        if "--help" in tmp:
            self._help()
            return
        if "--version" in tmp:
            self._version()
            return

        ignore_arg = ""
        for opt, arg in opts:
            if opt == "--ignore":
                ignore_arg = arg
                break

        if not ignore_arg:
            self._print_cpu_count()
            return

        if not ignore_arg.isdigit():
            self._print_error("nproc: {}: invalid number to ignore\n".format(ignore_arg))
            return

        self._print_cpu_count(int(ignore_arg))

    def _print_cpu_count(self, ignore: int = 0) -> None:
        n = 0
        data = self.fs.file_contents("/proc/cpuinfo")
        for line in data.decode().splitlines():
            if line.startswith("processor"):
                n += 1
        n = n - ignore if ignore < n else 1
        self.write("{}\n".format(n))

    def _print_error(self, msg: str) -> None:
        self.errorWrite(msg)
        self.errorWrite("Try 'nproc --help' for more information.\n")

    def _help(self) -> None:
        self.write(Command_nproc.HELP)

    def _version(self) -> None:
        self.write(Command_nproc.VERSION)


commands = {
    "nproc": Command_nproc,
    "/usr/bin/nproc": Command_nproc,
}
