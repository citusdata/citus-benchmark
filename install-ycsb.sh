#!/bin/bash

wget https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz

tar xfvz ycsb-0.17.0.tar.gz

cd ycsb-0.17.0

wget https://jdbc.postgresql.org/download/postgresql-42.2.14.jar
