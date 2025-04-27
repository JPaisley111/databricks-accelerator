############################################
# main.tf - Main resource definitions
############################################

# Get current client configuration from AzureRM provider
data "azurerm_client_config" "current" {}

# Generate a random string for resource naming
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  resource_prefix = "${var.prefix}-${random_string.suffix.result}"
  resource_group_name = var.resource_group_name != "" ? var.resource_group_name : "${local.resource_prefix}-rg"
  tags = var.tags
}

# Create a resource group
resource "azurerm_resource_group" "this" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.tags
}

# Create an Azure Key Vault for storing Databricks secrets
resource "azurerm_key_vault" "this" {
  name                = "${var.key_vault_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  
  # Enable RBAC for accessing secrets (using Azure AD identities)
  enable_rbac_authorization = true
  
  # Configure network access - default to allow from trusted Microsoft services
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = []
  }
  
  tags = local.tags
}

# Create a user-assigned managed identity for Databricks
resource "azurerm_user_assigned_identity" "databricks_mi" {
  name                = "${var.managed_identity_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags
}

# Grant the managed identity access to the Key Vault
resource "azurerm_role_assignment" "keyvault_secrets_user" {
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.databricks_mi.principal_id
}

# Grant the managed identity Reader access to the external storage account
resource "azurerm_role_assignment" "storage_reader" {
  scope                = var.external_storage_account_id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.databricks_mi.principal_id
}

# Storage account for Unity Catalog metastore
resource "azurerm_storage_account" "unity_catalog" {
  name                     = "unitycat${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  tags                     = local.tags
}

# Container for Unity Catalog metastore
resource "azurerm_storage_container" "unity_catalog" {
  name                  = "metastore"
  storage_account_name  = azurerm_storage_account.unity_catalog.name
  container_access_type = "private"
}

# Grant the managed identity Storage Blob Data Contributor access to the Unity Catalog storage
resource "azurerm_role_assignment" "unity_storage_contributor" {
  scope                = azurerm_storage_account.unity_catalog.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.databricks_mi.principal_id
}

# Create a Databricks workspace
resource "azurerm_databricks_workspace" "this" {
  name                        = "${var.databricks_workspace_name}-${random_string.suffix.result}"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = "premium" # Required for Unity Catalog
  managed_resource_group_name = "${local.resource_prefix}-workspace-rg"
  tags                        = local.tags
  
  custom_parameters {
    no_public_ip        = true
    virtual_network_id  = azurerm_virtual_network.this.id
    public_subnet_name  = azurerm_subnet.public.name
    private_subnet_name = azurerm_subnet.private.name
  }
}

# Network setup for Databricks
resource "azurerm_virtual_network" "this" {
  name                = "${local.resource_prefix}-vnet"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "public" {
  name                 = "${local.resource_prefix}-public-subnet"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.1.0/24"]
  delegation {
    name = "databricks-delegation"
    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action",
      ]
    }
  }
}

resource "azurerm_subnet" "private" {
  name                 = "${local.resource_prefix}-private-subnet"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.2.0/24"]
  delegation {
    name = "databricks-delegation"
    service_delegation {
      name = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/unprepareNetworkPolicies/action",
      ]
    }
  }
}

# Create a service principal in the Databricks workspace
resource "databricks_service_principal" "this" {
  application_id = azurerm_user_assigned_identity.databricks_mi.client_id
  display_name   = var.service_principal_display_name
  
  # This depends_on is crucial to ensure the workspace is created first
  depends_on = [azurerm_databricks_workspace.this]
}

# Create a Unity Catalog metastore
resource "databricks_metastore" "this" {
  name = var.unity_catalog_name
  storage_root = "abfss://${azurerm_storage_container.unity_catalog.name}@${azurerm_storage_account.unity_catalog.name}.dfs.core.windows.net/"
  owner = "account users"
  
  depends_on = [
    azurerm_role_assignment.unity_storage_contributor,
    azurerm_databricks_workspace.this
  ]
}

# Assign the metastore to the workspace
resource "databricks_metastore_assignment" "this" {
  metastore_id = databricks_metastore.this.id
  workspace_id = azurerm_databricks_workspace.this.workspace_id
  
  depends_on = [
    databricks_metastore.this
  ]
}