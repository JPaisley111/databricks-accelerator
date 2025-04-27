"""
Databricks autoloader implementation for incremental data processing.
Uses autoloader functionality for streaming data ingestion.
"""

from pyspark.sql import functions as F
from pyspark.sql.streaming import Trigger
from delta.tables import DeltaTable

# Import from modular components
from config.settings import configure_spark, get_storage_config, spark
from data.control_table import initialize_control_table, get_last_watermark, update_watermark
from utils.file_utils import list_entities
from utils.schema_utils import load_schema_definition

def process_with_autoloader():
    """
    Main Autoloader ETL process:
    - Iterates through each entity
    - Uses autoloader to incrementally load data
    - Writes to Delta tables with schema evolution
    
    Uses autoloader's built-in checkpoint mechanism for incremental processing
    and the control table for tracking processed data.
    """
    # Apply Spark configurations for Azure storage access
    configure_spark()
    
    # Get storage configuration
    storage_config = get_storage_config()
    raw_data_path = storage_config["raw_data_path"]
    silver_data_path = storage_config["silver_data_path"]
    
    # Ensure control table exists
    initialize_control_table()
    
    # Get entities to process
    entities = list_entities()
    if not entities:
        print("No entities found to process. Please check the raw data path.")
        return

    for entity in entities:
        print(f"\nProcessing entity with Autoloader: {entity}")
        
        # Determine paths
        entity_input_path = f"{raw_data_path}/{entity}"
        delta_table_path = f"{silver_data_path}/{entity}"
        checkpoint_path = f"{silver_data_path}/_checkpoints/{entity}"
        
        # Get schema if available, otherwise Autoloader will infer it
        schema = load_schema_definition(entity)
        
        # Get the last watermark for reporting purposes
        last_watermark = get_last_watermark(entity)
        print(f"Last watermark for {entity}: {last_watermark}")
        
        try:
            # Configure Autoloader read stream
            stream_df = (
                spark.readStream
                .format("cloudFiles")
                .option("cloudFiles.format", "parquet")  # Adjust based on your file format
                .option("cloudFiles.schemaLocation", f"{checkpoint_path}/schema")
                .option("cloudFiles.inferColumnTypes", "true")
            )
            
            # Apply schema if available
            if schema:
                stream_df = stream_df.schema(schema)
            
            # Load the stream data
            stream_df = stream_df.load(entity_input_path)
            
            # Add processing_time for tracking
            stream_df = stream_df.withColumn("processing_time", F.current_timestamp())
            
            # Write to Delta table in append mode
            stream_writer = (
                stream_df.writeStream
                .format("delta")
                .option("checkpointLocation", f"{checkpoint_path}/data")
                .outputMode("append")
                .trigger(Trigger.Once())  # Process available data once and stop
                .option("mergeSchema", "true")  # Enable schema evolution
            )
            
            # Start the stream and wait for this batch to complete
            print(f"  - Starting Autoloader stream for {entity}...")
            query = stream_writer.start(delta_table_path)
            query.awaitTermination()
            
            # Update control table with last processed timestamp
            # For Autoloader, we can use the current timestamp as the watermark
            # since it processes all available files up to now
            current_time = spark.sql("SELECT current_timestamp() as ts").collect()[0]["ts"]
            update_watermark(entity, current_time)
            print(f"  - Watermark updated for {entity}: {current_time}")
            
            # Check if any data was processed in this run
            # This requires a separate read of the Delta table to check for new entries
            try:
                # Read the Delta table directly to check for processing_time
                delta_df = spark.read.format("delta").load(delta_table_path)
                if last_watermark != "1970-01-01T00:00:00Z":  # Not the first run
                    # Count records added since last run
                    if isinstance(last_watermark, str):
                        new_count = delta_df.filter(
                            F.col("processing_time") > F.to_timestamp(F.lit(last_watermark))
                        ).count()
                    else:
                        new_count = delta_df.filter(
                            F.col("processing_time") > last_watermark
                        ).count()
                    
                    print(f"  - Processed {new_count} new records for {entity}")
                else:
                    # First run, just count total
                    total_count = delta_df.count()
                    print(f"  - First run, processed {total_count} records for {entity}")
            except Exception as e:
                print(f"  - Could not count processed records: {e}")
            
            print(f"  - Autoloader processing complete for {entity}")
            
        except Exception as e:
            print(f"  - Error processing {entity} with Autoloader: {e}")
            continue

    print("\nAutoloader processing completed for all entities.")

if __name__ == "__main__":
    process_with_autoloader()
