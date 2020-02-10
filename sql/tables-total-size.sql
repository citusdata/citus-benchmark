SELECT pg_size_pretty(sum(citus_relation_size(logicalrelid))) FROM pg_dist_partition;
