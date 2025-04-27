############################################
# variables.tf - Input variables definition
############################################

variable "prefix" {
  description = "Prefix for all resources to ensure uniqueness"
  type        = string
  default     = "databricks"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "westeurope"
}

variable "resource_group_name" {
  description = "Name of the resource group to create"
  type        = string
  default     = "databricks-rg"
}

variable "databricks_workspace_name" {
  description = "Name of the Databricks workspace"
  type        = string
  default     = "databricks-workspace"
}

variable "unity_catalog_name" {
  description = "Name of the Unity Catalog metastore"
  type        = string
  default     = "primary-metastore"
}

variable "key_vault_name" {
  description = "Name of the Azure Key Vault for storing secrets"
  type        = string
  default     = "databricks-kv"
}

variable "managed_identity_name" {
  description = "Name of the managed identity for Databricks"
  type        = string
  default     = "databricks-mi"
}

variable "service_principal_display_name" {
  description = "Display name for the Databricks service principal"
  type        = string
  default     = "Databricks Service Principal"
}

variable "external_storage_account_id" {
  description = "Resource ID of the external storage account to grant access to"
  type        = string
  # No default - this must be provided by the user
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "Development"
    Project     = "Databricks"
    Terraform   = "true"
  }
}