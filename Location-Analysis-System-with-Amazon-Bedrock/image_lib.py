"""
image_lib.py — thin wrapper that re-exports everything from shared/image_lib.py.
All logic lives in shared/image_lib.py to avoid duplication across projects.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.image_lib import *  # noqa: F401, F403
