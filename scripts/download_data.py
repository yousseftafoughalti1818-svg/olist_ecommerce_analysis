"""Download the Olist Brazilian e-commerce dataset (public, MIT licence).

Usage:
    python scripts/download_data.py
"""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from olist_analysis import config  # noqa: E402


def download(force: bool = False) -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for filename in config.TABLES.values():
        target = config.RAW_DIR / filename
        if target.exists() and not force:
            print(f"already there: {filename}")
            continue
        print(f"downloading {filename} ...")
        urllib.request.urlretrieve(config.DATA_URL + filename, target)
    print(f"Data saved in {config.RAW_DIR}")


if __name__ == "__main__":
    download(force="--force" in sys.argv)
