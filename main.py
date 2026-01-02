# main.py - Main entry point and CLI for TTRPG Table Manager
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

import argparse
import sys
import os
from typing import List

from loaders import CSVTableLoader
from models import Table, TableDirectory
from logger import g_logger

def browse_directory(current_dir: TableDirectory):
    """Display contents of the current directory."""
    print(f"\n--- {current_dir.name} ---")
    
    items = []
    
    # Add '..' if we are not at root
    if current_dir.parent:
        items.append(("..", current_dir.parent))
    
    # List subdirectories
    for subdir_name in sorted(current_dir.subdirs.keys()):
        items.append((f"[DIR] {subdir_name}", current_dir.subdirs[subdir_name]))
        
    # List tables
    for table in current_dir.tables:
        items.append((f"[TABLE] {table.name}", table))
        
    for i, (name, _) in enumerate(items):
        print(f"{i + 1}. {name}")
        
    print("---------------------")
    return items

def select_item(items: List):
    """Prompt user to select an item."""
    while True:
        try:
            choice = input("\nSelect an item (number) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Exiting.")
                sys.exit(0)
            
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx][1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def query_table(table: Table):
    """Loop to query the selected table."""
    print(f"\nUsing Table: {table.name}")
    print("Type 'b' to go back, 'q' to quit.")
    
    while True:
        min_val, max_val = table.get_range_bounds()
        user_input = input(f"\n[{table.name}] Enter dice roll value ({min_val}-{max_val}): ").strip()
        
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
    parser.add_argument("-p", "--path", help="Path to a CSV file or folder containing CSV files.")
    parser.add_argument("-l", "--logo", help="Path to a custom ASCII logo file.", default=None)
    return parser.parse_args()

def print_logo(logo_path: str = None):
    """Print the ASCII logo."""
    if logo_path is None:
        # Default to resources/logo.ascii.txt relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, 'resources', 'logo.ascii.txt')
    
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            g_logger.warning(f"Failed to load logo from {logo_path}: {e}")
    else:
        g_logger.warning(f"Logo file not found: {logo_path}")

def main():
    args = parse_cli_args()

    print_logo(args.logo)
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
        root_dir = loader.load(path)
    
    if not root_dir:
        print("No tables loaded. Exiting.")
        g_logger.warning("No tables loaded.")
        return

    current_dir = root_dir

    while True:
        items = browse_directory(current_dir)
        selected = select_item(items)
        
        if isinstance(selected, TableDirectory):
            current_dir = selected
        elif isinstance(selected, Table):
            query_table(selected)

if __name__ == "__main__":
    main()
