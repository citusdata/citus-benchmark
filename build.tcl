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
diset connection pg_host replace_with_host
diset tpcc pg_dbase citus
diset tpcc pg_user citus
diset tpcc pg_superuser citus
diset tpcc pg_defaultdbase citus
diset tpcc pg_pass 
diset tpcc pg_superuserpass 
# if you change this, make sure to change tpcc-distribute-funcs.sql
diset tpcc pg_storedprocs true
diset tpcc pg_num_vu 250
diset tpcc pg_count_ware 1000
loadscript
print dict
buildschema
wait_to_complete
vwait forever
