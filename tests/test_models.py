
# tests/test_models.py
#
# Copyright (C) 2026 Sergio Borghese <s.borghese@netresults.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from models import TableRow, Table, TableDirectory


class TestTableRow(unittest.TestCase):
    def test_matches(self):
        row = TableRow(range_start=1, range_end=5, content=["Data"])
        self.assertTrue(row.matches(1))
        self.assertTrue(row.matches(5))
        self.assertTrue(row.matches(3))
        self.assertFalse(row.matches(0))
        self.assertFalse(row.matches(6))


class TestTable(unittest.TestCase):
    def setUp(self):
        self.rows = [
            TableRow(1, 4, ["Low"]),
            TableRow(5, 5, ["Mid"]),
            TableRow(6, 10, ["High"])
        ]
        self.table = Table("TestTable", ["Range", "Result"], self.rows)

    def test_query_match(self):
        row = self.table.query(3)
        self.assertIsNotNone(row)
        self.assertEqual(row.content, ["Low"])

        row = self.table.query(5)
        self.assertIsNotNone(row)
        self.assertEqual(row.content, ["Mid"])

    def test_query_no_match(self):
        row = self.table.query(11)
        self.assertIsNone(row)

    def test_get_range_bounds(self):
        min_val, max_val = self.table.get_range_bounds()
        self.assertEqual(min_val, 1)
        self.assertEqual(max_val, 10)

    def test_range_bounds_empty(self):
        table = Table("Empty", [], [])
        self.assertEqual(table.get_range_bounds(), (0, 0))

    def test_repr(self):
        self.assertIn("TestTable", repr(self.table))
        self.assertIn("rows=3", repr(self.table))


class TestTableDirectory(unittest.TestCase):
    def test_add_table(self):
        root = TableDirectory("root")
        table = Table("t1", [], [])
        root.add_table(table)
        self.assertEqual(len(root.tables), 1)
        self.assertEqual(root.tables[0], table)

    def test_add_subdir(self):
        root = TableDirectory("root")
        subdir = TableDirectory("sub")
        root.add_subdir(subdir)
        self.assertIn("sub", root.subdirs)
        self.assertEqual(root.subdirs["sub"], subdir)
        self.assertEqual(subdir.parent, root)


if __name__ == '__main__':
    unittest.main()
