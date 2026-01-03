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
from views import browse_directory, select_item, print_logo, query_table


def parse_cli_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="TTRPG Table Manager")
    parser.add_argument(
        "-p", "--path",
        help="Path to a CSV file or folder containing CSV files."
    )
    parser.add_argument(
        "-l", "--logo",
        help="Path to a custom ASCII logo file.",
        default=None
    )
    return parser.parse_args()


def main():
    args = parse_cli_args()

    print_logo(args.logo)
    print("Welcome to TTRPG Table Manager")

    path = args.path
    loader = CSVTableLoader()

    # If no path provided, ask interactively
    if not path:
        path = input("Enter path to CSV file or directory: ").strip()

    root_dir = None
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
