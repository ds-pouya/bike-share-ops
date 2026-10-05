"""Download the initial Citi Bike archive; preserve raw bytes and source metadata."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://s3.amazonaws.com/tripdata/202501-citibike-tripdata.zip"
EXPECTED_BYTES = 414_213_312  # Official bucket listing checked 2026-10-05.
DEST = ROOT / "data/raw/citibike/2025-01/202501-citibike-tripdata.zip"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    headers = {}
    downloaded_at = None
    if not DEST.exists():
        partial = DEST.with_suffix(".zip.part")
        with urlopen(URL, timeout=60) as response, partial.open("wb") as output:
            headers = {key: response.headers.get(key) for key in ("ETag", "Last-Modified")}
            received = 0
            next_report = 50 * 1024 * 1024
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                received += len(chunk)
                if received >= next_report:
                    print(f"Downloaded {received / 1024**2:.0f} MiB", flush=True)
                    next_report += 50 * 1024 * 1024
        downloaded_at = datetime.now(timezone.utc).isoformat()
        if partial.stat().st_size != EXPECTED_BYTES:
            raise ValueError("Archive size differs from the checked listing; inspect the source before proceeding.")
        with ZipFile(partial) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise ValueError(f"Archive failed CRC verification: {bad_member}")
        partial.replace(DEST)
    if DEST.stat().st_size != EXPECTED_BYTES:
        raise ValueError("Existing archive size differs from the checked listing.")
    with ZipFile(DEST) as archive:
        if bad_member := archive.testzip():
            raise ValueError(f"Archive failed CRC verification: {bad_member}")
        members = [{"name": item.filename, "bytes": item.file_size} for item in archive.infolist()]
    manifest_path = DEST.parent / "download_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["sha256"] != sha256(DEST):
            raise ValueError("Archive no longer matches its recorded checksum.")
    else:
        manifest = {
            "source_url": URL,
            "downloaded_at_utc": downloaded_at,
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "bytes": DEST.stat().st_size,
            "sha256": sha256(DEST),
            "response_headers": headers,
            "archive_members": members,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
