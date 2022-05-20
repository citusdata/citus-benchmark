#!/bin/bash

export AWS_FOLDER=$1
export BUCKET=$2

aws s3 sync $AWS_FOLDER s3://${BUCKET}/
