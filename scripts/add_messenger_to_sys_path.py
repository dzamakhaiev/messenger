"""
That module adds /messenger directory to system PATH
that allows to find needed packages in this repository.
"""

import os
import sys

current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, repo_dir)
