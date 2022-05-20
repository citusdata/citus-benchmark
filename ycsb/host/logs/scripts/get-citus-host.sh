#!/bin/bash

echo export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',')"`  


#