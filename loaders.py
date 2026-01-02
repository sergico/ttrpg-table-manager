# loaders.py - Classes for loading TTRPG tables from files
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

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import csv
import os
import glob
from models import Table, TableRow, TableDirectory
from logger import g_logger

class TableLoader(ABC):
    """Abstract base class for table loaders."""
    
    @abstractmethod
    def load(self, source: str) -> TableDirectory:
        """Load tables from a source (file or directory)."""
        pass

class CSVTableLoader(TableLoader):
    """Loads tables from CSV files."""

    def load(self, source: str) -> TableDirectory:
        root_name = os.path.basename(os.path.abspath(source))
        root_dir = TableDirectory(name=root_name)

        if os.path.isfile(source):
            try:
                table = self._load_file(source)
                root_dir.add_table(table)
            except Exception as e:
                g_logger.error(f"Failed to load table from {source}: {e}")
        elif os.path.isdir(source):
            self._load_recursive(source, root_dir)
        else:
            g_logger.error(f"Source not found: {source}")
        
        return root_dir

    def _load_recursive(self, current_path: str, current_dir: TableDirectory):
        # Load files in current directory
        for item in os.listdir(current_path):
            full_path = os.path.join(current_path, item)
            if os.path.isfile(full_path) and item.endswith('.csv'):
                try:
                    table = self._load_file(full_path)
                    current_dir.add_table(table)
                except Exception as e:
                    g_logger.error(f"Failed to load table from {full_path}: {e}")
            elif os.path.isdir(full_path):
                # Create subdirectory node
                subdir = TableDirectory(name=item)
                current_dir.add_subdir(subdir)
                # Recurse
                self._load_recursive(full_path, subdir)

    def _load_file(self, filepath: str) -> Table:
        filename = os.path.basename(filepath)
        table_name = os.path.splitext(filename)[0]
        
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            if not headers or len(headers) < 2:
                raise ValueError("CSV must have at least a header row and two columns")
            
            rows = []
            for line_num, row_data in enumerate(reader, start=2):
                if not row_data:
                    continue
                
                # First column is the range (e.g., "1", "2-5")
                range_str = row_data[0].strip()
                try:
                    range_start, range_end = self._parse_range(range_str)
                    content = row_data[1:]
                    rows.append(TableRow(range_start, range_end, content))
                except ValueError as e:
                     g_logger.warning(f"Skipping invalid row {line_num} in {filepath}: {e}")

            g_logger.info(f"Loaded table '{table_name}' with {len(rows)} rows from {filepath}")
            return Table(table_name, headers, rows)

    def _parse_range(self, range_str: str) -> tuple[int, int]:
        """Parse a range string like '5' or '1-4' into (start, end)."""
        if '-' in range_str:
            parts = range_str.split('-')
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        
        return int(range_str), int(range_str)
