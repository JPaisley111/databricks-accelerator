"""
Data layer package for ETL operations.
"""

from .control_table import get_last_watermark, update_watermark, initialize_control_table

__all__ = [
    'get_last_watermark',
    'update_watermark',
    'initialize_control_table'
]