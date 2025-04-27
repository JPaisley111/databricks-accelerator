"""
Main entry point for the Databricks ETL pipeline.
This approach uses PySpark to read, transform, and write data incrementally.
It is a generic pyspark implementation - 
Simply review environment variables if using a platform other than Databricks
"""

from pyspark.sql import SparkSession
from config.settings import configure_spark
from etl.extract_load import process_schema_files

def main():
    """
    Entry point for the ETL process.
    - Configures Spark with necessary settings
    - Runs the incremental ETL process
    """
    # Configure Spark with all necessary settings
    configure_spark()
    
    # Run the ETL process
    print("Starting incremental ETL process...")
    process_schema_files()
    print("ETL process completed.")

if __name__ == "__main__":
    main()