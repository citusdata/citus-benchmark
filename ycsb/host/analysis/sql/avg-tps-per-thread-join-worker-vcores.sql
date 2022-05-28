select threads, count(threads), avg(throughput) from ((select * from ycsb where workers=5 and workloadtype='run') a left join hardware b on a.rg = b.resource_group) c where c.worker_vcp_num=32 group by threads order by avg desc;
