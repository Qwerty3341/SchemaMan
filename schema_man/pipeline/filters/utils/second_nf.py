"""
Second normal form algorithm detecter

Requirements
    1. The table must be in first normal form.
    2. If the primary key is simple (a single column), the table automatically satisfies second normal form.
    3. If the primary key is composite, look for attributes that depend on only part of the key. Those columns must be moved to a separate table.
"""

from collections import defaultdict
from itertools import combinations
import re

from .alerts import Alert, AlertColor
from .table_classes import Table


