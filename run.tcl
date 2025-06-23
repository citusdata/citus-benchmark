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
diset connection pg_port 7432
diset connection pg_sslmode prefer

diset tpcc pg_count_ware 100
diset tpcc pg_superuser cloudsa
diset tpcc pg_superuserpass $env(PGPASSWORD)
diset tpcc pg_defaultdbase postgres
diset tpcc pg_user cloudsa
diset tpcc pg_pass $env(PGPASSWORD)
diset tpcc pg_dbase postgres
diset tpcc pg_tspace pg_default
diset tpcc pg_vacuum false
diset tpcc pg_dritasnap false
diset tpcc pg_oracompat false
diset tpcc pg_cituscompat true
diset tpcc pg_storedprocs false
diset tpcc pg_partition false
diset tpcc pg_total_iterations 10000000
diset tpcc pg_raiseerror false
diset tpcc pg_keyandthink false
diset tpcc pg_driver timed
diset tpcc pg_rampup 2
diset tpcc pg_duration 5
diset tpcc pg_allwarehouse false
diset tpcc pg_timeprofile false
diset tpcc pg_async_scale false
diset tpcc pg_async_client 10
diset tpcc pg_async_verbose false
diset tpcc pg_async_delay 1000
diset tpcc pg_connect_pool false
diset tpcc pg_num_vu 2

loadscript
print dict
vuset vu 250
vuset timestamps 1
vuset logtotemp 1
vuset showoutput 0
vuset unique 1
vuset delay 20
vuset repeat 1
vurun
wait_to_complete
vwait forever
