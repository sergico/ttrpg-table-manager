from abc import ABC, abstractmethod
from typing import List, Dict, Any
import csv
import os
import glob
from models import Table, TableRow
from logger import g_logger

class TableLoader(ABC):
    """Abstract base class for table loaders."""
    
    @abstractmethod
    def load(self, source: str) -> List[Table]:
        """Load tables from a source (file or directory)."""
        pass

class CSVTableLoader(TableLoader):
    """Loads tables from CSV files."""

    def load(self, source: str) -> List[Table]:
        tables = []
        if os.path.isdir(source):
            # Load all .csv files in the directory recursively
            files = glob.glob(os.path.join(source, "**/*.csv"), recursive=True)
            for f in files:
                try:
                    table = self._load_file(f)
                    tables.append(table)
                except Exception as e:
                    g_logger.error(f"Failed to load table from {f}: {e}")
        elif os.path.isfile(source):
            try:
                tables.append(self._load_file(source))
            except Exception as e:
                g_logger.error(f"Failed to load table from {source}: {e}")
        else:
            g_logger.error(f"Source not found: {source}")
        
        return tables

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
