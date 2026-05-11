"""
Libs.py — thin wrapper that re-exports everything from shared/libs.py.
All logic lives in shared/libs.py to avoid duplication across projects.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.libs import *  # noqa: F401, F403
