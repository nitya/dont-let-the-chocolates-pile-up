targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('azd environment name; used to name the resource group and resources.')
param environmentName string

@minLength(1)
@description('Azure region for all resources.')
param location string

@secure()
@description('Optional. When set, agents must send this key to submit drafts (MCP + REST).')
param mmWriteKey string = ''

@secure()
@description('Optional. When set, the studio (approve/reject) requires this key.')
param mmAdminKey string = ''

var tags = { 'azd-env-name': environmentName, project: 'dont-let-the-chocolates-pile-up' }
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    mmWriteKey: mmWriteKey
    mmAdminKey: mmAdminKey
  }
}

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_LOCATION string = location
output MM_SITE_URL string = resources.outputs.siteUrl
output MM_MCP_URL string = '${resources.outputs.siteUrl}/mcp'
output APPLICATIONINSIGHTS_CONNECTION_STRING string = resources.outputs.appInsightsConnectionString
