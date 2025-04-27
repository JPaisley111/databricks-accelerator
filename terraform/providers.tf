############################################
# providers.tf - Provider configuration
############################################

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.18.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

# Initial empty provider for Databricks
provider "databricks" {}

# Configure the Databricks provider with workspace after creation
provider "databricks" {
  alias = "created_workspace"
  host = azurerm_databricks_workspace.this.workspace_url
  azure_client_id = azurerm_user_assigned_identity.databricks_mi.client_id
  azure_tenant_id = data.azurerm_client_config.current.tenant_id
}