"""
setup_assets.py
---------------
Downloads the pre-trained models and datasets from Google Drive,
extracts them into the project root, and removes the zip files.

USAGE
-----
1. Upload your zips to Google Drive and share them (Anyone with link can view).
2. Paste the share URL (or just the file ID) into the DOWNLOADS dict below.
3. Run:  python setup_assets.py
   or:   python setup_assets.py --models-only
   or:   python setup_assets.py --data-only

GOOGLE DRIVE LINK FORMAT
-------------------------
Share URL  : https://drive.google.com/file/d/FILE_ID/view?usp=sharing
File ID    : FILE_ID   (just the long alphanumeric string between /d/ and /view)

You can paste either format into the config below; the script strips it automatically.
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION  ←  FILL IN YOUR GOOGLE DRIVE LINKS / FILE IDs HERE
# ─────────────────────────────────────────────────────────────────────────────
DOWNLOADS = {
    "models": {
        # Paste the full share URL  OR  just the file ID
        "gdrive": "https://drive.google.com/file/d/1m-82bqvhosy8sZCjXA3Q1F0mfRkDGMl_/view?usp=sharing",
        # Where to extract (relative to this script's directory)
        "extract_to": ".",
        # Expected folder name after extraction (used to confirm success)
        "expected_dir": "models",
    },
    "data": {
        "gdrive": "https://drive.google.com/file/d/1HvfRSVkhHByEvrOvWt6-o50UlPYmW8PL/view?usp=sharing",
        "extract_to": ".",
        "expected_dir": "data",
    },
}

# ── Environment variable overrides (Docker / CI friendly) ──────────────────────
# Set MODELS_GDRIVE_URL / DATA_GDRIVE_URL in the shell or docker-compose.yml
# to avoid editing this file at all.
import os as _os
for _key, _env_var in [("models", "MODELS_GDRIVE_URL"), ("data", "DATA_GDRIVE_URL")]:
    _val = _os.environ.get(_env_var, "").strip()
    if _val and "YOUR_" not in _val:
        DOWNLOADS[_key]["gdrive"] = _val
del _os, _key, _env_var, _val  # clean up temp names
# ─────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.resolve()
SEP  = "─" * 60


def _extract_file_id(url_or_id: str) -> str:
    """Accept a full Drive share URL or a bare file ID; always return the ID."""
    url_or_id = url_or_id.strip()
    if "drive.google.com" in url_or_id:
        # https://drive.google.com/file/d/<ID>/view...
        parts = url_or_id.split("/d/")
        if len(parts) < 2:
            raise ValueError(f"Cannot parse file ID from URL: {url_or_id}")
        return parts[1].split("/")[0].split("?")[0]
    return url_or_id  # already a bare ID


def _ensure_gdown() -> None:
    """Install gdown if not already available."""
    try:
        import gdown  # noqa: F401
    except ImportError:
        print("[setup] gdown not found – installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "gdown"],
            stdout=subprocess.DEVNULL,
        )
        print("[setup] gdown installed successfully.\n")


def _download(label: str, cfg: dict) -> Path:
    """Download a zip from Google Drive; return the local zip Path."""
    import gdown

    file_id  = _extract_file_id(cfg["gdrive"])
    zip_name = f"{label}.zip"
    zip_path = ROOT / zip_name

    url = f"https://drive.google.com/uc?id={file_id}"

    print(f"\n{SEP}")
    print(f"  Downloading : {label}")
    print(f"  File ID     : {file_id}")
    print(f"  Destination : {zip_path}")
    print(SEP)

    gdown.download(url, str(zip_path), quiet=False)

    if not zip_path.exists() or zip_path.stat().st_size == 0:
        raise RuntimeError(
            f"Download failed for '{label}'. "
            "Check that the file ID is correct and the file is shared publicly "
            "(Anyone with the link → Viewer)."
        )

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Downloaded  : {size_mb:.1f} MB  ->  {zip_path.name}")
    return zip_path


def _extract(zip_path: Path, extract_to: str) -> None:
    """Extract zip into the given directory."""
    dest = (ROOT / extract_to).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    print(f"\n  Extracting  : {zip_path.name}  ->  {dest}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.namelist()
        for i, member in enumerate(members, 1):
            zf.extract(member, dest)
            # Simple progress every 50 files
            if i % 50 == 0 or i == len(members):
                print(f"  Progress    : {i}/{len(members)} files extracted", end="\r")
    print()  # newline after progress


def _cleanup(zip_path: Path) -> None:
    """Delete the zip file."""
    zip_path.unlink()
    print(f"  Cleaned up  : {zip_path.name} removed")


def _verify(label: str, cfg: dict) -> None:
    """Check that the expected directory exists after extraction."""
    expected = (ROOT / cfg["extract_to"] / cfg["expected_dir"]).resolve()
    if expected.exists():
        # Count items inside
        n = sum(1 for _ in expected.rglob("*"))
        print(f"  Verified    : '{expected.name}/' exists ({n} items)")
    else:
        print(
            f"  WARNING: Expected directory '{expected}' not found after extraction.\n"
            f"           The zip may have a different internal folder name. "
            f"Check the contents manually."
        )


def run(targets: list[str]) -> None:
    _ensure_gdown()

    print(f"\n{'='*60}")
    print("  AI Fraud Detection System — Asset Setup")
    print(f"{'='*60}")
    print(f"  Project root : {ROOT}")
    print(f"  Targets      : {', '.join(targets)}\n")

    for label in targets:
        cfg = DOWNLOADS[label]

        # Skip if placeholder URL hasn't been filled in
        if "YOUR_" in cfg["gdrive"]:
            print(
                f"\n[SKIP] '{label}': Google Drive link not configured.\n"
                f"       Edit the DOWNLOADS dict in this file and paste your share URL."
            )
            continue

        # Skip if directory already populated
        expected = ROOT / cfg["extract_to"] / cfg["expected_dir"]
        if expected.exists() and any(expected.iterdir()):
            answer = input(
                f"\n'{expected.name}/' already exists and is non-empty. "
                f"Re-download and overwrite? [y/N]: "
            ).strip().lower()
            if answer != "y":
                print(f"  Skipping '{label}'.")
                continue
            shutil.rmtree(expected)

        try:
            zip_path = _download(label, cfg)
            _extract(zip_path, cfg["extract_to"])
            _cleanup(zip_path)
            _verify(label, cfg)
            print(f"\n  [OK] '{label}' setup complete!")
        except Exception as exc:
            print(f"\n  [ERROR] '{label}' failed: {exc}")
            # Remove partial zip if it exists
            zip_path = ROOT / f"{label}.zip"
            if zip_path.exists():
                zip_path.unlink()
            sys.exit(1)

    print(f"\n{'='*60}")
    print("  Setup finished. You can now run:  streamlit run app.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and unpack pre-trained models and data from Google Drive."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--models-only", action="store_true",
        help="Only download and extract the models folder."
    )
    group.add_argument(
        "--data-only", action="store_true",
        help="Only download and extract the data folder."
    )
    args = parser.parse_args()

    if args.models_only:
        targets = ["models"]
    elif args.data_only:
        targets = ["data"]
    else:
        targets = list(DOWNLOADS.keys())   # both by default

    run(targets)
