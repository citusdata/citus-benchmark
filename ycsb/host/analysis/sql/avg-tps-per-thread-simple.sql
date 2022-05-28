select threads, count(threads), avg(throughput) from ycsb where workers=5 and workloadtype='load' group by threads order by avg desc;
