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
diset connection pg_host $env(PGHOST)
diset connection pg_port $env(PGPORT)
diset tpcc pg_dbase $env(PGDATABASE)
diset tpcc pg_user $env(PGUSER)
diset tpcc pg_superuser $env(PGUSER)
diset tpcc pg_defaultdbase $env(PGDATABASE)
diset tpcc pg_pass $env(PGPASSWORD)
diset tpcc pg_superuserpass $env(PGPASSWORD)
diset tpcc pg_raiseerror true
diset tpcc pg_storedprocs true
diset tpcc pg_num_vu 100
diset tpcc pg_count_ware 1000
diset tpcc pg_partition false
diset tpcc pg_cituscompat true
loadscript
print dict
buildschema
wait_to_complete
vwait forever
