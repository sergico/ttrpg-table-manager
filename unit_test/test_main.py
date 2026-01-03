
# tests/test_main.py
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
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

# Add parent directory to path to import modules
sys.path.append('..')
from main import parse_cli_args
from views import browse_directory, dump_table, print_logo
from models import TableDirectory, Table, TableRow


class TestMain(unittest.TestCase):
    
    def test_browse_directory(self):
        # Setup
        root = TableDirectory("root")
        sub = TableDirectory("sub")
        table = Table("t1", [], [])
        root.add_subdir(sub)
        root.add_table(table)
        
        # Test browsing root
        with patch('sys.stdout', new=StringIO()) as fake_out:
            items = browse_directory(root)
            output = fake_out.getvalue()
        
        # Should contain "sub" and "t1"
        self.assertIn("root", output)
        self.assertIn("sub", output)
        self.assertIn("t1", output)
        
        # Check returned items
        # items should be [(name, obj), ...]
        # order: subdirs then tables
        # Actually in main.py order is: parent (if any), subdirs, tables.
        
        # index 0: ("DIR sub", sub)
        # index 1: ("TABLE t1", table)
        # Note: names include [DIR] prefix
        
        self.assertEqual(len(items), 2)
        self.assertIn("[DIR ↓] sub", items[0][0])
        self.assertIn("[TABLE] t1", items[1][0])

    def test_dump_table(self):
        row = TableRow(1, 1, ["Result"])
        table = Table("test", ["R", "V"], [row])
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            dump_table(table)
            output = fake_out.getvalue()
            
        self.assertIn("Table: test", output)
        self.assertIn("R | V", output)
        self.assertIn("1 | Result", output)

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_cli_args(self, mock_parse):
        mock_args = MagicMock()
        mock_args.path = "some/path"
        mock_args.logo = "logo.txt"
        mock_parse.return_value = mock_args
        
        args = parse_cli_args()
        self.assertEqual(args.path, "some/path")
        self.assertEqual(args.logo, "logo.txt")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="LOGO")
    @patch('os.path.exists', return_value=True)
    def test_print_logo(self, mock_exists, mock_open):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_logo("logo.txt")
            self.assertEqual(fake_out.getvalue().strip(), "LOGO")

    @patch('os.path.exists', return_value=False)
    @patch('logger.g_logger.warning')
    def test_print_logo_not_found(self, mock_warn, mock_exists):
        print_logo("missing.txt")
        mock_warn.assert_called()


if __name__ == '__main__':
    unittest.main()
