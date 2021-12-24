import hashlib
import os
import tempfile
import unittest

from cowrie.core.artifact import Artifact

Artifact.artifactDir = os.path.join(tempfile.gettempdir(), "cowrie-artifacts")


class TestArtifact(unittest.TestCase):  # TODO: file_storage_path
    @classmethod
    def setUpClass(cls) -> None:
        os.mkdir(Artifact.artifactDir)

    @classmethod
    def tearDownClass(cls) -> None:
        os.rmdir(Artifact.artifactDir)

    def tearDown(self) -> None:
        for name in os.listdir(Artifact.artifactDir):
            os.unlink(os.path.join(Artifact.artifactDir, name))

    def test_hello_world(self) -> None:
        content = b"Hello world"

        a = Artifact("some_artifact")
        a.write(content)
        r = a.close()
        self.assertIsNotNone(r)
        sha256, path = r  # type: ignore # TODO: refactor Artifact

        self.assertEqual(hashlib.sha256(content).hexdigest(), sha256)
        self.assertTrue(os.path.exists(path))

        os.unlink(path)

    def test_keep_empty(self) -> None:
        content = b""

        a = Artifact("some_empty_artifact")
        r = a.close(keep_empty=True)
        self.assertIsNotNone(r)
        sha256, path = r  # type: ignore # TODO: refactor Artifact

        self.assertEqual(a.shasum, hashlib.sha256(content).hexdigest())
        self.assertTrue(os.path.exists(path))

        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
