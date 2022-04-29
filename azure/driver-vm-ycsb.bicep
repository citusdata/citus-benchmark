param adminPublicKey string
param adminUsername string

param pgHost string
param pgUser string
param pgPassword string
param pgPort int
param pgVersion string
param pre_created int

param zone string
param location string
param size string
param records string
param operations string
param shard_count string
param thread_counts string

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
export ALL_THREADS={9}
export PRE_CREATED={10}

echo $ALL_THREADS

# Make sure we can open enough connections
echo 'ulimit -n "$(ulimit -Hn)"' >> .bashrc

cat >> .bashrc << '__ssh_connection_bashrc__'
{4}
__ssh_connection_bashrc__

git clone https://github.com/citusdata/citus-benchmark.git --branch ycsb-model
cd citus-benchmark
sudo apt install -y default-jre python postgresql-client-common postgresql-client-{5}

sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib

while ! psql -c 'select 1'; do  echo failed; sleep 1; done
tmux new-session -d -t main -s cloud-init \; send-keys './build-and-run-ycsb.sh {6} {7} {8}' Enter
'''

var driverBootScript = format(driverBootTemplate, pgHost, pgUser, pgPassword, pgPort, bashrcTmuxAutoAttach, pgVersion, records, operations, shard_count, thread_counts, pre_created)

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
    thread_counts: thread_counts
  }
}

output publicIp string = vm.outputs.publicIp
