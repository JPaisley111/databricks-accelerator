"""
Control table operations for tracking watermarks in incremental data processing.
"""

from pyspark.sql import functions as F
from ..config import spark, get_control_table_path

def initialize_control_table():
    """
    Ensure the control table exists (create if not exists).
    The control table tracks the latest processed timestamp per entity.
    """
    control_table_path = get_control_table_path()
    
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS incremental_control (
          entity STRING, 
          last_watermark TIMESTAMP
        )
        USING delta 
        LOCATION '{control_table_path}'
    """)

def get_last_watermark(entity: str):
    """
    Retrieve the last processed timestamp for the given entity from the control table.
    If no record is found (first run for this entity), returns a minimal timestamp.
    
    Args:
        entity: The name of the entity/table for which to retrieve the watermark
        
    Returns:
        Timestamp of last processed data for this entity
    """
    # Ensure control table exists
    initialize_control_table()
    
    # Query the control table for this entity
    result = spark.sql(f"SELECT last_watermark FROM incremental_control WHERE entity = '{entity}'").collect()
    if result:
        return result[0]['last_watermark']
    else:
        # If no watermark exists, return a timestamp epoch (or None to indicate full load).
        # Here we use 1970-01-01 as a default "zero" timestamp.
        return "1970-01-01T00:00:00Z"

def update_watermark(entity: str, new_watermark):
    """
    Update the control table with the new watermark for the given entity.
    If the entity exists, update its timestamp; if not, insert a new record.
    
    Args:
        entity: The name of the entity/table to update
        new_watermark: The new watermark timestamp to set
    """
    # Ensure control table exists
    initialize_control_table()
    
    # Convert watermark to a string in case it's a datetime object (for safe SQL insertion)
    watermark_str = new_watermark if isinstance(new_watermark, str) else str(new_watermark)
    
    # Use MERGE for upsert (ensures idempotent update or insert)
    spark.sql(f"""
        MERGE INTO incremental_control AS ctrl
        USING (SELECT '{entity}' AS entity, TIMESTAMP('{watermark_str}') AS last_watermark) AS upd
        ON ctrl.entity = upd.entity
        WHEN MATCHED THEN 
            UPDATE SET ctrl.last_watermark = upd.last_watermark
        WHEN NOT MATCHED THEN 
            INSERT (entity, last_watermark) VALUES (upd.entity, upd.last_watermark)
    """)
    # Note: We cast the string to TIMESTAMP in SQL to ensure proper type