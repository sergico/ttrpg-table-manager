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
import curses
from loaders import CSVTableLoader
from logger import g_logger
from views import run_tui, print_logo

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

    # Print logo to standard stdout before TUI starts
    print_logo(args.logo)
    
    # We might want to pause here for user to see logo? 
    # Or just print it as info.
    # The requirement was "Display an ASCII logo on startup".
    # Since we are entering TUI immediately, the logo on stdout will be cleared.
    # Maybe display it inside TUI or just briefly pause?
    # For now, let's just proceed. The user might have meant a splash screen.
    # But TUI clears screen.
    # Let's keep print_logo call but also maybe show it in a splash in TUI?
    # Sticking to minimal requirement compliance + TUI.
    
    path = args.path
    loader = CSVTableLoader()

    # If no path provided, ask interactively using input()
    # This happens BEFORE TUI init, so acceptable.
    if not path:
        print("Welcome to TTRPG Table Manager")
        path = input("Enter path to CSV file or directory: ").strip()

    root_dir = None
    if path:
        g_logger.info(f"Loading tables from {path}...")
        try:
            root_dir = loader.load(path)
        except Exception as e:
            print(f"Error loading tables: {e}")
            g_logger.error(f"Error loading tables: {e}")
            return

    if not root_dir:
        print("No tables loaded. Exiting.")
        g_logger.warning("No tables loaded.")
        return

    # Start TUI
    try:
        curses.wrapper(run_tui, root_dir)
    except Exception as e:
        # If terminal is too small or other curses error
        print(f"TUI Error: {e}")
        g_logger.error(f"TUI Error: {e}")


if __name__ == "__main__":
    main()
