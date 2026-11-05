"""Smoke tests for guardrails and generated psql input; NOT a PostgreSQL integration test."""
import csv
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LoaderSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ('scripts', 'data/staging', 'bin'):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        for file in ('load_gassco_csv.sh', 'check_gassco_csv.py'):
            shutil.copy(ROOT / 'scripts' / file, self.root / 'scripts' / file)
        with (self.root / 'data/staging/gassco_umm_import.csv').open('w', newline='') as f:
            from test_check_gassco_csv import module, make_row
            w = csv.DictWriter(f, fieldnames=module.COLUMNS)
            w.writeheader()
            w.writerow(make_row())
        mock = self.root / 'bin' / 'psql'
        mock.write_text('#!/usr/bin/env bash\ncat > "$PSQL_CAPTURE"\necho "COPY 1"\necho "raw_messages=1"\necho "eligible_reductions=1"\n')
        mock.chmod(0o755)
        self.env = os.environ.copy()
        self.env['PATH'] = f'{self.root / "bin"}:{self.env["PATH"]}'
        self.env['PSQL_CAPTURE'] = str(self.root / 'captured.sql')

    def tearDown(self):
        self.tmp.cleanup()

    def run_loader(self, db):
        return subprocess.run(['bash', str(self.root/'scripts/load_gassco_csv.sh'), db],
                              env=self.env, text=True, capture_output=True)

    def test_non_test_database_refused(self):
        result = self.run_loader('norway_ttf')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root/'captured.sql').exists())

    def test_valid_test_db_emits_guarded_copy(self):
        result = self.run_loader('norway_ttf_script_test')
        self.assertEqual(result.returncode, 0, result.stderr)
        sql = (self.root/'captured.sql').read_text()
        self.assertIn('BEGIN;', sql)
        self.assertIn('LOCK TABLE raw.gassco_umm_import IN ACCESS EXCLUSIVE MODE;', sql)
        self.assertIn("RAISE EXCEPTION 'Target table is not empty'", sql)
        self.assertIn('\\copy raw.gassco_umm_import', sql)
        self.assertIn('COMMIT;', sql)

    def test_missing_input_never_calls_psql(self):
        (self.root/'data/staging/gassco_umm_import.csv').unlink()
        result = self.run_loader('norway_ttf_script_test')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'captured.sql').exists())


if __name__ == '__main__':
    unittest.main()
