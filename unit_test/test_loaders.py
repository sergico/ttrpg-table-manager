
# tests/test_loaders.py
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
import os
import tempfile
import shutil
from loaders import CSVTableLoader
from models import TableDirectory, Table


class TestCSVTableLoader(unittest.TestCase):
    def setUp(self):
        self.loader = CSVTableLoader()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_range(self):
        self.assertEqual(self.loader._parse_range("5"), (5, 5))
        self.assertEqual(self.loader._parse_range("1-4"), (1, 4))
        self.assertEqual(self.loader._parse_range("10-20"), (10, 20))
        with self.assertRaises(ValueError):
            self.loader._parse_range("invalid")

    def test_load_file_valid(self):
        filepath = os.path.join(self.test_dir, "test.csv")
        with open(filepath, "w") as f:
            f.write("Range,Result\n1,One\n2-5,Many\n")
        
        table = self.loader._load_file(filepath)
        self.assertEqual(table.name, "test")
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].range_start, 1)
        self.assertEqual(table.rows[1].range_end, 5)

    def test_load_file_invalid_structure(self):
        filepath = os.path.join(self.test_dir, "bad.csv")
        with open(filepath, "w") as f:
            f.write("JustHeader\n")
        
        with self.assertRaises(ValueError):
            self.loader._load_file(filepath)

    def test_load_recursive(self):
        # Create structure:
        # root/
        #   table1.csv
        #   subdir/
        #     table2.csv
        
        with open(os.path.join(self.test_dir, "table1.csv"), "w") as f:
            f.write("R,V\n1,A\n")
            
        subdir = os.path.join(self.test_dir, "subdir")
        os.mkdir(subdir)
        with open(os.path.join(subdir, "table2.csv"), "w") as f:
            f.write("R,V\n2,B\n")
            
        root_dir = self.loader.load(self.test_dir)
        
        self.assertIsInstance(root_dir, TableDirectory)
        self.assertEqual(len(root_dir.tables), 1)
        self.assertEqual(root_dir.tables[0].name, "table1")
        
        self.assertIn("subdir", root_dir.subdirs)
        sub = root_dir.subdirs["subdir"]
        self.assertEqual(len(sub.tables), 1)
        self.assertEqual(sub.tables[0].name, "table2")

    def test_load_nonexistent(self):
        # Should return a directory wrapper but with no content and probably logs an error
        # Implementation returns "root_dir" always, check error handling
        # If source doesn't exist, it logs error but returns initialized root_dir object
        # which is empty. 
        # Actually load() creates root_dir based on basename of source.
        
        result = self.loader.load("nonexistent_path")
        self.assertIsInstance(result, TableDirectory)
        self.assertEqual(result.name, "nonexistent_path")
        self.assertEqual(len(result.tables), 0)


if __name__ == '__main__':
    unittest.main()
