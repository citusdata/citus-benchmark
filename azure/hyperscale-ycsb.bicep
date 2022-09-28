@secure()
param pgAdminPassword string
@secure()
param vmAdminPublicKey string
param vmAdminUsername string = 'azureuser'

param location string = resourceGroup().location
param zone string = '1'
param records string = '10000'
param operations string = '10000'
param shard_count string = '64'
param thread_counts string = '100,300'
param pgPort int = 5432
param iterations int = 1
param workloads string = 'run_all_workloads'


// Configuration of the postgres server group
param pgVersion string = '14'
param coordinatorVcores int = 16
param coordinatorStorageSizeMB int = 2097152 // 2TB
param workers int = 2
param workerVcores int = 16
param workerStorageSizeMB int = 2097152 // 2TB
param enableHa bool = false
param enablePublicIpAccess bool = true

// Configuration of the VM that runs the benchmark (the driver)
// This VM should be pretty big, to make sure it does not become the bottleneck
param driverSize string  = 'Standard_D64s_v3'

param sshAllowIpPrefix string = '*'
// networking reletaed settings, usually you don't have to change this

param vnetPrefix string = '10.13.0.0/16'
param subnetPrefix string = '10.13.0.0/24'

// names for all resources, based on resourcegroup name by default
// usually should not need to be changed
param namePrefix string = resourceGroup().name
param pgServerGroupName string = '${namePrefix}-pg'
param driverVmName string = '${namePrefix}-driver'
param driverNicName string = '${driverVmName}-nic'
param driverIpName string = '${driverVmName}-ip'
param nsgName string = '${driverVmName}-nsg'
param vnetName string = '${namePrefix}-vnet'
param subnetName string = 'default'

resource serverGroup 'Microsoft.DBforPostgreSQL/serverGroupsv2@2020-10-05-privatepreview' = {
  name: pgServerGroupName
  location: location
  properties: {
    administratorLoginPassword: pgAdminPassword
    previewFeatures: true
    postgresqlVersion: pgVersion
    serverRoleGroups: [
      {
        role: 'Coordinator'
        serverCount: 1
        serverEdition: 'GeneralPurpose'
        vCores: coordinatorVcores
        storageQuotaInMb: coordinatorStorageSizeMB
        enableHa: enableHa
        // enablePublicIpAccess : enablePublicIpAccess
      }
      {
        role: 'Worker'
        serverCount: workers
        serverEdition: 'MemoryOptimized'
        vCores: workerVcores
        storageQuotaInMb: workerStorageSizeMB
        enableHa: enableHa
        enablePublicIpAccess : enablePublicIpAccess
      }
    ]
  }
}

resource serverGroupFirewallRule 'Microsoft.DBforPostgreSQL/serverGroupsv2/firewallRules@2020-10-05-privatepreview' = {
  name: '${pgServerGroupName}/AllowAll'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
  dependsOn: [
    serverGroup
  ]
}

module vnet 'vnet.bicep' = {
  name: vnetName
  params: {
    vnetName: vnetName
    subnetName: subnetName
    nsgName: nsgName
    sshAllowIpPrefix: sshAllowIpPrefix
    vnetPrefix: vnetPrefix
    subnetPrefix: subnetPrefix
    location: location
  }
}

module driverVm 'driver-vm-ycsb.bicep' = {
  name: driverVmName
  params: {
    adminPublicKey: vmAdminPublicKey
    adminUsername: vmAdminUsername
    location: location
    size: driverSize
    vmName: driverVmName
    nicName: driverNicName
    ipName: driverIpName
    nsgName: nsgName
    vnetName: vnetName
    subnetName: subnetName
    pgHost: 'c.${pgServerGroupName}.postgres.database.azure.com'
    pgUser: 'citus'
    pgPassword: pgAdminPassword
    pgVersion: pgVersion
    records: records
    operations: operations
    shard_count: shard_count
    thread_counts: thread_counts
    zone: zone
    pgPort: pgPort
    iterations: iterations
    namePrefix: namePrefix
    workers: workers
    workloads: workloads
  }
}

output driverPublicIp string = driverVm.outputs.publicIs
