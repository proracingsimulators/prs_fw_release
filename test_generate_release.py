import json
import os
import tempfile
import unittest
from pathlib import Path

from generate_release import generate_release_structure, update_root_metadata


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

            original_cwd = Path.cwd()
            os.chdir(release_dir)
            try:
                generate_release_structure(release_dir, "prs-test", "alpha")
            finally:
                os.chdir(original_cwd)

            metadata_path = release_dir / "v1" / "prs-test" / "firmware" / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertIsNone(metadata["versions"][0]["minAppVersion"])

    def test_empty_min_app_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            release_dir = Path(tmp_dir)
            (release_dir / "changes.txt").write_text("- change 1\n", encoding="utf-8")
            firmware = {
                "Version": "1.2.3",
                "MinAppVersion": "   "
            }
            source = release_dir / "firmware.json"
            source.write_text(json.dumps(firmware), encoding="utf-8")

            original_cwd = Path.cwd()
            os.chdir(release_dir)
            try:
                with self.assertRaisesRegex(ValueError, "empty or whitespace"):
                    generate_release_structure(release_dir, "prs-test", "alpha")
            finally:
                os.chdir(original_cwd)


    def test_root_metadata_contains_generated_base_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            release_dir = Path(tmp_dir)
            (release_dir / "changes.txt").write_text("- change 1\n", encoding="utf-8")
            firmware = {
                "Version": "1.2.3",
                "Device": "test-device"
            }
            source = release_dir / "firmware.json"
            source.write_text(json.dumps(firmware), encoding="utf-8")

            original_cwd = Path.cwd()
            os.chdir(release_dir)
            try:
                generate_release_structure(release_dir, "prs-test", "alpha")
            finally:
                os.chdir(original_cwd)

            metadata_path = release_dir / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["baseName"], "v1")
            self.assertIn("prs-test", metadata["folders"])

    def test_root_metadata_keeps_previous_base_names(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            release_dir = Path(tmp_dir)
            (release_dir / "changes.txt").write_text("- change 1\n", encoding="utf-8")
            source = release_dir / "firmware.json"
            source.write_text(json.dumps({"Version": "1.2.3"}), encoding="utf-8")

            (release_dir / "v1" / "prs-old").mkdir(parents=True)

            original_cwd = Path.cwd()
            os.chdir(release_dir)
            try:
                generate_release_structure(release_dir, "prs-new", "alpha")
            finally:
                os.chdir(original_cwd)

            metadata = json.loads(
                (release_dir / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["folders"], ["prs-new", "prs-old"])


class UpdateRootMetadataTest(unittest.TestCase):
    def test_lists_only_directories_sorted(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_dir = Path(tmp_dir) / "v1"
            for name in ("prs-zeta", "prs-alpha", "prs-beta"):
                (v_dir / name).mkdir(parents=True)
            (v_dir / "metadata.json").write_text("{}", encoding="utf-8")

            update_root_metadata(v_dir)

            metadata_path = Path(tmp_dir) / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["baseName"], "v1")
            self.assertEqual(
                metadata["folders"], ["prs-alpha", "prs-beta", "prs-zeta"]
            )
            self.assertIn("updatedAt", metadata)

    def test_uses_directory_name_as_base_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_dir = Path(tmp_dir) / "v2"
            (v_dir / "prs-test").mkdir(parents=True)

            update_root_metadata(v_dir)

            metadata = json.loads(
                (Path(tmp_dir) / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["baseName"], "v2")
            self.assertEqual(metadata["folders"], ["prs-test"])

    def test_empty_version_dir_yields_empty_folders(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            v_dir = Path(tmp_dir) / "v1"
            v_dir.mkdir()

            update_root_metadata(v_dir)

            metadata = json.loads(
                (Path(tmp_dir) / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["folders"], [])


if __name__ == "__main__":
    unittest.main()
