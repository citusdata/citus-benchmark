SELECT
threads, avg(throughput)
FROM ycsb
WHERE
workloadtype='run'
AND
rg IN (select resource_group as rg from hardware where workers=2 and worker_vcp_num=4)
GROUP BY
threads
ORDER BY avg DESC;
