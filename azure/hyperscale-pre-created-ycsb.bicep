@secure()
param pgAdminPassword string
@secure()
param vmAdminPublicKey string
param vmAdminUsername string = 'azureuser'
param pgHost string
param pgPort int = 5432
param pgPortAnalysis int = 5004


param location string = resourceGroup().location
param zone string = '1'
param records string = '10000'
param operations string = '10000'
param shard_count string = '64'

// Configuration of the postgres server group
param pgVersion string = '14'

// Configuration of the VM that runs the benchmark (the driver)
// This VM's should be pretty big, to make sure it does not become the bottleneck
param driverSize string  = 'Standard_D64s_v3'
param AnalysisDriverSize string = 'Standard_D64s_v3'

param sshAllowIpPrefix string = '*'
// networking reletaed settings, usually you don't have to change this

param vnetPrefix string = '10.13.0.0/16'
param subnetPrefix string = '10.13.0.0/24'

// names for all resources, based on resourcegroup name by default
// usually should not need to be changed
param namePrefix string = resourceGroup().name
param driverVmName string = '${namePrefix}-driver'
param driverNicName string = '${driverVmName}-nic'
param driverIpName string = '${driverVmName}-ip'
param nsgName string = '${driverVmName}-nsg'
param vnetName string = '${namePrefix}-vnet'
param subnetName string = 'default'

param AnalysisDriverVmName string = '${namePrefix}-driver-analysis'
param AnalysisDriverNicName string = '${AnalysisDriverVmName}-nic'
param AnalysisDriverIpName string = '${AnalysisDriverVmName}-ip'
// param AnalysisNsgName string = '${AnalysisDriverVmName}-nsg'

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
    pgPort: pgPort
    location: location
    zone: zone
    size: driverSize
    vmName: driverVmName
    nicName: driverNicName
    ipName: driverIpName
    nsgName: nsgName
    vnetName: vnetName
    subnetName: subnetName
    pgHost: pgHost
    pgUser: 'citus'
    pgPassword: pgAdminPassword
    pgVersion: pgVersion
    records: records
    operations: operations
    shard_count: shard_count
  }
}

module AnalysisDriverVm 'driver-model.bicep' = {
  name: AnalysisDriverVmName
  params: {
    adminPublicKey: vmAdminPublicKey
    adminUsername: vmAdminUsername
    pgPort: pgPortAnalysis
    location: location
    zone: zone
    size: AnalysisDriverSize
    vmName: AnalysisDriverVmName
    nicName: AnalysisDriverNicName
    ipName: AnalysisDriverIpName
    nsgName: nsgName
    vnetName: vnetName
    subnetName: subnetName
    pgHost: pgHost
    pgUser: 'citus'
    pgPassword: pgAdminPassword
    pgVersion: pgVersion
    records: records
    operations: operations
  }
}

output driverPublicIp string = driverVm.outputs.publicIp
output AnalysisDriverPublicIp string = AnalysisDriverVm.outputs.AnalysisPublicIp
