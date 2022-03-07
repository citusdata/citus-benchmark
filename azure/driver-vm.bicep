param adminPublicKey string
param adminUsername string

param pgHost string
param pgUser string
param pgPassword string
param pgVersion string

param location string
param size string

param vmName string
param nicName string
param ipName string

param nsgName string
param vnetName string
param subnetName string

param buildAndRunFlags string
param buildWarehouses int
param runWarehouses int
param buildVirtualUsers int
param runVirtualUsers int
param allWarehouses bool
param duration int
param rampup int
param timeprofile bool

// Interpolating booleans directly will result in capitalized words, i.e. True/False
// instead of true/false. HammerDB needs lower cased ones
var allWarehousesString = allWarehouses ? 'true' : 'false'
var timeprofileString = timeprofile ? 'true' : 'false'

var bashrcTmuxAutoAttach = '''
if [[ -n "${PS1:-}" ]] && [[ -z "${TMUX:-}" ]] && [[ -n "${SSH_CONNECTION:-}" ]] ; then
  if { tmux list-sessions | grep '(group main)' ; } > /dev/null 2>&1; then
    tmux attach-session -t ssh 2> /dev/null || tmux new-session -t main -s ssh
  else
    echo "WARNING: Benchmark isn't running yet, try connecting again in a few minutes"
  fi
fi
'''

var sedCommandsTemplate = '''
sed -i -e "s/diset tpcc pg_count_ware .*/diset tpcc pg_count_ware {0}/" build.tcl
sed -i -e "s/diset tpcc pg_count_ware .*/diset tpcc pg_count_ware {1}/" run.tcl
sed -i -e "s/diset tpcc pg_num_vu .*/diset tpcc pg_num_vu {2}/" build.tcl
sed -i -e "s/vuset vu .*/vuset vu {3}/" run.tcl
sed -i -e "s/diset tpcc pg_allwarehouse .*/diset tpcc pg_allwarehouse {4}/" run.tcl
sed -i -e "s/diset tpcc pg_duration .*/diset tpcc pg_duration {5}/" run.tcl
sed -i -e "s/diset tpcc pg_rampup .*/diset tpcc pg_rampup {6}/" run.tcl
sed -i -e "s/diset tpcc pg_timeprofile .*/diset tpcc pg_timeprofile {7}/" run.tcl
'''

var sedCommands = format(sedCommandsTemplate, buildWarehouses, runWarehouses, buildVirtualUsers, runVirtualUsers, allWarehousesString, duration, rampup, timeprofileString)


var driverBootTemplate = '''
echo export PGHOST='{0}' >> .bashrc
echo export PGUSER={1} >> .bashrc
echo export PGPASSWORD='{2}' >> .bashrc

# Use the same environment variables right now, sourcing bashrc doesn't work
# since we are not in an interactive shell
export PGHOST='{0}'
export PGUSER={1}
export PGPASSWORD='{2}'

# Make sure we can open enough connections
echo 'ulimit -n "$(ulimit -Hn)"' >> .bashrc

cat >> .bashrc << '__ssh_connection_bashrc__'
{3}
__ssh_connection_bashrc__

sudo apt-get install -y postgresql-client-{4}
git clone https://github.com/citusdata/citus-benchmark.git
cd citus-benchmark

{5}

while ! psql -c 'select 1'; do  echo failed; sleep 1; done
tmux new-session -d -t main -s cloud-init \; send-keys './build-and-run.sh {6}' Enter
'''
var driverBootScript = format(driverBootTemplate, pgHost, pgUser, pgPassword, bashrcTmuxAutoAttach, pgVersion, sedCommands, replace(buildAndRunFlags, '\'', '\'\\\'\''))

module vm 'vm.bicep' = {
  name: '${vmName}-driver-module'
  params: {
    adminPublicKey: adminPublicKey
    adminUsername: adminUsername
    location: location
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
