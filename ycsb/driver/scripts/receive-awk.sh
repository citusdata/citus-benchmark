#!/bin/bash

PID=$$
FLAG=0

(sleep 10 && kill "$PID" && echo "Timeout error: no awk received from host") & 2> /dev/null

while [ ! -f awk ]
do
  sleep 1 # or less like 0.2
done

rm awk

