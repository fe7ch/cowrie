# Copyright (c) 2016 Michel Oosterhof <michel@oosterhof.net>
"""This module contains code to handling saving of honeypot artifacts
These will typically be files uploaded to the honeypot and files
downloaded inside the honeypot, or input being piped in.

Code behaves like a normal Python file handle.

Example:
    with Artifact(name) as f:
        f.write("abc")

or:
    g = Artifact("testme2")
    g.write("def")
    g.close()
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from typing import Optional, Tuple, Type, TYPE_CHECKING

from twisted.python import log

from cowrie.core.config import CowrieConfig

if TYPE_CHECKING:
    from types import TracebackType


class Artifact:
    artifactDir: str = CowrieConfig.get("honeypot", "download_path")

    def __init__(self, label: str) -> None:
        self.label: str = label

        self.fp = tempfile.NamedTemporaryFile(dir=self.artifactDir, delete=False)
        self.tempFilename = self.fp.name
        self.closed: bool = False

        self.shasum: str = ""
        self.shasumFilename: str = ""

    def __enter__(self) -> tempfile.NamedTemporaryFile:
        return self.fp

    def __exit__(
            self,
            etype: Optional[Type[BaseException]],
            einst: Optional[BaseException],
            etrace: Optional[TracebackType],
    ) -> bool:
        self.close()
        return True

    def write(self, data: bytes) -> None:
        self.fp.write(data)

    def fileno(self) -> int:
        return self.fp.fileno()

    def close(self, keep_empty: bool = False) -> Optional[Tuple[str, str]]:
        if self.fp.tell() == 0 and not keep_empty:
            os.remove(self.fp.name)
            return None

        self.fp.seek(0)

        sha256 = hashlib.sha256()
        for chunk in iter(lambda: self.fp.read(4096), b""):
            sha256.update(chunk)

        self.fp.close()
        self.closed = True

        self.shasum = sha256.hexdigest()
        self.shasumFilename = os.path.join(self.artifactDir, self.shasum)

        if os.path.exists(self.shasumFilename):
            log.msg("Not storing duplicate content " + self.shasum)
            os.remove(self.fp.name)
        else:
            os.rename(self.fp.name, self.shasumFilename)
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(self.shasumFilename, 0o666 & ~umask)

        return self.shasum, self.shasumFilename
