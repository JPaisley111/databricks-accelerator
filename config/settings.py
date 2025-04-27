"""
Configuration settings module for Databricks ETL pipelines.
Contains all environment variables, Azure storage settings, and Spark configurations.
"""

import os
from pyspark.sql import SparkSession

def get_spark_session():
    """
    Initialize and return the global SparkSession.
    """
    return SparkSession.builder.getOrCreate()

# Initialize SparkSession as a module-level variable for reuse
spark = get_spark_session()

# Retrieve sensitive configs from environment or Databricks secrets
def get_credentials():
    """
    Get all necessary credentials from environment variables or Databricks secrets.
    """
    # Replace "my_scope" and key names with your secret scope and keys
    client_id = os.getenv("AZURE_CLIENT_ID") or dbutils.secrets.get("my_scope", "sp_client_id")
    tenant_id = os.getenv("AZURE_TENANT_ID") or dbutils.secrets.get("my_scope", "sp_tenant_id")
    client_secret = os.getenv("AZURE_CLIENT_SECRET") or dbutils.secrets.get("my_scope", "sp_client_secret")
    
    return {
        "client_id": client_id,
        "tenant_id": tenant_id,
        "client_secret": client_secret
    }

def get_storage_config():
    """
    Get storage account configuration for Azure Data Lake Storage.
    """
    # Retrieve storage account and container names
    storage_account = os.getenv("STORAGE_ACCOUNT") or dbutils.secrets.get("my_scope", "storage_account_name")
    raw_container = os.getenv("RAW_CONTAINER") or dbutils.secrets.get("my_scope", "raw_container_name")
    silver_container = os.getenv("SILVER_CONTAINER") or dbutils.secrets.get("my_scope", "silver_container_name")
    
    # Construct base paths for raw and processed (silver) data
    raw_data_path = f"abfss://{raw_container}@{storage_account}.dfs.core.windows.net"
    silver_data_path = f"abfss://{silver_container}@{storage_account}.dfs.core.windows.net"
    
    return {
        "storage_account": storage_account,
        "raw_container": raw_container,
        "silver_container": silver_container,
        "raw_data_path": raw_data_path,
        "silver_data_path": silver_data_path
    }

def configure_spark():
    """
    Configure Spark with all necessary settings for Azure Data Lake access.
    """
    # Get credentials and storage config
    creds = get_credentials()
    storage_config = get_storage_config()
    
    storage_account = storage_config["storage_account"]
    
    # Set Spark config for Azure ADLS Gen2 access via OAuth (Service Principal credentials)
    spark.conf.set(f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net", "OAuth")
    spark.conf.set(f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net", 
                "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
    spark.conf.set(f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net", 
                creds["client_id"])
    spark.conf.set(f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net", 
                creds["client_secret"])
    spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net", 
                f"https://login.microsoftonline.com/{creds['tenant_id']}/oauth2/token")
    
    # Enable automatic schema evolution for Delta (so new columns in source data are added to the Delta table)
    spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")

# Control table settings
def get_control_table_path():
    """
    Get the path to the control table used for tracking watermarks.
    """
    storage_config = get_storage_config()
    return f"{storage_config['silver_data_path']}/_control_table"