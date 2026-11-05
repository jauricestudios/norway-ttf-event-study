#!/usr/bin/env python3
"""Validate the exact 21-column staging export before any database write."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

COLUMNS = [
    'message_id', 'asset', 'event_status', 'unavailability_type', 'event_type',
    'publication_time', 'event_start', 'event_stop', 'unit', 'technical_capacity',
    'available_capacity', 'unavailable_capacity', 'reason', 'remarks',
    'balancing_zone', 'market_participant', 'market_participant_code',
    'asset_eic_code', 'source_year', 'source_file', 'source_excel_row'
]


def validate_csv(path: Path) -> int:
    if not path.is_file():
        raise ValueError(f'Missing staging CSV: {path}')
    if path.stat().st_size == 0:
        raise ValueError(f'Empty staging CSV: {path}')
    seen = set()
    n = 0
    with path.open('r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f'Unexpected CSV header: {reader.fieldnames!r}; expected {COLUMNS!r}')
        for n, row in enumerate(reader, 1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'Malformed CSV record at data row {n}')
            message = (row['message_id'] or '').strip()
            if not message:
                raise ValueError(f'Missing message_id at data row {n}')
            if message in seen:
                raise ValueError(f'Duplicate message_id {message!r} at data row {n}')
            seen.add(message)
            if row['source_year'] not in {'2024', '2025', '2026'}:
                raise ValueError(f'Unexpected source_year in data row {n}: {row["source_year"]!r}')
            for key in ('publication_time', 'event_start', 'event_stop'):
                if row[key].strip():
                    try:
                        parsed = datetime.fromisoformat(row[key].strip())
                        if parsed.tzinfo is not None:
                            raise ValueError('timezone-aware timestamp cannot be loaded into a naive SQL field')
                    except ValueError as exc:
                        raise ValueError(f'Invalid {key} in data row {n}: {row[key]!r}') from exc
            for key in ('technical_capacity', 'available_capacity', 'unavailable_capacity'):
                if row[key].strip():
                    try:
                        value = Decimal(row[key])
                        if not value.is_finite():
                            raise ValueError()
                    except (InvalidOperation, ValueError) as exc:
                        raise ValueError(f'Invalid {key} at data row {n}: {row[key]!r}') from exc
            try:
                if int(row['source_excel_row']) < 4:
                    raise ValueError()
            except ValueError as exc:
                raise ValueError(f'Invalid source_excel_row at data row {n}') from exc
    if not n:
        raise ValueError('CSV has a header but no records')
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', type=Path)
    args = parser.parse_args()
    try:
        rows = validate_csv(args.csv_path)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'CSV preflight FAILED: {exc}\n')
    print(f'CSV preflight PASS: {rows} records; 21 exact columns; unique IDs; source/clock fields checked')


if __name__ == '__main__':
    main()
