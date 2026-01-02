
# tests/test_logger.py
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
import logging
from logger import setup_logging


class TestLogger(unittest.TestCase):
    def test_setup_logging(self):
        logger = setup_logging(log_file="test.log", verbose=True)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertTrue(logger.hasHandlers())
        
        # Check handlers
        # We expect a FileHandler and a StreamHandler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        
        self.assertTrue(file_handlers)
        self.assertTrue(stream_handlers)
        
        # Initialize non-verbose
        logger = setup_logging(log_file="test.log", verbose=False)
        self.assertEqual(logger.level, logging.INFO)

if __name__ == '__main__':
    unittest.main()
