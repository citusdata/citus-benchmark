param adminPublicKey string
param adminUsername string

param location string
param size string

param vmName string
param nicName string
param ipName string

param nsgName string
param vnetName string
param subnetName string

param bootScript string
param dataDisks array = []

var nsgId = resourceId(resourceGroup().name, 'Microsoft.Network/networkSecurityGroups', nsgName)
var vnetId = resourceId(resourceGroup().name, 'Microsoft.Network/virtualNetworks', vnetName)
var subnetRef = '${vnetId}/subnets/${subnetName}'

resource nic 'Microsoft.Network/networkInterfaces@2021-03-01' = {
  name: nicName
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: subnetRef
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: resourceId(resourceGroup().name, 'Microsoft.Network/publicIpAddresses', ipName)
          }
        }
      }
    ]
    enableAcceleratedNetworking: true
    networkSecurityGroup: {
      id: nsgId
    }
  }
  dependsOn: [
    ip
  ]
}


resource ip 'Microsoft.Network/publicIpAddresses@2019-02-01' = {
  name: ipName
  location: location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
  sku: {
    name: 'Basic'
  }
}


output publicIp string = reference(resourceId(resourceGroup().name, 'Microsoft.Network/publicIpAddresses', ipName)).ipAddress

var tmuxConf = '''
set -g default-terminal "screen-256color"

# https://stackoverflow.com/a/40902312/2570866
# Version-specific commands [grumble, grumble]
# See: https://github.com/tmux/tmux/blob/master/CHANGES
run-shell "tmux setenv -g TMUX_VERSION $(tmux -V | cut -c 6-)"

if-shell -b '[ $(printf "%s\n" "$TMUX_VERSION" "2.1" | sort -V | tail -n1) = 2.1 ]' \
  "set -g mouse-select-pane on; set -g mode-mouse on; \
    set -g mouse-resize-pane on; set -g mouse-select-window on"

# In version 2.1 "mouse" replaced the previous 4 mouse options
if-shell -b '[ $(printf "%s\n" "$TMUX_VERSION" "2.1" | sort -V | head -n1) = 2.1 ]' \
  "set -g mouse on"

# UTF8 is autodetected in 2.2 onwards, but errors if explicitly set
if-shell -b '[ $(printf "%s\n" "$TMUX_VERSION" "2.2" | sort -V | tail -n1) = 2.2 ]' \
  "set -g utf8 on; set -g status-utf8 on; set -g mouse-utf8 on"

# Intuitive splitting
bind | split-window -h
bind _ split-window -v
# Easy swithing pane
bind-key C-a last-pane

set -g status-bg black
set -g status-fg white
set -g status-left '#S | '
setw -g window-status-format "#I #W |"
setw -g window-status-current-format "#[fg=green] #I #W #[fg=white]|"

set -g history-limit 50000

# Turn on vim awesomeness
set-window-option -g mode-keys vi

bind h select-layout even-vertical

# Make ctrl left/right work
set-window-option -g xterm-keys on

set -ga terminal-overrides ',*:sitm@,ritm@'
'''

var bootTemplate = '''
#!/bin/bash
set -euxo pipefail
sudo su {0} << '__admin_user_EOF__'
set -euxo pipefail
whoami
cd /home/{0}

cat > .tmux.conf << '__tmux_conf_EOF__'
{1}
__tmux_conf_EOF__

sudo apt -y install wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt-get update -y
while ! sudo apt-get upgrade -y; do
    sleep 5
done
sudo apt-get install -y git tmux vim bash-completion net-tools

{2}
__admin_user_EOF__
'''
var driverBootScript = format(bootTemplate, adminUsername, tmuxConf, bootScript)

resource vm 'Microsoft.Compute/virtualMachines@2021-07-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: {
      vmSize: size
    }
    storageProfile: {
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Premium_LRS'
        }
      }
      imageReference: {
        publisher: 'canonical'
        offer: '0001-com-ubuntu-server-focal'
        sku: '20_04-lts-gen2'
        version: 'latest'
      }
      dataDisks: dataDisks
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: adminPublicKey
            }
          ]
        }
      }
      customData: base64(driverBootScript)
    }
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: true
      }
    }
  }
}
