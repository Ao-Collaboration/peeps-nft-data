#!/usr/bin/env python3
"""
Migrate image URLs from api.peeps.club to data.peeps.club
"""

import os
import re
import sys
from pathlib import Path

PEEP_DIR = Path(__file__).parent.parent.parent / "peep"
OLD_DOMAIN = "https://api.peeps.club/peep/"
NEW_DOMAIN = "https://data.peeps.club/"


def migrate_image_urls(dry_run: bool = True):
    json_files = list(PEEP_DIR.glob("*.json"))

    print(f"Found {len(json_files)} JSON files")

    updated = 0
    for json_file in json_files:
        content = json_file.read_text(encoding="utf-8")

        if OLD_DOMAIN in content:
            updated += 1
            if not dry_run:
                new_content = content.replace(OLD_DOMAIN, NEW_DOMAIN)
                json_file.write_text(new_content, encoding="utf-8")
            else:
                print(f"  Would update: {json_file.name}")

    if dry_run:
        print(f"DRY RUN: Would update {updated} files")
    else:
        print(f"Updated {updated} files")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    migrate_image_urls(dry_run=dry_run)
