SELECT
c.threads, c.avg_throughput_ycsb, d.avg_throughput_parallel
FROM
(select a.threads, avg(a.throughput) as avg_throughput_ycsb from ycsb a, (select DISTINCT(resource_group) as rg from hardware where workers=5 and worker_vcp_num=32) b where a.rg = b.rg and a.workloadtype='run' group by threads order by avg_throughput_ycsb desc) c,
(select a.threads, avg(a.throughput) as avg_throughput_parallel from parallel a, (select DISTINCT(resource_group) as rg from hardware where workers=5 and worker_vcp_num=32) b where a.rg = b.rg and a.workloadtype='run' group by threads order by avg_throughput_parallel desc) d
WHERE
c.threads = d.threads;
