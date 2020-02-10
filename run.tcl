#!/bin/tclsh
puts "SETTING CONFIGURATION"
global complete
proc wait_to_complete {} {
global complete
set complete [vucomplete]
if {!$complete} { after 5000 wait_to_complete } else { exit }
}
dbset db pg
loadscript
diset connection pg_host replace_with_ip_address
diset tpcc pg_dbase pguser
diset tpcc pg_user pguser
diset tpcc pg_superuser pguser
diset tpcc pg_defaultdbase pguser
#diset tpcc pg_pass yourpasswordhere
#diset tpcc pg_superuserpass yourpasswordhere
# if you change this, make sure to change tpcc-distribute-funcs.sql
diset tpcc pg_storedprocs true
diset tpcc pg_driver timed
diset tpcc pg_rampup 3
diset tpcc pg_duration 20
diset tpcc pg_timeprofile false
diset tpcc pg_allwarehouse true
diset tpcc pg_keyandthink false
loadscript
print dict
vuset vu 250
vuset timestamps 1
vuset logtotemp 1
vuset showoutput 0
vuset unique 1
vuset delay 100
vuset repeat 0
vurun
wait_to_complete
vwait forever
