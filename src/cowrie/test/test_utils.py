from __future__ import annotations

import configparser
import os
import tempfile
import unittest
import hashlib
from io import StringIO

from cowrie.core import utils

from twisted.application.service import MultiService
from twisted.internet import protocol
from twisted.internet import reactor  # type: ignore


def get_config(config_string: str) -> configparser.ConfigParser:
    """Create ConfigParser from a config_string."""
    cfg = configparser.ConfigParser()
    cfg.read_file(StringIO(config_string))
    return cfg


class UtilsTestCase(unittest.TestCase):
    """Tests for cowrie/core/utils.py."""

    def test_durationHuman(self) -> None:
        minute = utils.durationHuman(60)
        self.assertEqual(minute, "01:00")

        hour = utils.durationHuman(3600)
        self.assertEqual(hour, "01:00:00")

        something = utils.durationHuman(364020)
        self.assertEqual(something, "4.0 days 05:07:00")

    def test_get_endpoints_from_section(self) -> None:
        cfg = get_config(
            "[ssh]\n"
            "listen_addr = 1.1.1.1\n"
        )
        self.assertEqual(["tcp:2223:interface=1.1.1.1"], utils.get_endpoints_from_section(cfg, "ssh", 2223))

        cfg = get_config(
            "[ssh]\n"
            "listen_addr = 1.1.1.1\n"
        )
        self.assertEqual(["tcp:2224:interface=1.1.1.1"], utils.get_endpoints_from_section(cfg, "ssh", 2224))

        cfg = get_config(
            "[ssh]\n"
            "listen_addr = 1.1.1.1 2.2.2.2\n"
        )
        self.assertEqual(
            ["tcp:2223:interface=1.1.1.1", "tcp:2223:interface=2.2.2.2"],
            utils.get_endpoints_from_section(cfg, "ssh", 2223)
        )

        cfg = get_config(
            "[ssh]\n"
            "listen_addr = 1.1.1.1 2.2.2.2\n"
            "listen_port = 23\n"
        )
        self.assertEqual(
            ["tcp:23:interface=1.1.1.1", "tcp:23:interface=2.2.2.2"], utils.get_endpoints_from_section(cfg, "ssh", 2223)
        )

        cfg = get_config(
            "[ssh]\n"
            "listen_endpoints = tcp:23:interface=1.1.1.1 tcp:2323:interface=1.1.1.1\n"
        )
        self.assertEqual(
            ["tcp:23:interface=1.1.1.1", "tcp:2323:interface=1.1.1.1"],
            utils.get_endpoints_from_section(cfg, "ssh", 2223)
        )

    def test_create_endpoint_services(self) -> None:
        parent = MultiService()
        utils.create_endpoint_services(reactor, parent, ["tcp:23:interface=1.1.1.1"], protocol.Factory())
        self.assertEqual(len(parent.services), 1)

        parent = MultiService()
        utils.create_endpoint_services(reactor, parent, ["tcp:23:interface=1.1.1.1"], protocol.Factory())
        self.assertEqual(len(parent.services), 1)

        parent = MultiService()
        utils.create_endpoint_services(
            reactor, parent, ["tcp:23:interface=1.1.1.1", "tcp:2323:interface=2.2.2.2"], protocol.Factory()
        )
        self.assertEqual(len(parent.services), 2)

    def test_sha256_of_path(self) -> None:
        content = b"Hello world"
        with tempfile.NamedTemporaryFile(prefix="test-", delete=False) as f:
            f.write(content)
        self.assertEqual(hashlib.sha256(content).hexdigest(), utils.sha256_of_file(f.name))
        os.unlink(f.name)

    def test_sha256_of_file_object(self) -> None:
        content = b"Hello world"
        with tempfile.NamedTemporaryFile(prefix="test-", delete=False) as f:
            f.write(content)
        with open(f.name, "rb") as f:
            self.assertEqual(hashlib.sha256(content).hexdigest(), utils.sha256_of_file_object(f))
        os.unlink(f.name)
