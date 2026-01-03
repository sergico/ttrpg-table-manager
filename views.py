
"""views.py: Manages the CLI views and user interaction."""

__author__      = "Sergio Borghese"
__copyright__   = "Copyright 2026, "
__credits__     = []
__license__     = "GPLv3"
__version__		= "2.0.0"
__email__       = "s.borghese@netresults.it"
__status__      = "Development"

import sys
import os
import json
import curses
from typing import List, Tuple, Any, Optional, Dict
from models import Table, TableDirectory
from logger import g_logger


# Curses color mapping
COLOR_MAP = {
    'black': curses.COLOR_BLACK,
    'red': curses.COLOR_RED,
    'green': curses.COLOR_GREEN,
    'yellow': curses.COLOR_YELLOW,
    'blue': curses.COLOR_BLUE,
    'magenta': curses.COLOR_MAGENTA,
    'cyan': curses.COLOR_CYAN,
    'white': curses.COLOR_WHITE
}


def load_theme(theme_path: str = None) -> Dict:
    """Load theme configuration from JSON file."""
    if theme_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(base_dir, 'resources', 'theme.json')
    
    # Default theme if file not found
    default_theme = {
        "name": "Default Dark",
        "colors": {
            "directory": {"foreground": "cyan", "background": "black"},
            "table": {"foreground": "green", "background": "black"},
            "logo": {"foreground": "yellow", "background": "black"},
            "status_bar": {"foreground": "white", "background": "blue"},
            "selected": {"foreground": "black", "background": "white"},
            "header": {"foreground": "white", "background": "black"}
        }
    }
    
    if os.path.exists(theme_path):
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme = json.load(f)
                g_logger.info(f"Loaded theme: {theme.get('name', 'Unknown')}")
                return theme
        except Exception as e:
            g_logger.warning(f"Failed to load theme from {theme_path}: {e}")
    
    return default_theme


def init_color_pairs(theme: Dict):
    """Initialize curses color pairs from theme."""
    if not curses.has_colors():
        return
    
    curses.start_color()
    colors = theme.get('colors', {})
    
    # Pair 1: Directories
    dir_fg = COLOR_MAP.get(colors.get('directory', {}).get('foreground', 'cyan'), curses.COLOR_CYAN)
    dir_bg = COLOR_MAP.get(colors.get('directory', {}).get('background', 'black'), curses.COLOR_BLACK)
    curses.init_pair(1, dir_fg, dir_bg)
    
    # Pair 2: Tables
    tbl_fg = COLOR_MAP.get(colors.get('table', {}).get('foreground', 'green'), curses.COLOR_GREEN)
    tbl_bg = COLOR_MAP.get(colors.get('table', {}).get('background', 'black'), curses.COLOR_BLACK)
    curses.init_pair(2, tbl_fg, tbl_bg)
    
    # Pair 3: Logo
    logo_fg = COLOR_MAP.get(colors.get('logo', {}).get('foreground', 'yellow'), curses.COLOR_YELLOW)
    logo_bg = COLOR_MAP.get(colors.get('logo', {}).get('background', 'black'), curses.COLOR_BLACK)
    curses.init_pair(3, logo_fg, logo_bg)
    
    # Pair 4: Status bar
    status_fg = COLOR_MAP.get(colors.get('status_bar', {}).get('foreground', 'white'), curses.COLOR_WHITE)
    status_bg = COLOR_MAP.get(colors.get('status_bar', {}).get('background', 'blue'), curses.COLOR_BLUE)
    curses.init_pair(4, status_fg, status_bg)


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


def draw_status_bar(stdscr, path_str: str, table_name: str, width: int, use_colors: bool = True):
    """Draw the status bar at the bottom of the screen."""
    height, _ = stdscr.getmaxyx()
    status_y = height - 1
    
    # Ensure strings don't exceed width
    # Layout: [ PATH ... ] | [ TABLE ... ] | [ COMMANDS ]
    
    # Calculate available space
    cmd_str = "Keys: ↑/↓ Move, Enter Select, b Back, d Dump, q Quit"
    cmd_len = len(cmd_str)
    
    # Basic truncation if needed (unlikely for typical terms but good practice)
    if cmd_len >= width:
        cmd_str = cmd_str[:width-1]
    
    remaining_w = width - cmd_len - 4 # 4 for separators
    if remaining_w < 10:
        remaining_w = 10 # minimal fallback
        
    part_w = remaining_w // 2
    
    path_display = f"Path: {path_str}"
    if len(path_display) > part_w:
        path_display = "..." + path_display[-(part_w-3):]
    else:
        path_display = path_display.ljust(part_w)
        
    table_display = f"Table: {table_name}"
    if len(table_display) > part_w:
        table_display = table_display[:part_w-3] + "..."
    else:
        table_display = table_display.ljust(part_w)

    status_line = f"{path_display} | {table_display} | {cmd_str}"
    
    # Pad to full width
    if len(status_line) < width:
        status_line += " " * (width - len(status_line) - 1)
        
    try:
        if use_colors and curses.has_colors():
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(status_y, 0, status_line[:width-1])
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(status_y, 0, status_line[:width-1])
            stdscr.attroff(curses.A_REVERSE)
    except curses.error:
        pass


def get_items_for_dir(current_dir: TableDirectory) -> List[Tuple[str, str, Any]]:
    """Return list of (display_name, type, object) for the directory."""
    items = []
    
    if current_dir.parent:
        items.append(("..", "DIR_UP", current_dir.parent))
        
    for sub_name in sorted(current_dir.subdirs.keys()):
        items.append((sub_name, "DIR", current_dir.subdirs[sub_name]))
        
    for table in current_dir.tables:
        items.append((table.name, "TABLE", table))
        
    return items


def dump_table_view(stdscr, table: Table):
    """View to dump table content."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    title = f"Table Dump: {table.name}"
    stdscr.addstr(0, 0, title, curses.A_BOLD)
    
    headers_str = " | ".join(table.headers)
    stdscr.addstr(2, 0, headers_str[:width-1], curses.A_UNDERLINE)
    
    row_idx = 3
    for row in table.rows:
        if row_idx >= height - 2:
            break
        r_start = row.range_start
        r_end = row.range_end
        range_disp = f"{r_start}" if r_start == r_end else f"{r_start}-{r_end}"
        full_row = [range_disp] + row.content
        line_str = " | ".join(full_row)
        stdscr.addstr(row_idx, 0, line_str[:width-1])
        row_idx += 1
        
    stdscr.addstr(height-1, 0, "Press any key to return...", curses.A_REVERSE)
    stdscr.refresh()
    stdscr.getch()


def query_table_view(stdscr, table: Table):
    """View to query a specific table."""
    # Simple query mode: Input loop
    curses.echo()
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        title = f"Query Table: {table.name}"
        stdscr.addstr(0, 0, title, curses.A_BOLD)
        
        min_val, max_val = table.get_range_bounds()
        prompt = f"Enter dice roll ({min_val}-{max_val}) or 'q' to quit: "
        stdscr.addstr(2, 0, prompt)
        
        stdscr.refresh()
        
        try:
            # Get input string
            user_input_bytes = stdscr.getstr(2, len(prompt))
            user_input = user_input_bytes.decode('utf-8').strip()
        except curses.error:
            continue
            
        if user_input.lower() == 'q':
            break
            
        result_text = []
        try:
            value = int(user_input)
            row = table.query(value)
            
            if row:
                headers = " | ".join(table.headers)
                result_text.append(headers)
                result_text.append("-" * len(headers))
                
                r_start = row.range_start
                r_end = row.range_end
                range_disp = f"{r_start}" if r_start == r_end else f"{r_start}-{r_end}"
                full_row = [range_disp] + row.content
                result_text.append(" | ".join(full_row))
            else:
                result_text.append("No match found.")
                
        except ValueError:
            result_text.append("Invalid input. Integers only.")
            
        # Show result
        y_off = 4
        for line in result_text:
            stdscr.addstr(y_off, 0, line[:width-1])
            y_off += 1
            
        stdscr.addstr(height-1, 0, "Press any key to continue...", curses.A_REVERSE)
        curses.noecho()
        stdscr.getch()
        curses.echo()

    curses.noecho()


def load_logo_lines(logo_path: str = None) -> List[str]:
    """Load logo lines from file."""
    if logo_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, 'resources', 'logo.ascii.txt')
    
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except Exception as e:
            g_logger.warning(f"Failed to load logo from {logo_path}: {e}")
    return []


def run_tui(stdscr, root_dir: TableDirectory, logo_path: str = None, theme_path: str = None):
    """Main TUI Entry point."""
    # Settings
    curses.curs_set(0) # Hide cursor
    stdscr.keypad(True) # Enable special keys
    
    # Load and apply theme
    theme = load_theme(theme_path)
    init_color_pairs(theme)
    use_colors = curses.has_colors()
        
    current_dir = root_dir
    selected_idx = 0
    path_stack = [root_dir.name]
    logo_lines = load_logo_lines(logo_path)
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Get Items
        items = get_items_for_dir(current_dir)
        
        # Ensure selection is valid
        if selected_idx >= len(items):
            selected_idx = len(items) - 1
        if selected_idx < 0:
            selected_idx = 0
            
        # Draw Logo
        logo_y = 0
        if logo_lines:
            for line in logo_lines[:min(len(logo_lines), height // 3)]:
                try:
                    attr = curses.A_BOLD
                    if curses.has_colors():
                        attr = curses.color_pair(3) | curses.A_BOLD
                    stdscr.addstr(logo_y, 0, line[:width-1], attr)
                except curses.error:
                    pass
                logo_y += 1
            logo_y += 1  # Extra spacing
        
        # Draw Header
        header = f"Browsing: {'/'.join(path_stack)}"
        stdscr.addstr(logo_y, 0, header, curses.A_BOLD)
        logo_y += 1
        
        # Draw List
        max_display_items = height - logo_y - 2  # Adjust for logo, header, and status bar
        start_idx = 0
        if selected_idx >= max_display_items:
            start_idx = selected_idx - max_display_items + 1
            
        list_y = logo_y
        for i in range(start_idx, min(len(items), start_idx + max_display_items)):
            name, type_, obj = items[i]
            
            display_str = name
            attr = curses.A_NORMAL
            
            if type_ == "DIR" or type_ == "DIR_UP":
                display_str = f"[{name}]"
                if curses.has_colors():
                    attr = curses.color_pair(1)
            elif type_ == "TABLE":
                display_str = f"{name}"
                if curses.has_colors():
                    attr = curses.color_pair(2)
            
            if i == selected_idx:
                attr |= curses.A_REVERSE
                
            try:
                stdscr.addstr(list_y, 0, display_str[:width-1], attr)
            except curses.error:
                pass
            list_y += 1
            
        # Draw Status Bar
        selected_obj_name = "None"
        if items:
            selected_obj_name = items[selected_idx][0]
            
        draw_status_bar(stdscr, "/".join(path_stack), selected_obj_name, width, use_colors)
        
        stdscr.refresh()
        
        # Input Handling
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected_idx = max(0, selected_idx - 1)
        elif key == curses.KEY_DOWN:
            selected_idx = min(len(items) - 1, selected_idx + 1)
        elif key == ord('q'):
            break
        elif key == ord('d'):
            if items:
                _, type_, obj = items[selected_idx]
                if type_ == "TABLE":
                    dump_table_view(stdscr, obj)
        elif key == ord('\n') or key == curses.KEY_ENTER:
            if items:
                name, type_, obj = items[selected_idx]
                
                if type_ == "DIR_UP":
                    # Go up
                    if current_dir.parent:
                        current_dir = current_dir.parent
                        path_stack.pop()
                        selected_idx = 0
                elif type_ == "DIR":
                    # Go down
                    current_dir = obj
                    path_stack.append(name)
                    selected_idx = 0
                elif type_ == "TABLE":
                    # Query Table
                    query_table_view(stdscr, obj)
