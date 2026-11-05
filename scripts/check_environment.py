#!/usr/bin/env python3
"""Check local Python dependencies, binaries, and optional private source files."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ['numpy', 'pandas', 'openpyxl', 'matplotlib', 'scipy', 'ipykernel']
INPUTS = [
    'data/raw/gassco/gassco_umm_unplanned_2024.xlsx',
    'data/raw/gassco/gassco_umm_unplanned_2025.xlsx',
    'data/raw/gassco/gassco_umm_unplanned_2026.xlsx',
    'data/raw/ttf/ice_dutch_ttf_futures_2024-07-01_to_2026-09-17.csv',
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-inputs', action='store_true', help='also require all ignored raw input files')
    args = p.parse_args()
    failed = False
    if sys.version_info < (3, 10):
        print('FAIL Python >=3.10 is required')
        failed = True
    else:
        print(f'OK Python {sys.version.split()[0]}')
    for package in PACKAGES:
        found = importlib.util.find_spec(package) is not None
        print(f'{"OK" if found else "FAIL"} Python package: {package}')
        failed |= not found
    found = shutil.which('psql') is not None
    print(f'{"OK" if found else "FAIL"} PostgreSQL client: psql')
    failed |= not found
    if args.check_inputs:
        for relative in INPUTS:
            found = (ROOT / relative).is_file()
            print(f'{"OK" if found else "FAIL"} Raw input: {relative}')
            failed |= not found
    if failed:
        p.exit(1, 'Environment check FAILED; install requirements/psql or restore private inputs.\n')
    print('Environment check PASS (not a database/market-data provenance verification).')


if __name__ == '__main__':
    main()
