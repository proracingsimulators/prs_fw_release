#!/usr/bin/env python3
"""Generate release folder structure for firmware JSON files.

Expected output pattern (for each input JSON file):
v1/{baseName}/{jsonName}/lastest.json
v1/{baseName}/{jsonName}/{version}.json
v1/{baseName}/{jsonName}/metadata.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Generate release files and metadata for firmware JSONs."
	)
	parser.add_argument(
		"release_dir",
		type=Path,
		help="Directory containing firmware JSON files and changes.txt",
	)
	parser.add_argument(
		"base_name",
		help="Base project name used as output root folder",
	)
	parser.add_argument(
		"release_version",
		choices=["stable", "beta", "alpha"],
		default="stable",
		help="Release version (optional, default: stable)",
	)
	return parser.parse_args()


def load_changes(changes_path: Path) -> List[str]:
	if not changes_path.is_file():
		raise FileNotFoundError(
			f"changes.txt not found in release directory: {changes_path}"
		)

	content = changes_path.read_text(encoding="utf-8")
	return [line.strip() for line in content.splitlines() if line.strip()]


def get_release_json_files(release_dir: Path) -> List[Path]:
	json_files = sorted(file for file in release_dir.glob("*.json") if file.is_file())

	if not json_files:
		raise FileNotFoundError(f"No JSON files found in release directory: {release_dir}")

	for file_path in json_files:
		try:
			with file_path.open("r", encoding="utf-8") as fp:
				json.load(fp)
		except json.JSONDecodeError as exc:
			raise ValueError(f"Invalid JSON file '{file_path.name}': {exc}") from exc

	return json_files


def extract_version_from_json(json_file_path: Path) -> str:
	with json_file_path.open("r", encoding="utf-8") as fp:
		payload = json.load(fp)

	if not isinstance(payload, dict):
		raise ValueError(f"JSON root must be an object in file: {json_file_path}")

	for key in ("Version", "version"):
		value = payload.get(key)
		if value is None:
			continue

		version = str(value).strip()
		if version:
			return version

	raise ValueError(
		f"Version field not found in '{json_file_path.name}'. "
		"Expected 'Version' or 'version'."
	)


def load_existing_metadata(metadata_path: Path) -> Dict[str, Any]:
	if not metadata_path.exists():
		return {}

	try:
		with metadata_path.open("r", encoding="utf-8") as fp:
			data = json.load(fp)
	except json.JSONDecodeError as exc:
		raise ValueError(f"metadata.json is invalid in '{metadata_path.parent}': {exc}") from exc

	if not isinstance(data, dict):
		raise ValueError(f"metadata.json must be a JSON object: {metadata_path}")

	return data


def update_metadata(
	metadata_path: Path,
	*,
	base_name: str,
	json_name: str,
	version: str,
	source_file_name: str,
	changes: List[str],
) -> None:
	metadata = load_existing_metadata(metadata_path)
	versions = metadata.get("versions", [])

	if not isinstance(versions, list):
		raise ValueError(f"'versions' must be a list in metadata: {metadata_path}")

	release_info = {
		"version": version,
		"file": f"{version}.json",
		"sourceFile": source_file_name,
		"releasedAt": datetime.now(timezone.utc).isoformat(),
		"changesFile": "changes.txt",
		"changes": changes,
	}

	replaced = False
	for idx, item in enumerate(versions):
		if isinstance(item, dict) and item.get("version") == version:
			versions[idx] = release_info
			replaced = True
			break

	if not replaced:
		versions.append(release_info)

	metadata.update(
		{
			"baseName": base_name,
			"jsonName": json_name,
			"latest": version,
			"versions": versions,
		}
	)

	with metadata_path.open("w", encoding="utf-8") as fp:
		json.dump(metadata, fp, indent=2, ensure_ascii=False)
		fp.write("\n")


def update_base_metadata(base_dir: Path, base_name: str) -> None:
	folders = sorted(entry.name for entry in base_dir.iterdir() if entry.is_dir())

	metadata = {
		"baseName": base_name,
		"folders": folders,
		"updatedAt": datetime.now(timezone.utc).isoformat(),
	}

	metadata_path = base_dir / "metadata.json"
	with metadata_path.open("w", encoding="utf-8") as fp:
		json.dump(metadata, fp, indent=2, ensure_ascii=False)
		fp.write("\n")


def generate_release_structure(release_dir: Path, base_name: str, release_version: str) -> None:
	if not release_dir.is_dir():
		raise NotADirectoryError(f"Release directory not found: {release_dir}")

	changes = load_changes(release_dir / "changes.txt")
	json_files = get_release_json_files(release_dir)

	for source_json_path in json_files:
		json_name = source_json_path.stem
		version = extract_version_from_json(source_json_path)
		target_dir = Path("v1") / base_name / json_name
		target_dir.mkdir(parents=True, exist_ok=True)

		copy2(source_json_path, target_dir / "latest.json")
		copy2(source_json_path, target_dir / f"latest-{release_version}.json")
		copy2(source_json_path, target_dir / f"{version}.json")

		update_metadata(
			target_dir / "metadata.json",
			base_name=base_name,
			json_name=json_name,
			version=version,
			source_file_name=source_json_path.name,
			changes=changes,
		)

		print(f"Generated release for {json_name} ({version})")

	base_dir = Path("v1") / base_name
	update_base_metadata(base_dir, base_name)
	print(f"Updated base metadata for {base_name}")


def main() -> None:
	args = parse_args()
	generate_release_structure(args.release_dir, args.base_name, args.release_version)


if __name__ == "__main__":
	main()
