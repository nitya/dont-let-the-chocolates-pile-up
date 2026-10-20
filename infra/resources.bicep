param location string
param tags object
param resourceToken string

@secure()
param mmWriteKey string

@secure()
param mmAdminKey string

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: 'plan-${resourceToken}'
  location: location
  tags: tags
  kind: 'linux'
  sku: { name: 'B1' }
  properties: { reserved: true }
}

// Single instance on purpose: drafts live in one JSON file under /home (persistent storage).
resource site 'Microsoft.Web/sites@2024-04-01' = {
  name: 'app-mm-${resourceToken}'
  location: location
  tags: union(tags, { 'azd-service-name': 'site' })
  kind: 'app,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appCommandLine: 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
        { name: 'WEBSITES_PORT', value: '8000' }
        { name: 'MM_STATE_DIR', value: '/home/mm-state' }
        { name: 'MM_WRITE_KEY', value: mmWriteKey }
        { name: 'MM_ADMIN_KEY', value: mmAdminKey }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
      ]
    }
  }
}

output siteUrl string = 'https://${site.properties.defaultHostName}'
output appInsightsConnectionString string = appInsights.properties.ConnectionString
