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
