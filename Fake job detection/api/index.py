import os
import sys
from pathlib import Path

# Add project root directory to Python path
basedir = Path(__file__).resolve().parent.parent
if str(basedir) not in sys.path:
    sys.path.insert(0, str(basedir))

from app import create_app

app = create_app('production' if os.environ.get('VERCEL') else 'development')

