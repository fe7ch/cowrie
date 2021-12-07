import getopt

from cowrie.shell.command import HoneyPotCommand


class PicoCmd(HoneyPotCommand):
    HELP = ("Usage: nano [OPTIONS] [[+LINE[,COLUMN]] FILE]...\n"
            "\n"
            "To place the cursor on a specific line of a file, put the line number with\n"
            "a '+' before the filename.  The column number can be added after a comma.\n"
            "When a filename is '-', nano reads data from standard input.\n"
            "\n"
            " Option         Long option             Meaning\n"
            " -A             --smarthome             Enable smart home key\n"
            " -B             --backup                Save backups of existing files\n"
            " -C <dir>       --backupdir=<dir>       Directory for saving unique backup files\n"
            " -D             --boldtext              Use bold instead of reverse video text\n"
            " -E             --tabstospaces          Convert typed tabs to spaces\n"
            " -F             --multibuffer           Read a file into a new buffer by default\n"
            " -G             --locking               Use (vim-style) lock files\n"
            " -H             --historylog            Log & read search/replace string history\n"
            " -I             --ignorercfiles         Don't look at nanorc files\n"
            " -J <number>    --guidestripe=<number>  Show a guiding bar at this column\n"
            " -K             --rawsequences          Fix numeric keypad key confusion problem\n"
            " -L             --nonewlines            Don't add an automatic newline\n"
            " -M             --trimblanks            Trim tail spaces when hard-wrapping\n"
            " -N             --noconvert             Don't convert files from DOS/Mac format\n"
            " -O             --bookstyle             Leading whitespace means new paragraph\n"
            " -P             --positionlog           Log & read location of cursor position\n"
            " -Q <regex>     --quotestr=<regex>      Regular expression to match quoting\n"
            " -R             --restricted            Restrict access to the filesystem\n"
            " -S             --softwrap              Display overlong lines on multiple rows\n"
            " -T <number>    --tabsize=<number>      Make a tab this number of columns wide\n"
            " -U             --quickblank            Wipe status bar upon next keystroke\n"
            " -V             --version               Print version information and exit\n"
            " -W             --wordbounds            Detect word boundaries more accurately\n"
            " -X <string>    --wordchars=<string>    Which other characters are word parts\n"
            " -Y <name>      --syntax=<name>         Syntax definition to use for coloring\n"
            " -Z             --zap                   Let Bsp and Del erase a marked region\n"
            " -a             --atblanks              When soft-wrapping, do it at whitespace\n"
            " -b             --breaklonglines        Automatically hard-wrap overlong lines\n"
            " -c             --constantshow          Constantly show cursor position\n"
            " -d             --rebinddelete          Fix Backspace/Delete confusion problem\n"
            " -e             --emptyline             Keep the line below the title bar empty\n"
            " -f <file>      --rcfile=<file>         Use only this file for configuring nano\n"
            " -g             --showcursor            Show cursor in file browser & help text\n"
            " -h             --help                  Show this help text and exit\n"
            " -i             --autoindent            Automatically indent new lines\n"
            " -j             --jumpyscrolling        Scroll per half-screen, not per line\n"
            " -k             --cutfromcursor         Cut from cursor to end of line\n"
            " -l             --linenumbers           Show line numbers in front of the text\n"
            " -m             --mouse                 Enable the use of the mouse\n"
            " -n             --noread                Do not read the file (only write it)\n"
            " -o <dir>       --operatingdir=<dir>    Set operating directory\n"
            " -p             --preserve              Preserve XON (^Q) and XOFF (^S) keys\n"
            " -q             --indicator             Show a position+portion indicator\n"
            " -r <number>    --fill=<number>         Set width for hard-wrap and justify\n"
            " -s <program>   --speller=<program>     Use this alternative spell checker\n"
            " -t             --saveonexit            Save changes on exit, don't prompt\n"
            " -u             --unix                  Save a file by default in Unix format\n"
            " -v             --view                  View mode (read-only)\n"
            " -w             --nowrap                Don't hard-wrap long lines [default]\n"
            " -x             --nohelp                Don't show the two help lines\n"
            " -y             --afterends             Make Ctrl+Right stop at word ends\n"
            " -z             --suspendable           Enable suspension\n"
            " -%             --stateflags            Show some states on the title bar\n")

    VERSION = (" GNU nano, version 2.9.3\n"
               " (C) 1999-2011, 2013-2018 Free Software Foundation, Inc.\n"
               " (C) 2014-2018 the contributors to nano\n"
               " Email: nano@nano-editor.org    Web: https://nano-editor.org/\n"
               " Compiled options: --disable-libmagic --disable-wrapping-as-root --enable-utf8\n")

    def call(self) -> None:
        try:
            opts, args = getopt.getopt(self.args, "hV", ["help", "version"])
        except getopt.GetoptError as e:
            self.errorWrite("pico: unrecognized option '--{}'\n".format(e.opt))
            self._help()
            return

        tmp = [oa[0] for oa in opts]
        if "--help" in tmp or "-h" in tmp:
            self._help()
            return
        if "--version" in tmp or "-V" in tmp:
            self._version()
            return

    def _help(self) -> None:
        self.write(PicoCmd.HELP)

    def _version(self) -> None:
        self.write(PicoCmd.VERSION)


commands = {
    "pico": PicoCmd,
    "/usr/bin/pico": PicoCmd,
}
