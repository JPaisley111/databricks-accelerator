"""
File system utility functions for ETL operations.
"""

from ..config import get_storage_config

def list_entities():
    """
    Discover all entities to process from the raw data container. 
    Returns a list of entity names (e.g., folder names in the raw data container).
    
    Returns:
        List of entity names as strings
    """
    storage_config = get_storage_config()
    raw_data_path = storage_config["raw_data_path"]
    
    entities = []
    try:
        for file_info in dbutils.fs.ls(raw_data_path):
            name = file_info.name.rstrip("/")  # remove trailing slash for directories
            if file_info.isDir() and name != "schemas":  # Exclude the schemas directory
                entities.append(name)
    except Exception as e:
        # Handle case where raw_data_path might be invalid or inaccessible
        print(f"Error listing entities in raw path: {e}")
    return entities