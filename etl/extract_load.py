"""
Core ETL logic for incremental data processing.
"""

from pyspark.sql import functions as F
from delta.tables import DeltaTable

from ..config import get_storage_config
from ..utils import list_entities, load_schema_definition
from ..data import get_last_watermark, update_watermark

def process_schema_files():
    """
    Main ETL process: 
    - Iterates through each entity
    - Reads incremental data using watermarks
    - Writes to Delta tables with schema evolution
    
    Uses a watermark from the control table to only process new or updated records.
    """
    # Get configuration
    storage_config = get_storage_config()
    raw_data_path = storage_config["raw_data_path"]
    silver_data_path = storage_config["silver_data_path"]
    
    # Get entities to process
    entities = list_entities()
    if not entities:
        print("No entities found to process. Please check the raw data path.")
        return

    for entity in entities:
        print(f"\nProcessing entity: {entity}")
        
        # 1. Get the last processed timestamp for this entity
        last_watermark = get_last_watermark(entity)
        if last_watermark is None:
            last_watermark = "1970-01-01T00:00:00Z"  # default start (no data loaded yet)
        print(f"Last watermark for {entity}: {last_watermark}")

        # 2. Read raw data for the entity, filtering by last_watermark
        # Determine the input path for the entity's data
        entity_input_path = f"{raw_data_path}/{entity}"
        
        # Optionally get schema (if schema definitions are provided)
        schema = load_schema_definition(entity)
        
        try:
            # Read data based on whether schema is available
            if schema:
                df = spark.read.format("parquet").schema(schema).load(entity_input_path)
            else:
                # If no predefined schema, infer schema (assuming Parquet/JSON/CSV format)
                # Adjust format as needed (e.g., .format("csv").option("header","true") if CSV)
                df = spark.read.format("parquet").load(entity_input_path)
        except Exception as e:
            # If reading fails (e.g., no files), skip this entity
            print(f"  - Skipping {entity}, no data or read error: {e}")
            continue

        # 3. Apply incremental filter: only records with modification timestamp > last_watermark
        # Assuming the source data has a timestamp column named 'modified_at' (adjust if needed)
        if isinstance(last_watermark, str):
            # Convert string to timestamp literal that Spark can compare
            df_new = df.filter(F.col("modified_at") > F.to_timestamp(F.lit(last_watermark)))
        else:
            df_new = df.filter(F.col("modified_at") > last_watermark)

        # 4. Cache the new data DF to avoid redundant reads (we will use it multiple times)
        df_new.cache()
        new_count = df_new.count()  # Materialize cache & get count

        if new_count == 0:
            print(f"  - No new data for {entity} since last watermark.")
            df_new.unpersist()
            continue

        print(f"  - New records found for {entity}: {new_count}")

        # 5. Write the new data to Delta (append mode, with schema merge for new columns)
        # Use a Delta table path per entity under the silver container
        delta_table_path = f"{silver_data_path}/{entity}"
        
        (df_new.write.format("delta")
             .mode("append")
             .option("mergeSchema", "true")   # ensure new columns are merged
             .save(delta_table_path))
             
        print(f"  - Data written to Delta table for {entity} at {delta_table_path}")

        # 6. Compute new high watermark and update control table
        max_timestamp = df_new.agg(F.max(F.col("modified_at"))).collect()[0][0]
        update_watermark(entity, max_timestamp)
        print(f"  - Watermark updated for {entity}: {max_timestamp}")

        # 7. Cleanup cache
        df_new.unpersist()

    print("\nIncremental ETL processing completed for all entities.")