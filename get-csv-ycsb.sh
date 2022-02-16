#!/bin/bash
set -euo pipefail

dir=${1:-$BENCHMARK_NAME}

result=output-results.csv
rm -f result

echo "bench-name,threads,records,operations,throughput" >> $result

for outputfile in $dir/*.log
do
	row=$(echo ${outputfile//[_]/,} | cut -d"." -f 1)
	tp=$(grep Throughput $outputfile | awk '{print $3}')
       	echo ${row},${tp} >> $result
done

echo $(cat $result)
