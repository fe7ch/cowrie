# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The names of the author(s) may not be used to endorse or promote
#    products derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from __future__ import annotations

import getopt
import os
import re

from twisted.python import log

from cowrie.core.artifact import Artifact
from cowrie.core.config import CowrieConfig
from cowrie.shell import fs
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_scp(HoneyPotCommand):
    """
    scp command
    """

    download_path = CowrieConfig.get("honeypot", "download_path")
    out_dir: str = ""

    def help(self):
        self.write("usage: scp [-12346BCpqrv] [-c cipher] [-F ssh_config] [-i identity_file]\n"
                   "           [-l limit] [-o ssh_option] [-P port] [-S program]\n"
                   "           [[user@]host1:]file1 ... [[user@]host2:]file2\n")

    def start(self):
        try:
            optlist, args = getopt.getopt(self.args, "12346BCpqrvfstdv:cFiloPS:")
        except getopt.GetoptError:
            self.help()
            self.exit()
            return

        self.out_dir = ""

        for opt in optlist:
            if opt[0] == "-d":
                self.out_dir = args[0]
                break

        if self.out_dir:
            outdir = self.fs.resolve_path(self.out_dir, self.protocol.cwd)

            if not self.fs.exists(outdir):
                self.errorWrite(f"-scp: {self.out_dir}: No such file or directory\n")
                self.exit()

        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")
        self.write("\x00")

    def lineReceived(self, line):
        log.msg(
            eventid="cowrie.session.file_download",
            realm="scp",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )
        self.protocol.terminal.write("\x00")

    def save_file(self, fake_path: str, data: bytes) -> None:
        with Artifact() as a:
            a.write(data)

        if a.path and os.path.exists(a.path):  # TODO: refactor this...
            log.msg(format="SCP Uploaded file \"%(filename)s\" to %(outfile)s",
                    eventid="cowrie.session.file_upload",
                    filename=os.path.basename(fake_path),
                    duplicate=a.duplicate,
                    url=fake_path,
                    outfile=a.path,
                    shasum=a.sha256,
                    destfile=fake_path)

            # Update the honeyfs to point to downloaded file.
            self.fs.update_realfile(self.fs.getfile(fake_path), a.path)
            self.fs.chown(fake_path, self.protocol.user.uid, self.protocol.user.gid)

    def parse_scp_data(self, data):
        # scp data format:
        # C0XXX filesize filename\nfile_data\x00
        # 0XXX - file permissions
        # filesize - size of file in bytes in decimal notation

        pos = data.find("\n")
        if pos != -1:
            header = data[:pos]

            pos += 1

            if re.match(r"^C0[\d]{3} [\d]+ [^\s]+$", header):

                r = re.search(r"C(0[\d]{3}) ([\d]+) ([^\s]+)", header)

                if r and r.group(1) and r.group(2) and r.group(3):

                    dend = pos + int(r.group(2))

                    if dend > len(data):
                        dend = len(data)

                    d = data[pos:dend]

                    if self.out_dir:
                        fname = os.path.join(self.out_dir, r.group(3))
                    else:
                        fname = r.group(3)

                    outfile = self.fs.resolve_path(fname, self.protocol.cwd)

                    try:
                        self.fs.mkfile(outfile, 0, 0, r.group(2), r.group(1))
                    except fs.FileNotFound:
                        # The outfile locates at a non-existing directory.
                        self.errorWrite(f"-scp: {outfile}: No such file or directory\n")
                        return ""

                    self.save_file(outfile, d)

                    data = data[dend + 1 :]  # cut saved data + \x00
            else:
                data = ""
        else:
            data = ""

        return data

    def handle_CTRL_D(self):
        if (
            self.protocol.terminal.stdinlogOpen
            and self.protocol.terminal.stdinlogFile
            and os.path.exists(self.protocol.terminal.stdinlogFile)
        ):
            with open(self.protocol.terminal.stdinlogFile, "rb") as f:
                data = f.read()
                header = data[: data.find(b"\n")]
                if re.match(r"C0[\d]{3} [\d]+ [^\s]+", header.decode()):
                    data = data[data.find(b"\n") + 1 :]
                else:
                    data = ""

            if data:
                with open(self.protocol.terminal.stdinlogFile, "wb") as f:
                    f.write(data)

        self.exit()


commands["/usr/bin/scp"] = Command_scp
commands["scp"] = Command_scp
