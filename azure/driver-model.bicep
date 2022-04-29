param adminPublicKey string
param adminUsername string

param pgHost string
param pgUser string
param pgPassword string
param pgPort int
param pgVersion string

param zone string
param location string
param size string
param thread_counts string

param vmName string
param nicName string
param ipName string

param nsgName string
param vnetName string
param subnetName string

var AnalysisDriverBootTemplate = '''
echo export PGHOST='{0}' >> .bashrc
echo export PGUSER={1} >> .bashrc
echo export PGPASSWORD='{2}' >> .bashrc
echo export PGPORT={3} >> .bashrc

# Use the same environment variables right now, sourcing bashrc doesn't work
# since we are not in an interactive shell

export PGHOST='{0}'
export PGUSER={1}
export PGPASSWORD='{2}'
export PGPORT={3}

# Make sure we can open enough connections
echo 'ulimit -n "$(ulimit -Hn)"' >> .bashrc

cat >> .bashrc << '__ssh_connection_bashrc__'
{4}
__ssh_connection_bashrc__

git clone https://github.com/citusdata/citus-benchmark.git --branch ycsb-model
cd citus-benchmark
sudo apt install -y default-jre python postgresql-client-common postgresql-client-{4}

sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib

mkdir success

'''

var AnalysisDriverBootScript = format(AnalysisDriverBootTemplate, pgHost, pgUser, pgPassword, pgPort, pgVersion)

module vmAnalysis 'vm.bicep' = {
  name: '${vmName}-driver-module'
  params: {
    adminPublicKey: adminPublicKey
    adminUsername: adminUsername
    location: location
    zone: zone
    size: size
    vmName: vmName
    nicName: nicName
    ipName: ipName
    nsgName: nsgName
    vnetName: vnetName
    subnetName: subnetName
    bootScript: AnalysisDriverBootScript
    thread_counts: thread_counts
  }
}

output AnalysisPublicIp string = vmAnalysis.outputs.publicIp
