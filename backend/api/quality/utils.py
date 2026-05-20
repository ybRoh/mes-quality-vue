"""
Quality API utility functions
"""

import re


def escape_like(s: str) -> str:
    """Escape special characters for SQL LIKE/ILIKE patterns."""
    return re.sub(r'([%_\\])', r'\\\1', s)
