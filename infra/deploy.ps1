#!/usr/bin/env pwsh
#Requires -Version 7.0

# Load configuration
$configPath = Join-Path $PSScriptRoot "infra_config.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Configuration file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

# Ensure az cli is installed and logged in
$null = az account show
if ($LASTEXITCODE -ne 0) {
    Write-Error "Please run 'az login' to connect to Azure first"
    exit 1
}

# Create or update resource group
$resourceGroupName = $config.resourceNames.resourceGroup
$location = $config.location
Write-Host "Ensuring resource group $resourceGroupName exists..."
$null = az group create --name $resourceGroupName --location $location

# Validate the deployment first
Write-Host "Validating deployment..."
$null = az deployment group what-if `
    --resource-group $resourceGroupName `
    --template-file main.bicep `
    --parameters environmentName=$($config.environment) `
    --parameters location=$($config.location) `
    --parameters storageAccountName=$($config.resourceNames.storageAccount) `
    --parameters cdnProfileName=$($config.resourceNames.cdnProfile) `
    --parameters computerVisionName=$($config.resourceNames.computerVision) `
    --parameters keyVaultName=$($config.resourceNames.keyVault) `
    --parameters managedIdentityName=$($config.resourceNames.managedIdentity)

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment validation failed"
    exit 1
}

# Ask for confirmation
$confirmation = Read-Host "Do you want to proceed with the deployment? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Deployment cancelled"
    exit 0
}

# Deploy the infrastructure
Write-Host "Deploying infrastructure..."
$deployment = az deployment group create `
    --resource-group $resourceGroupName `
    --template-file main.bicep `
    --parameters environmentName=$($config.environment) `
    --parameters location=$($config.location) `
    --parameters storageAccountName=$($config.resourceNames.storageAccount) `
    --parameters cdnProfileName=$($config.resourceNames.cdnProfile) `
    --parameters computerVisionName=$($config.resourceNames.computerVision) `
    --parameters keyVaultName=$($config.resourceNames.keyVault) `
    --parameters managedIdentityName=$($config.resourceNames.managedIdentity) `
    --query "properties.outputs" `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed"
    exit 1
}

# Output the deployment results
Write-Host "`nDeployment completed successfully! Here are your resource details:`n"
Write-Host "Storage Account Name: $($deployment.STORAGE_ACCOUNT_NAME.value)"
Write-Host "Computer Vision Endpoint: $($deployment.COMPUTER_VISION_ENDPOINT.value)"
Write-Host "CDN Endpoint: $($deployment.CDN_ENDPOINT.value)"
Write-Host "Managed Identity Client ID: $($deployment.MANAGED_IDENTITY_CLIENT_ID.value)"
Write-Host "Key Vault Name: $($deployment.KEY_VAULT_NAME.value)"
Write-Host "Key Vault Endpoint: $($deployment.KEY_VAULT_ENDPOINT.value)"

# Write the outputs to a configuration file
$azureConfig = @{
    STORAGE_ACCOUNT_NAME = $deployment.STORAGE_ACCOUNT_NAME.value
    COMPUTER_VISION_ENDPOINT = $deployment.COMPUTER_VISION_ENDPOINT.value
    CDN_ENDPOINT = $deployment.CDN_ENDPOINT.value
    MANAGED_IDENTITY_CLIENT_ID = $deployment.MANAGED_IDENTITY_CLIENT_ID.value
    KEY_VAULT_NAME = $deployment.KEY_VAULT_NAME.value
    KEY_VAULT_ENDPOINT = $deployment.KEY_VAULT_ENDPOINT.value
}

$azureConfigPath = Join-Path (Split-Path -Parent $PSScriptRoot) "azure_config.json"
$azureConfig | ConvertTo-Json | Set-Content -Path $azureConfigPath

Write-Host "`nConfiguration has been saved to: $azureConfigPath"