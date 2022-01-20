SELECT create_distributed_table('pgbench_accounts', 'aid');
SELECT create_distributed_table('pgbench_branches', 'bid');
SELECT create_distributed_table('pgbench_history', 'tid');
SELECT create_distributed_table('pgbench_tellers', 'tid');
