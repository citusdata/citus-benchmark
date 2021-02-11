pgbench -P 60 -j 32 -c 512 -T 1800 -n -f citus4-2pc.sql --log --log-prefix=/mnt/resource/data/citus4-2pc-1.log --sampling-rate=0.01 | tee citus4-2pc.log
pgbench -P 60 -j 32 -c 512 -T 1800 -n -f citus4-1pc.sql --log --log-prefix=/mnt/resource/data/citus4-1pc-1.log --sampling-rate=0.01 | tee citus4-1pc.log
