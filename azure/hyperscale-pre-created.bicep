@secure()
param pgAdminPassword string
@secure()
param vmAdminPublicKey string
param vmAdminUsername string = 'azureuser'
param pgHost string


param location string = resourceGroup().location

param buildAndRunFlags string = ''
param warehouses int = 1000
param buildWarehouses int = warehouses
param runWarehouses int = warehouses
param buildVirtualUsers int = 100
param runVirtualUsers int = 250
param allWarehouses bool = true
param duration int = 60
param rampup int = 5
param timeprofile bool = true


// Configuration of the postgres server group
param pgVersion string = '14'

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
param driverVmName string = '${namePrefix}-driver'
param driverNicName string = '${driverVmName}-nic'
param driverIpName string = '${driverVmName}-ip'
param nsgName string = '${driverVmName}-nsg'
param vnetName string = '${namePrefix}-vnet'
param subnetName string = 'default'

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

module driverVm 'driver-vm.bicep' = {
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
    pgHost: pgHost
    pgUser: 'citus'
    pgPassword: pgAdminPassword
    pgVersion: pgVersion
    buildAndRunFlags: '--name "${namePrefix}" ${buildAndRunFlags}'
    buildWarehouses: buildWarehouses
    runWarehouses: runWarehouses
    buildVirtualUsers: buildVirtualUsers
    runVirtualUsers: runVirtualUsers
    allWarehouses: allWarehouses
    duration: duration
    rampup: rampup
    timeprofile: timeprofile
  }
}

output driverPublicIp string = driverVm.outputs.publicIp
