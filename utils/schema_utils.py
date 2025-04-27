"""
Schema utility functions for handling data schemas in ETL processes.
"""

import json
from pyspark.sql.types import StructType
from ..config import spark, get_storage_config

def load_schema_definition(entity_name: str):
    """
    Load schema definition for the given entity from a schema file (if exists).
    Returns a Spark StructType object or None if no predefined schema is available.
    
    Args:
        entity_name: The name of the entity/table for which to load the schema
        
    Returns:
        StructType object if schema is found, None otherwise
    """
    storage_config = get_storage_config()
    raw_data_path = storage_config["raw_data_path"]
    
    try:
        schema_file_path = f"{raw_data_path}/schemas/{entity_name}_schema.json"  # Example schema path
        schema_json = spark.read.text(schema_file_path).collect()[0][0]
        schema_dict = json.loads(schema_json)
        return StructType.fromJson(schema_dict)
    except Exception as e:
        # If schema file not found or invalid, return None to allow schema inference
        return None