############################################
# outputs.tf - Output values
############################################

output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.this.name
}

output "databricks_workspace_url" {
  description = "The URL of the Databricks workspace"
  value       = "https://${azurerm_databricks_workspace.this.workspace_url}"
}

output "databricks_workspace_id" {
  description = "The ID of the Databricks workspace"
  value       = azurerm_databricks_workspace.this.id
}

output "key_vault_name" {
  description = "The name of the Azure Key Vault"
  value       = azurerm_key_vault.this.name
}

output "key_vault_id" {
  description = "The ID of the Azure Key Vault"
  value       = azurerm_key_vault.this.id
}

output "managed_identity_name" {
  description = "The name of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.databricks_mi.name
}

output "managed_identity_id" {
  description = "The ID of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.databricks_mi.id
}

output "managed_identity_client_id" {
  description = "The client ID of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.databricks_mi.client_id
}

output "managed_identity_principal_id" {
  description = "The principal ID of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.databricks_mi.principal_id
}

output "unity_catalog_metastore_id" {
  description = "The ID of the Unity Catalog metastore"
  value       = databricks_metastore.this.id
}

output "unity_catalog_storage_account" {
  description = "The name of the storage account for Unity Catalog"
  value       = azurerm_storage_account.unity_catalog.name
}

output "databricks_service_principal_id" {
  description = "The ID of the Databricks service principal"
  value       = databricks_service_principal.this.id
}