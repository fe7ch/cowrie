# Copyright (c) 2025 Ivan Korolev
# See LICENSE for details.
from __future__ import annotations

import os
import unittest

from cowrie.shell.protocol import HoneyPotInteractiveProtocol
from cowrie.test.fake_server import FakeAvatar, FakeServer
from cowrie.test.fake_transport import FakeTransport

os.environ["COWRIE_HONEYPOT_DATA_PATH"] = "data"
os.environ["COWRIE_HONEYPOT_DOWNLOAD_PATH"] = "/tmp"
os.environ["COWRIE_SHELL_FILESYSTEM"] = "share/cowrie/fs.pickle"

PROMPT = b"root@unitTest:~# "


class ShellUnameCommandTests(unittest.TestCase):
    """Test for cowrie/commands/uname.py."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("tearDown From Unit Test")

    def test_uname_command_001(self) -> None:
        self.proto.lineReceived(b"uname\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux\n"
            + PROMPT,
        )

    def test_uname_command_002(self) -> None:
        self.proto.lineReceived(b"uname -m\n")
        self.assertEqual(
            self.tr.value(),
            b"x86_64\n"
            + PROMPT,
        )

    def test_uname_command_003(self) -> None:
        self.proto.lineReceived(b"uname -s -v -n -r -m\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux unitTest 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64\n"
            + PROMPT,
        )

    def test_uname_command_004(self) -> None:
        self.proto.lineReceived(b"uname -a\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux unitTest 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64 GNU/Linux\n"
            + PROMPT,
        )

    def test_uname_command_005(self) -> None:
        self.proto.lineReceived(b"uname -s -m\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux x86_64\n"
            + PROMPT,
        )

    def test_uname_command_006(self) -> None:
        self.proto.lineReceived(b"uname -s -v -n -r\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux unitTest 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1\n"
            + PROMPT,
        )

    def test_uname_command_007(self) -> None:
        self.proto.lineReceived(b"uname -mn\n")
        self.assertEqual(
            self.tr.value(),
            b"unitTest x86_64\n"
            + PROMPT,
        )

    def test_uname_command_008(self) -> None:
        self.proto.lineReceived(b"uname -s\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux\n"
            + PROMPT,
        )

    def test_uname_command_009(self) -> None:
        self.proto.lineReceived(b"uname -o -m -n\n")
        self.assertEqual(
            self.tr.value(),
            b"unitTest x86_64 GNU/Linux\n"
            + PROMPT,
        )

    def test_uname_command_010(self) -> None:
        self.proto.lineReceived(b"uname -svnrm\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux unitTest 3.2.0-4-amd64 #1 SMP Debian 3.2.68-1+deb7u1 x86_64\n"
            + PROMPT,
        )

    def test_uname_command_011(self) -> None:
        self.proto.lineReceived(b"uname -s && uname -m\n")
        self.assertEqual(
            self.tr.value(),
            b"Linux\nx86_64\n"
            + PROMPT,
        )