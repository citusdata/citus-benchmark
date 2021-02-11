pgbench -P 60 -j 32 -c 256 -T 900 -n -f citus4-small-2pc.sql --log --log-prefix=/mnt/resource/data/citus4-small-2pc-1.log --sampling-rate=0.01 | tee citus4-small-2pc.log
pgbench -P 60 -j 32 -c 256 -T 900 -n -f citus4-small-1pc.sql --log --log-prefix=/mnt/resource/data/citus4-small-1pc-1.log --sampling-rate=0.01 | tee citus4-small-1pc.log
