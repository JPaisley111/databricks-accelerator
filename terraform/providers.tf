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

# Configure the Databricks provider - this is configured after workspace creation 
# using the workspace URL and Azure AD token for authentication
provider "databricks" {
  host = module.databricks_workspace.workspace_url
  azure_client_id             = azurerm_user_assigned_identity.databricks_mi.client_id
  azure_client_secret         = azurerm_user_assigned_identity.databricks_mi.client_secret
  azure_tenant_id             = data.azurerm_client_config.current.tenant_id
}