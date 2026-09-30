import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pelicanconf import *  # noqa: F401, F403

SITEURL = "https://perlmsu.github.io"
RELATIVE_URLS = False
DELETE_OUTPUT_DIRECTORY = True
