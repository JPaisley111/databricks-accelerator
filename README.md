# Databricks D365FO Synapse Link Accelerator

![Acrux Digital](https://www.acruxdigital.tech/_next/image?url=%2Flogo-light.png)

An accelerator to quickly get users up and running using Synapse Link by building D365FO entities back into raw tables in Databricks

[Visit Acrux Digital](https://acruxdigital.tech) | [LinkedIn](https://www.linkedin.com/company/acruxdigital-technology) | [Report Bug](https://github.com/JPaisley111/databricks-accelerator/issues) | [Request Feature](https://github.com/JPaisley111/databricks-accelerator/issues)

[![LinkedIn][linkedin-shield]][linkedin-url]
[![MIT License][license-shield]][license-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Issues][issues-shield]][issues-url]

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Deployment with Terraform](#quick-deployment-with-terraform)
  - [Terraform Prerequisites](#terraform-prerequisites)
  - [Terraform Deployment](#terraform-deployment)
  - [Terraform Outputs](#terraform-outputs)
  - [Terraform Configuration Options](#terraform-configuration-options)
- [Implementation Options](#implementation-options)
  - [Generic PySpark Implementation](#generic-pyspark-implementation)
  - [Databricks Auto Loader Implementation](#databricks-auto-loader-implementation)
- [Running on Databricks](#running-on-databricks)
  - [Using Databricks Notebooks](#using-databricks-notebooks)
  - [Scheduling with Databricks Jobs](#scheduling-with-databricks-jobs)
- [Quick Start Guide](#quick-start-guide)
  - [1. Databricks Secret Configuration](#1-databricks-secret-configuration)
  - [2. Control Table Creation](#2-control-table-creation)
  - [3. Run the Implementation](#3-run-the-implementation)
  - [4. Monitor and Manage](#4-monitor-and-manage)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Support](#support)
- [License](#license)
- [Contact](#contact)

## Overview

The accelerator automates the process of:
1. Connecting to Synapse Link for D365FO
2. Retrieving entity data 
3. Converting the data into Databricks Delta tables
4. Setting up an automated pipeline for data refresh

This accelerator provides two different implementation options to suit different environments and requirements:
- **Generic PySpark Implementation** (main.py): A more portable implementation that can be adapted for different Spark platforms
- **Databricks Auto Loader Implementation** (autoloader.py): An implementation that leverages Databricks-specific features for optimized performance

## Prerequisites

- Azure Databricks workspace
- Synapse Link for D365FO configured in your Azure environment
- Appropriate permissions to create secrets and tables in Databricks

## Quick Deployment with Terraform

This accelerator includes Terraform scripts to quickly set up a complete Databricks environment including:

- A new Databricks workspace on Azure
- Unity Catalog metastore configuration
- Azure Key Vault for storing secrets
- Managed identity for accessing external storage accounts
- Proper role assignments for secure access

### Terraform Prerequisites

Before you begin deployment, ensure you have:

1. **Terraform installed** (v1.3.0 or later)
   ```bash
   terraform -v
   ```

2. **Azure CLI installed and authenticated**
   ```bash
   az login
   az account set --subscription "Your Subscription Name"
   ```

3. **An existing Azure Storage Account** to grant access to (or create one first)

### Terraform Deployment

1. **Navigate to the terraform directory**
   ```bash
   cd terraform
   ```

2. **Initialize Terraform**
   ```bash
   terraform init
   ```

3. **Review the deployment plan**
   ```bash
   terraform plan -var="external_storage_account_id=/subscriptions/your-subscription-id/resourceGroups/your-rg/providers/Microsoft.Storage/storageAccounts/your-storage"
   ```

4. **Deploy the infrastructure**
   ```bash
   terraform apply -var="external_storage_account_id=/subscriptions/your-subscription-id/resourceGroups/your-rg/providers/Microsoft.Storage/storageAccounts/your-storage"
   ```

5. **Confirm the deployment** when prompted by typing `yes`

The deployment process typically takes 10-15 minutes to complete.

### Terraform Outputs

After successful deployment, Terraform will output important information:

- **Databricks Workspace URL**: Use this to access your new workspace
- **Key Vault Name**: Reference for storing and retrieving secrets
- **Managed Identity Details**: Used for connecting to external storage
- **Unity Catalog Information**: Metastore ID and storage account

Example usage of the outputs:
```bash
# Access your new Databricks workspace
echo "Open the Databricks workspace at: $(terraform output -raw databricks_workspace_url)"

# Get the managed identity client ID for authentication
echo "Managed Identity Client ID: $(terraform output -raw managed_identity_client_id)"
```

### Terraform Configuration Options

You can customize your deployment by modifying the variables in `variables.tf` or by passing values at runtime:

```bash
terraform apply \
  -var="location=eastus" \
  -var="databricks_workspace_name=my-workspace" \
  -var="unity_catalog_name=my-metastore" \
  -var="external_storage_account_id=/subscriptions/your-subscription-id/resourceGroups/your-rg/providers/Microsoft.Storage/storageAccounts/your-storage"
```

## Implementation Options

The accelerator provides two different implementation approaches to meet different requirements:

### Generic PySpark Implementation

The `main.py` implementation uses standard PySpark functionality to read, transform, and write data incrementally. This approach:

- Is more portable and can be adapted for non-Databricks Spark environments
- Uses standard Spark DataFrame operations
- Manually tracks watermarks for incremental processing
- Requires customization of environment variables for non-Databricks platforms

### Databricks Auto Loader Implementation

The `autoloader.py` implementation leverages Databricks-specific Auto Loader functionality for optimized performance. This approach:

- Uses Databricks Auto Loader via the cloudFiles format
- Automatically discovers and processes new files
- Provides built-in checkpointing and fault tolerance
- Optimizes for Databricks with automatic schema inference and evolution
- Is Databricks-specific and not portable to other platforms

**Which implementation should you choose?**

- Choose the Generic PySpark implementation if you need a more portable solution or plan to adapt the code for other Spark platforms
- Choose the Databricks Auto Loader implementation if you're committed to Databricks and want to leverage its performance optimisations and Auto Loader capabilities

## Running on Databricks

In the Databricks environment, you'll need to run these implementations as notebooks or schedule them as jobs rather than executing them directly as Python scripts.

### Using Databricks Notebooks

#### Converting Python Files to Notebooks

1. **Import the Python files as notebooks**:
   ```bash
   databricks workspace import /local/path/main.py /path/to/notebook/main
   databricks workspace import /local/path/autoloader.py /path/to/notebook/autoloader
   ```

   Alternatively, you can create new notebooks in the Databricks UI and copy the code from the Python files.

2. **For the Generic PySpark Notebook**:
   - Create a new notebook named `main_notebook`
   - Add the following content to the notebook:

   ```python
   # Import the main processing function
   from main import process_schema_files
   
   # Execute the main processing function
   process_schema_files()
   ```

3. **For the Auto Loader Notebook**:
   - Create a new notebook named `autoloader_notebook`
   - Add the following content to the notebook:

   ```python
   # Import the Auto Loader processing function
   from autoloader import process_with_autoloader
   
   # Execute the Auto Loader processing function
   process_with_autoloader()
   ```

#### Running Notebooks Manually

To run a notebook manually:

1. Navigate to the notebook in the Databricks workspace
2. Select an appropriate cluster from the dropdown menu
3. Click the "Run All" button at the top of the notebook

### Scheduling with Databricks Jobs

You can schedule your implementation to run automatically using Databricks Jobs via the UI or CLI.

#### Using the Databricks UI

1. Navigate to the Jobs tab in your Databricks workspace
2. Click the "Create Job" button
3. Set a name for your job
4. Add a task:
   - Select "Notebook" as the task type
   - Choose your implementation notebook
   - Select a cluster configuration
5. Set a schedule using the Schedule tab
6. Click "Create" to save the job

#### Using the Databricks CLI

This accelerator includes two YAML configuration files (`incremental_load.yaml` and `autoloader.yaml`) that define job configurations for both implementation approaches.

> **Important Note**: Before creating jobs, you must update the notebook paths in both YAML files to match your workspace environment. Look for the `notebook_path` property in each YAML file and update it with the correct path where you've imported or created your notebooks.

1. Install the Databricks CLI if you haven't already:
   ```bash
   pip install databricks-cli
   ```

2. Configure authentication:
   ```bash
   databricks configure --token
   ```

3. Create the jobs using the provided YAML files:
   ```bash
   # For the Generic PySpark Implementation
   databricks jobs create --json-file <(yq eval -j incremental_load.yaml)
   
   # For the Auto Loader Implementation  
   databricks jobs create --json-file <(yq eval -j autoloader.yaml)
   ```
   
   Note: The above command uses `yq` to convert YAML to JSON. If you don't have `yq` installed, you can install it with:
   ```bash
   brew install yq
   ```
   
   Alternatively, you can use any YAML to JSON converter before creating the job.

4. To trigger a job run immediately:
   ```bash
   databricks jobs run-now --job-id <job-id>
   ```

## Quick Start Guide

### 1. Databricks Secret Configuration

First, you need to set up secrets in Databricks to securely store your connection information:

1. Navigate to your Databricks workspace
2. Go to "Secrets" in the left sidebar
3. Create a new secret scope named "synapse_link"
4. Add the following secrets:

   | Secret Name | Description |
   |-------------|-------------|
   | `synapse_link_uri` | Your Synapse Link endpoint URI |
   | `synapse_link_key` | Your Synapse Link access key |
   | `tenant_id` | Your Azure AD tenant ID |
   | `client_id` | Your Azure AD application (client) ID |
   | `client_secret` | Your Azure AD application secret |

You can use the following commands in Databricks CLI to create these secrets:

```bash
databricks secrets create-scope --scope synapse_link
databricks secrets put --scope synapse_link --key synapse_link_uri
databricks secrets put --scope synapse_link --key synapse_link_key
databricks secrets put --scope synapse_link --key tenant_id
databricks secrets put --scope synapse_link --key client_id
databricks secrets put --scope synapse_link --key client_secret
```

### 2. Control Table Creation

Create a control table to manage entity configurations:

1. Run the following SQL in a Databricks SQL cell:

```sql
CREATE TABLE IF NOT EXISTS d365fo_entity_control (
  entity_name STRING,
  target_schema STRING,
  target_table STRING,
  refresh_frequency STRING,
  last_processed_timestamp TIMESTAMP,
  is_active BOOLEAN,
  incremental_load BOOLEAN,
  incremental_field STRING
);

-- Add some initial entities to process
INSERT INTO d365fo_entity_control VALUES
('GeneralJournalAccountEntries', 'finance', 'general_journal_entries', 'daily', null, true, true, 'MODIFIEDDATETIME'),
('LedgerJournalTrans', 'finance', 'ledger_journal_transactions', 'daily', null, true, true, 'MODIFIEDDATETIME'),
('CustTable', 'customers', 'customer_master', 'daily', null, true, false, null);
```

Customize the inserted entities based on your specific D365FO entities of interest.

### 3. Run the Implementation

After setting up the control table, you can run either implementation:

#### Generic PySpark Implementation

1. Open or import the `main.py` file as a notebook in your Databricks workspace
2. Configure a cluster with appropriate settings
3. Run the notebook to process all configured entities

#### Auto Loader Implementation

1. Open or import the `autoloader.py` file as a notebook in your Databricks workspace
2. Configure a cluster with appropriate settings
3. Run the notebook to process all configured entities using Auto Loader

Both implementations will:
- Connect to your D365FO environment via Synapse Link
- Process each entity defined in the control table
- Create or update Delta tables with the latest data

### 4. Monitor and Manage

- Check the execution logs within the notebook for any errors
- View the created Delta tables in the specified schemas
- Monitor the scheduled jobs in the Databricks Jobs UI

## Advanced Configuration

### Incremental Loading

For entities with high volumes of data, enable incremental loading by:
1. Setting `incremental_load` to `true` in the control table
2. Specifying the timestamp field to use (typically `MODIFIEDDATETIME`) in `incremental_field`

### Customizing Schema Mapping

You can modify the notebook to implement custom column mappings or transformations for specific entities.

### Scheduling Options

The default schedule is based on the `refresh_frequency` column in the control table. Options include:
- `hourly`
- `daily`
- `weekly`
- `monthly`

## Troubleshooting

Common issues and their solutions:

1. **Authentication Errors**: Verify your secret values and permissions
2. **Missing Entities**: Ensure the entity exists in D365FO and is enabled for Synapse Link
3. **Processing Failures**: Check the error logs and verify entity structure matches expectations

## Support

For assistance with this accelerator, please open an issue or visit [our website](https://acruxdigital.tech) for commercial enquiries. 

## License

This accelerator is provided as-is under the MIT License. See `LICENSE` for more information.

## Contact

Acrux Digital - [https://acruxdigital.tech](https://acruxdigital.tech)

Project Link: [https://github.com/JPaisley111/databricks-accelerator](https://github.com/JPaisley111/databricks-accelerator)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/JPaisley111/databricks-accelerator.svg?style=for-the-badge
[contributors-url]: https://github.com/JPaisley111/databricks-accelerator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/JPaisley111/databricks-accelerator.svg?style=for-the-badge
[forks-url]: https://github.com/JPaisley111/databricks-accelerator/network/members
[issues-shield]: https://img.shields.io/github/issues/JPaisley111/databricks-accelerator.svg?style=for-the-badge
[issues-url]: https://github.com/JPaisley111/databricks-accelerator/issues
[license-shield]: https://img.shields.io/github/license/JPaisley111/databricks-accelerator.svg?style=for-the-badge
[license-url]: https://github.com/JPaisley111/databricks-accelerator/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=0077B5
[linkedin-url]: https://www.linkedin.com/company/acruxdigital/