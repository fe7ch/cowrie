import hashlib
import os
import tempfile
import unittest

from cowrie.core.artifact import Artifact

Artifact.download_path = os.path.join(tempfile.gettempdir(), "cowrie-artifacts")


class TestArtifact(unittest.TestCase):  # TODO: file_storage_path
    @classmethod
    def setUpClass(cls) -> None:
        os.mkdir(Artifact.download_path)

    @classmethod
    def tearDownClass(cls) -> None:
        os.rmdir(Artifact.download_path)

    def tearDown(self) -> None:
        for name in os.listdir(Artifact.download_path):
            os.unlink(os.path.join(Artifact.download_path, name))

    def test_artifact_hello_world(self) -> None:
        content = b"Hello world"

        a = Artifact()
        a.write(content)
        a.close()

        self.assertEqual(a.sha256, hashlib.sha256(content).hexdigest())
        self.assertTrue(os.path.exists(a.path))

        os.unlink(a.path)

    def test_artifact_keep_empty(self) -> None:
        a = Artifact(keep_empty=True)
        a.close()

        self.assertEqual(a.sha256, hashlib.sha256(b"").hexdigest())
        self.assertTrue(os.path.exists(a.path))

        os.unlink(a.path)


if __name__ == "__main__":
    unittest.main()
