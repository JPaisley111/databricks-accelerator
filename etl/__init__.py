"""
ETL package for data processing operations.
"""

from .extract_load import process_schema_files

__all__ = [
    'process_schema_files'
]