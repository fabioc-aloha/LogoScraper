@description('The environment name. This should be a short identifier like dev, test, prod')
param environmentName string

@description('Primary region for all resources')
param location string = 'eastus2'

@description('Storage account name')
param storageAccountName string

@description('CDN profile name')
param cdnProfileName string

@description('Computer Vision service name')
param computerVisionName string

@description('Key Vault name')
param keyVaultName string

@description('Managed Identity name')
param managedIdentityName string

// Tags that should be applied to all resources.
var tags = {
  'azd-env-name': environmentName
  environment: environmentName
  application: 'logo-scraper'
}

// Storage account for logos
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: ['AzureServices']
    }
    supportsHttpsTrafficOnly: true
  }
}

// Create a blob service
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

// Create a container for logos
resource logoContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'logos'
  properties: {
    publicAccess: 'None'
  }
}

// Create a container for temp files
resource tempContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'temp'
  properties: {
    publicAccess: 'None'
  }
}

// CDN profile for fast logo delivery
resource cdnProfile 'Microsoft.Cdn/profiles@2023-05-01' = {
  name: cdnProfileName
  location: location
  tags: tags
  sku: {
    name: 'Standard_Microsoft'
  }
}

// CDN endpoint
resource cdnEndpoint 'Microsoft.Cdn/profiles/endpoints@2023-05-01' = {
  parent: cdnProfile
  name: 'logos'
  location: location
  tags: tags
  properties: {
    originHostHeader: '${storageAccount.name}.blob.core.windows.net'
    isHttpAllowed: false
    isHttpsAllowed: true
    queryStringCachingBehavior: 'IgnoreQueryString'
    contentTypesToCompress: [
      'image/png'
      'image/jpeg'
      'image/gif'
    ]
    isCompressionEnabled: true
    origins: [
      {
        name: 'storage'
        properties: {
          hostName: '${storageAccount.name}.blob.core.windows.net'
          originHostHeader: '${storageAccount.name}.blob.core.windows.net'
          priority: 1
          weight: 1000
          enabled: true
        }
      }
    ]
  }
}

// Computer Vision service for logo analysis
resource computerVision 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: computerVisionName
  location: location
  tags: tags
  sku: {
    name: 'S1'
  }
  kind: 'ComputerVision'
  properties: {
    customSubDomainName: computerVisionName
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
  }
}

// User assigned managed identity for secure access
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: tags
}

// Assign Storage Blob Data Contributor role to managed identity
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, managedIdentity.id, 'storage-contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Key Vault for storing secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
  }
}

// Grant managed identity access to Key Vault
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, managedIdentity.id, 'keyvault-secrets')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Store computer vision key in Key Vault
resource cognitiveServiceKey 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'CognitiveServiceKey'
  properties: {
    value: computerVision.listKeys().key1
  }
}

// Store storage connection string in Key Vault
resource storageConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'StorageConnectionString'
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
  }
}

// Outputs
output STORAGE_ACCOUNT_NAME string = storageAccount.name
output COMPUTER_VISION_ENDPOINT string = computerVision.properties.endpoint
output CDN_ENDPOINT string = 'https://${cdnEndpoint.properties.hostName}'
output MANAGED_IDENTITY_CLIENT_ID string = managedIdentity.properties.clientId
output KEY_VAULT_NAME string = keyVault.name
output KEY_VAULT_ENDPOINT string = keyVault.properties.vaultUri
