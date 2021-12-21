@secure()
param pgAdminPassword string
@secure()
param vmAdminPublicKey string
param vmAdminUsername string = 'azureuser'

param location string = resourceGroup().location

// Configuration of the benchmark
param buildAndRunFlags string = '--no-citus'
param warehouses int = 1000
param buildWarehouses int = warehouses
param runWarehouses int = warehouses
param buildVirtualUsers int = 100
param runVirtualUsers int = 250
param allWarehouses bool = true
param duration int = 60
param rampup int = 3
param timeprofile bool = true

// Configuration of the postgres server
param pgVersion string = '14'
param pgSize string  = 'Standard_D8s_v3' 
param pgStorageSizeGB int = 512


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
param nsgName string = '${namePrefix}-nsg'
param pgVmName string = '${namePrefix}-pg'
param pgNicName string = '${pgVmName}-nic'
param pgIpName string = '${pgVmName}-ip'
param pgDiskName string = '${pgVmName}-data-disk'
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

var pgBootTemplate = '''
sudo su << '__root_user_EOF__'
set -euxo pipefail
# disk formatting/mounting commands taken from: 
# https://docs.microsoft.com/en-us/azure/virtual-machines/linux/attach-disk-portal
parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
mkfs.xfs /dev/sdc1
partprobe /dev/sdc1
mkdir /datadrive
mount /dev/sdc1 /datadrive

apt-get install -y postgresql-{0}
systemctl stop postgresql@{0}-main || true

mv /var/lib/postgresql/14/main/ /datadrive/pgdata

echo "data_directory = '/datadrive/pgdata'" >> /etc/postgresql/{0}/main/postgresql.conf
echo "listen_addresses = '*'" >> /etc/postgresql/{0}/main/postgresql.conf
echo "max_connections = 500" >> /etc/postgresql/{0}/main/postgresql.conf


echo "host  all  all  0.0.0.0/0  scram-sha-256" >> /etc/postgresql/{0}/main/pg_hba.conf
echo "host  all  all  ::/0       scram-sha-256" >> /etc/postgresql/{0}/main/pg_hba.conf

systemctl start postgresql@{0}-main
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '{1}'"
__root_user_EOF__
'''

var pgBootScript = format(pgBootTemplate, pgVersion, pgAdminPassword)

module pgVm 'vm.bicep' = {
  name: pgVmName
  params: {
    adminPublicKey: vmAdminPublicKey
    adminUsername: vmAdminUsername
    location: location
    size: pgSize
    vmName: pgVmName
    nicName: pgNicName
    ipName: pgIpName
    nsgName: nsgName
    vnetName: vnetName
    subnetName: subnetName
    bootScript: pgBootScript
    dataDisks: [
      {
        name: pgDiskName
        createOption: 'Empty'
        diskSizeGB: pgStorageSizeGB
        lun: 0
        managedDisk: {
          storageAccountType: 'Premium_LRS'
        }
      }
    ]
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
    pgHost: '${pgVmName}.internal.cloudapp.net'
    pgUser: 'postgres'
    pgPassword: pgAdminPassword
    pgVersion: pgVersion
    buildAndRunFlags: '--no-citus'
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
output pgPublicIp string = pgVm.outputs.publicIp
