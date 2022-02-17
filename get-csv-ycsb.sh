#!/bin/bash
set -euo pipefail

dir=${1:-$BENCHMARK_NAME}

result=output-results.csv
rm -f result

echo "$RESOURCE_GROUP" >> $result

for outputfile in $dir/*.log
do
	row=$(echo ${outputfile//[_]/,} | cut -d"." -f 1)
	tp=$(grep Throughput $outputfile | awk '{print $3}')
       	echo ${row},${tp} >> $result
done

echo $(cat $result)
