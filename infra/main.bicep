targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('The image name for the API service')
param apiImageName string = ''

@description('Id of the user or app to assign application roles')
param principalId string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'


// Store secrets in a keyvault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}-vault'
    location: location
    tags: tags
    principalId: principalId
  }
}

// Container apps host (including container registry)
module containerApps 'core/host/container-apps.bicep' = {
  name: 'container-apps'
  scope: resourceGroup
  params: {
    name: 'app'
    location: location
    tags: tags
    containerAppsEnvironmentName: '${prefix}-containerapps-env'
    containerRegistryName: '${replace(prefix, '-', '')}registry'
    logAnalyticsWorkspaceName: logAnalyticsWorkspace.outputs.name
  }
}

// CDN in front
module cdn 'core/networking/cdn.bicep' = {
  name: 'cdn'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    cdnProfileName: '${prefix}-cdn-profile'
    cdnEndpointName: '${prefix}-cdn-endpoint'
    originUrl: last(split(api.outputs.appUri, '//'))
    deliveryPolicyRules: [
      {
        name: 'Global'
        order: 0
        actions: [
          {
            name: 'CacheExpiration'
            parameters: {
                cacheBehavior: 'SetIfMissing'
                cacheType: 'All'
                cacheDuration: '00:05:00'
                typeName: 'DeliveryRuleCacheExpirationActionParameters'
            }
          }
        ]
      }
      {
        name: 'images'
        order: 1
        conditions: [
          {
            name: 'UrlPath'
            parameters: {
                operator: 'BeginsWith'
                negateCondition: false
                matchValues: [
                  'charts/'
                ]
                transforms: ['Lowercase']
                typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
            }
          }
        ]
        actions: [
          {
            name: 'CacheExpiration'
            parameters: {
                cacheBehavior: 'Override'
                cacheType: 'All'
                cacheDuration: '7.00:00:00'
                typeName: 'DeliveryRuleCacheExpirationActionParameters'
            }
          }
        ]
      }
    ]
  }
}

// API on ACA
module api 'api.bicep' = {
  name: 'api'
  scope: resourceGroup
  params: {
    name: '${take(prefix,19)}-containerapp'
    location: location
    tags: tags
    imageName: apiImageName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    keyVaultName: keyVault.outputs.name
  }
}


module logAnalyticsWorkspace 'core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  scope: resourceGroup
  params: {
    name: '${prefix}-loganalytics'
    location: location
    tags: tags
  }
}


output AZURE_LOCATION string = location
output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_REGISTRY_NAME string = containerApps.outputs.registryName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApps.outputs.registryLoginServer
output SERVICE_API_IDENTITY_PRINCIPAL_ID string = api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
output SERVICE_API_NAME string = api.outputs.SERVICE_API_NAME
output SERVICE_API_ENDPOINTS array = [cdn.outputs.uri]
output SERVICE_API_IMAGE_NAME string = api.outputs.SERVICE_API_IMAGE_NAME
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
