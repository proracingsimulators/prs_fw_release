import json
import tempfile
import unittest
from pathlib import Path

from generate_release import generate_release_structure


class GenerateReleaseTest(unittest.TestCase):
    def test_missing_min_app_version_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            release_dir = Path(tmp_dir)
            (release_dir / "changes.txt").write_text("- change 1\n", encoding="utf-8")
            firmware = {
                "Version": "1.2.3",
                "Device": "test-device"
            }
            source = release_dir / "firmware.json"
            source.write_text(json.dumps(firmware), encoding="utf-8")

            generate_release_structure(release_dir, "prs-test", "alpha")

            metadata_path = Path("v1") / "prs-test" / "firmware" / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertIsNone(metadata["versions"][0]["minAppVersion"])


if __name__ == "__main__":
    unittest.main()
