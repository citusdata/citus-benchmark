 select iteration, workloadtype, threads, throughput from ycsb where workers=5 and records=10000000 order by throughput desc;
