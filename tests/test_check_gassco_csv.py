"""Run with: python3 -m unittest discover -s tests -v."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_gassco_csv.py'
spec = importlib.util.spec_from_file_location('check_gassco_csv', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def make_row(**updates):
    r = {c: '' for c in module.COLUMNS}
    r.update(message_id='UMM_001', source_year='2024', source_excel_row='4',
             publication_time='2024-09-01 06:00:00', event_start='2024-09-01 06:00:00')
    r.update(updates)
    return r


class CsvPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'stage.csv'

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows, fields=None):
        with self.path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields or module.COLUMNS)
            w.writeheader()
            w.writerows(rows)

    def test_valid_two_rows(self):
        self.write([make_row(), make_row(message_id='UMM_002')])
        self.assertEqual(module.validate_csv(self.path), 2)

    def test_duplicate_id_rejected(self):
        self.write([make_row(), make_row()])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            module.validate_csv(self.path)

    def test_bad_header_rejected(self):
        self.write([make_row()], fields=list(reversed(module.COLUMNS)))
        with self.assertRaisesRegex(ValueError, 'header'):
            module.validate_csv(self.path)

    def test_empty_records_rejected(self):
        self.write([])
        with self.assertRaisesRegex(ValueError, 'no records'):
            module.validate_csv(self.path)

    def test_missing_id_rejected(self):
        self.write([make_row(message_id='')])
        with self.assertRaisesRegex(ValueError, 'Missing message_id'):
            module.validate_csv(self.path)

    def test_bad_time_rejected(self):
        self.write([make_row(publication_time='not-a-time')])
        with self.assertRaisesRegex(ValueError, 'Invalid publication_time'):
            module.validate_csv(self.path)

    def test_timezone_aware_timestamp_rejected(self):
        self.write([make_row(publication_time='2024-09-01T06:00:00+02:00')])
        with self.assertRaisesRegex(ValueError, 'Invalid publication_time'):
            module.validate_csv(self.path)

    def test_bad_numeric_capacity_rejected(self):
        self.write([make_row(technical_capacity='not-a-number')])
        with self.assertRaisesRegex(ValueError, 'Invalid technical_capacity'):
            module.validate_csv(self.path)

    def test_bad_source_year_rejected(self):
        self.write([make_row(source_year='2035')])
        with self.assertRaisesRegex(ValueError, 'source_year'):
            module.validate_csv(self.path)

    def test_missing_file_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing staging'):
            module.validate_csv(self.path)


if __name__ == '__main__':
    unittest.main()
