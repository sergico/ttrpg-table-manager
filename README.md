# TTRPG Table Manager Walkthrough

## Overview
I have implemented a command-line tool to manage and query TTRPG tables stored in CSV format. The tool allows loading tables from a file or directory, selecting a table, and querying results based on dice rolls.

## Changes
### Core Logic
- **`models.py`**: Defined `Table` and `TableRow` classes. `TableRow` supports integer ranges (e.g., 1-4).
- **`loaders.py`**: Implemented `CSVTableLoader` to parse CSV files. Handles ranges like "5", "1-4", or "10-20".
- **`logger.py`**: Integrated existing logger for info/error tracking.

### CLI Interface
- **`main.py`**: Created an interactive CLI loop:
    1. Lists loaded tables.
    2. Allows user to select a table.
    3. Accepts dice roll input to show corresponding result.

## Testing
To run the project's unit tests, execute the following command from the project root:

```bash
python3 -m unittest discover tests
```

## Usage
Run the tool by providing a path to a CSV file or a directory containing CSV files using the `-p` or `--path` flag:

```bash
python3 main.py -p test_tables/
```

You can also specify a custom ASCII logo using the `-l` or `--logo` flag:

```bash
python3 main.py -p test_tables/ -l my_logo.txt
```

Or run without arguments to be prompted for a path:

```bash
python3 main.py
```

## Verification Results
I created a test table `test_tables/combat_results.csv` and verified the following:

### 1. Loading Tables
The tool successfully loads tables from a directory or file.

### 2. Querying Results
Verified correct range matching:
- **Input `5`** matched range `2-5` -> Output: "Failure"
- **Input `10`** matched value `10` -> Output: "Critical Success"

### Example Output
```text
Using Table: combat_results
Type 'b' to go back, 'q' to quit.

[combat_results] Enter dice roll value: 5

Result:
d10 | Result | Description
--------------------------
2-5 | Failure | You missed.
```
