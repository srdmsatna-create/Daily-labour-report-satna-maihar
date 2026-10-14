"""Date policy, pagination and atomic rollback regression checks."""
from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import update_secure_ts as ts


class SecureTests(unittest.TestCase):
    def test_inclusive_dates_and_fiscal_year_end(self):
        end = date(2026, 10, 14)
        for value in ('2026-08-06', '2026-09-30', '2026-10-15'):
            self.assertFalse(ts.eligible(value, end))
        for value in ('2026-10-01', '2026-10-13', '14-10-2026', '14/10/2026'):
            self.assertTrue(ts.eligible(value, end))
        self.assertFalse(ts.eligible('2027-04-01', date(2027, 4, 1)))
        with self.assertRaises(ValueError):
            ts.eligible('', end)

    def test_pagination_and_incomplete_response(self):
        class Opener:
            def __init__(self, payloads):
                self.payloads = iter(payloads)
            def open(self, *args, **kwargs):
                return io.BytesIO(json.dumps(next(self.payloads)).encode())
        c = ts.Client.__new__(ts.Client)
        c.headers = {}
        c.count_warnings = []
        c.opener = Opener([{'recordsFiltered':3,'data':[1,2]}, {'recordsFiltered':3,'data':[3]}])
        self.assertEqual(c.table('test'), [1,2,3])
        for pages in ([{'recordsFiltered':1,'data':[]}],
                      [{'recordsFiltered':2,'data':[1]}, {'recordsFiltered':3,'data':[2]}]):
            c.opener = Opener(pages)
            with self.assertRaises(ValueError):
                c.table('test')
        c.opener = Opener([{'recordsFiltered':121,'data':list(range(115))}])
        self.assertEqual(len(c.table('tsregisterpt', expected_count=115)),115)
        self.assertEqual(c.count_warnings[0]['reported'],121)

    def test_failing_fetch_retains_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'secure-ts-data.js'
            path.write_text('previous verified snapshot')
            with patch.object(ts, 'Client', side_effect=OSError('source unavailable')):
                with self.assertRaises(OSError):
                    ts.fetch(Path(tmp))
            self.assertEqual(path.read_text(), 'previous verified snapshot')


if __name__ == '__main__':
    unittest.main()
