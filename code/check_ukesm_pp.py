import re
import sys
from pathlib import Path

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]

def check_directory(directory):
    path = Path(directory)
    files = path.glob("*.pm*.pp")

    present = set()
    for f in files:
        m = re.search(r'pm(\d{4})(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', f.name)
        if m:
            present.add((int(m.group(1)), m.group(2)))

    if not present:
        print(f"\n{directory}: no files found")
        return

    min_year = min(y for y, _ in present)
    max_year = max(y for y, _ in present)

    missing = []
    for year in range(min_year, max_year + 1):
        for month in MONTHS:
            if (year, month) not in present:
                missing.append(f"{year}{month}")

    if missing:
        print(f"\n{directory}: missing {len(missing)} months ({min_year}–{max_year})")
        for m in missing:
            print(f"  {m}")
    else:
        print(f"\n{directory}: complete ({len(present)} months, {min_year}–{max_year})")

dirs = sys.argv[1:] or ["."]
for d in dirs:
    check_directory(d)
