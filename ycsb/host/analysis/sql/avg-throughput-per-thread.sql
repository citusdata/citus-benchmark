select threads, avg(throughput) from ycsb where workloadtype='run' and rg in (select resource_group as rg from hardware where workers=2 and worker_vcp_num=4) group by threads order by avg desc;
