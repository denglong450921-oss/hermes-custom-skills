#!/usr/bin/env python3
"""
Convenience wrapper: adds prefixed IDs to elements WITHOUT existing IDs.
Delegates to add_html_ids.py with --preserve-existing flag.
Preserves ALL original IDs exactly as-is so CSS/JS references stay valid.
Usage: python3 add_ids_preserve_existing.py path/to/file.html [--prefix custom_]
"""
import sys, os, subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(script_dir, 'add_html_ids.py')

if not os.path.isfile(main_script):
    print(f"Error: add_html_ids.py not found at {main_script}", file=sys.stderr)
    sys.exit(1)

cmd = [sys.executable or 'python3', main_script] + sys.argv[1:] + ['--preserve-existing']
proc = subprocess.run(cmd)
sys.exit(proc.returncode)
