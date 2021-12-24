# Copyright (c) 2016 Michel Oosterhof <michel@oosterhof.net>
from __future__ import annotations

import os
import tempfile

from twisted.python import log

from cowrie.core import utils
from cowrie.core.config import CowrieConfig


class Artifact:
    """This class contains code to handling saving of honeypot artifacts.

    These will typically be files uploaded to the honeypot and files downloaded inside the honeypot,
    or input being piped in.

    Example:
        a = Artifact(keep_empty=True)
        a.write("Hello world")
        a.close()

        print(a.sha256)
        if a.path:
            print(a.path)
    """

    download_path = CowrieConfig.get("honeypot", "download_path")

    def __init__(self, keep_empty: bool = False) -> None:
        self._f = tempfile.NamedTemporaryFile(dir=self.download_path, delete=False)
        self._keep_empty = keep_empty
        self._sha256 = ""
        self._path = ""

    @property
    def sha256(self) -> str:
        return self._sha256

    @property
    def path(self) -> str:
        return self._path

    def write(self, data: bytes) -> int:
        return self._f.write(data)

    def close(self) -> None:
        self._sha256 = utils.sha256_of_file_object(self._f)

        if not self._keep_empty:
            self._f.seek(0, 2)
            if self._f.tell() == 0:
                self._f.close()
                os.remove(self._f.name)
                return

        self._f.close()

        try:
            self._path = utils.store_file_by_sha256(self._f.name, self._sha256)
        except FileExistsError:
            log.msg(f"Known artifact; sha256 = {self._sha256}")
            os.remove(self._f.name)
        else:
            log.msg(f"New artifact was be saved; sha256 = {self._sha256}, path = {self._path:s}")
