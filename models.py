# models.py - Data models for TTRPG tables and rows
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

from dataclasses import dataclass
from typing import List, Any, Optional

@dataclass
class TableRow:
    """Represents a single row in a TTRPG table."""
    range_start: int
    range_end: int
    content: List[str]

    def matches(self, value: int) -> bool:
        """Check if the value falls within the row's range."""
        return self.range_start <= value <= self.range_end

class Table:
    """Represents a TTRPG table."""
    def __init__(self, name: str, headers: List[str], rows: List[TableRow]):
        self.name = name
        self.headers = headers
        self.rows = rows

    def query(self, value: int) -> Optional[TableRow]:
        """Find the row that matches the given value."""
        for row in self.rows:
            if row.matches(value):
                return row
        return None

    def get_range_bounds(self) -> tuple[int, int]:
        """Return the minimum and maximum values covered by the table."""
        if not self.rows:
            return 0, 0
        min_val = min(row.range_start for row in self.rows)
        max_val = max(row.range_end for row in self.rows)
        return min_val, max_val

    def __repr__(self):
        return f"<Table name='{self.name}' rows={len(self.rows)}>"
