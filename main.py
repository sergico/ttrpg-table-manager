import argparse
import sys
import os
from typing import List

from loaders import CSVTableLoader
from models import Table
from logger import g_logger

def list_tables(tables: List[Table]):
    """Display a list of loaded tables."""
    print("\n--- Loaded Tables ---")
    for i, table in enumerate(tables):
        print(f"{i + 1}. {table.name} (Rows: {len(table.rows)})")
    print("---------------------")

def select_table(tables: List[Table]) -> Table:
    """Prompt user to select a table."""
    while True:
        try:
            choice = input("\nSelect a table (number) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Exiting.")
                sys.exit(0)
            
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                return tables[idx]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def query_table(table: Table):
    """Loop to query the selected table."""
    print(f"\nUsing Table: {table.name}")
    print("Type 'b' to go back, 'q' to quit.")
    
    while True:
        user_input = input(f"\n[{table.name}] Enter dice roll value: ").strip()
        
        if user_input.lower() == 'q':
            print("Exiting.")
            sys.exit(0)
        if user_input.lower() == 'b':
            return

        try:
            value = int(user_input)
            row = table.query(value)
            
            if row:
                print("\nResult:")
                # Print headers and content aligned
                headers_str = " | ".join(table.headers)
                print(headers_str)
                print("-" * len(headers_str))
                
                # Reconstruct the full row display with the input value range if desired,
                # but requirements say "output has the header and the actual selected line"
                # The selected line content corresponds to the headers (minus the range column usually? 
                # or is the range column part of the header? 
                # User said: "first line is always the dice value to roll that selects the corresponding row"
                # "output has the header and the actual selected line"
                
                # The loaded table rows store 'content' which is everything AFTER the first column.
                # The headers include the first column name too probably.
                
                # Let's check how we loaded it. 
                # loader: headers = next(reader), content = row_data[1:]
                # So headers[0] is the range column name. headers[1:] correspond to row.content.
                
                # Display:
                # Range Header | Col 1 Header | Col 2 Header ...
                # Range Val    | Val 1        | Val 2 ...
                
                range_display = f"{row.range_start}" if row.range_start == row.range_end else f"{row.range_start}-{row.range_end}"
                full_row = [range_display] + row.content
                
                # Simple tab/pipe separation
                print(" | ".join(full_row))
                
            else:
                print("No match found for that value.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def parse_cli_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="TTRPG Table Manager")
    parser.add_argument("path", nargs='?', help="Path to a CSV file or folder containing CSV files.")
    return parser.parse_args()

def main():
    args = parse_cli_args()

    print("Welcome to TTRPG Table Manager")
    
    path = args.path
    loader = CSVTableLoader()
    tables = []

    # If no path provided, ask interactively or just start empty?
    # User requirement: "load can happen by direct filename or folder"
    # Doesn't strictly say it MUST be CLI arg, but good for usability.
    # If not provided args, let's ask.
    if not path:
        path = input("Enter path to CSV file or directory: ").strip()

    if path:
        g_logger.info(f"Loading tables from {path}...")
        tables = loader.load(path)
    
    if not tables:
        print("No tables loaded. Exiting.")
        g_logger.warning("No tables loaded.")
        return

    while True:
        list_tables(tables)
        selected_table = select_table(tables)
        query_table(selected_table)

if __name__ == "__main__":
    main()
