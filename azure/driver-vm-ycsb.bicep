param adminPublicKey string
param adminUsername string

param pgHost string
param pgUser string
param pgPassword string
param pgPort int
param pgVersion string
param monitorpw string

param zone string
param location string
param size string
param records string
param operations string
param shard_count string
param thread_counts string
param iterations int
param rg string
param workers int

param vmName string
param nicName string
param ipName string

param nsgName string
param vnetName string
param subnetName string

var bashrcTmuxAutoAttach = '''
if [[ -n "${PS1:-}" ]] && [[ -z "${TMUX:-}" ]] && [[ -n "${SSH_CONNECTION:-}" ]] ; then
  if { tmux list-sessions | grep '(group main)' ; } > /dev/null 2>&1; then
    tmux attach-session -t ssh 2> /dev/null || tmux new-session -t main -s ssh
  else
    echo "WARNING: Benchmark isn't running yet, try connecting again in a few minutes"
  fi
fi
'''

var driverBootTemplate = '''
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
export PGDATABASE=citus
export RECORDS={6}
export OPERATIONS={7}
export SHARD_COUNT={8}
export THREAD_COUNT={9}
export ITERATIONS={10}
export WORKERS={11}
export RESOURCE_GROUP={12}
export MONITORPW={13}

# Make sure we can open enough connections
echo 'ulimit -n "$(ulimit -Hn)"' >> .bashrc

cat >> .bashrc << '__ssh_connection_bashrc__'
{4}
__ssh_connection_bashrc__

git clone https://github.com/citusdata/citus-benchmark.git --branch ycsb-refactored
cd citus-benchmark/ycsb/driver
export HOMEDIR=$PWD
sudo apt install -y default-jre python postgresql-client-common postgresql-client-{5}

sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib

while ! psql -c 'select 1'; do  echo failed; sleep 1; done
cd scripts
tmux new-session -d -t main -s init-bench \; send-keys './build-and-run-ycsb.sh' Enter
'''

var driverBootScript = format(driverBootTemplate, pgHost, pgUser, pgPassword, pgPort, bashrcTmuxAutoAttach, pgVersion, records, operations, shard_count, thread_counts, iterations, workers, rg, monitorpw)

module vm 'vm.bicep' = {
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
    bootScript: driverBootScript
  }
}

output publicIp string = vm.outputs.publicIp
