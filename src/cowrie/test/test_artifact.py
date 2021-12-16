import hashlib
import os
import tempfile
import unittest

from cowrie.core.artifact import Artifact

Artifact.artifactDir = os.path.join(tempfile.gettempdir(), "cowrie-artifacts")


class MyTest(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(Artifact.artifactDir)

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
        a.close(keepEmpty=True)

        self.assertEqual(a.shasum, sha256)
        path = os.path.join(Artifact.artifactDir, sha256)
        self.assertEqual(a.shasumFilename, path)
        self.assertTrue(os.path.exists(path))

    def tearDown(self) -> None:
        for name in os.listdir(Artifact.artifactDir):
            os.unlink(os.path.join(Artifact.artifactDir, name))
        os.rmdir(Artifact.artifactDir)


if __name__ == "__main__":
    unittest.main()
