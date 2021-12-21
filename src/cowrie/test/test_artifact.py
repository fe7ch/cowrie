import hashlib
import os
import tempfile
import unittest

from cowrie.core.artifact import Artifact

Artifact.artifactDir = os.path.join(tempfile.gettempdir(), "cowrie-artifacts")


class TestArtifact(unittest.TestCase):
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
        sha256 = hashlib.sha256(content).hexdigest()

        a = Artifact("some_artifact")
        a.write(content)
        a.close()

        self.assertEqual(a.shasum, sha256)
        path = os.path.join(Artifact.artifactDir, sha256)
        self.assertEqual(a.shasumFilename, path)
        self.assertTrue(os.path.exists(path))

    def test_keep_empty(self) -> None:
        content = b""
        sha256 = hashlib.sha256(content).hexdigest()

        a = Artifact("some_empty_artifact")
        a.close(keep_empty=True)

        self.assertEqual(a.shasum, sha256)
        path = os.path.join(Artifact.artifactDir, sha256)
        self.assertEqual(a.shasumFilename, path)
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
