"""Build the static reader and its portable single-file edition."""
from pathlib import Path
import runpy
import sys

if '--publish' not in sys.argv:
    sys.argv.append('--publish')
runpy.run_path(str(Path(__file__).with_name('build-book.py')), run_name='__main__')
