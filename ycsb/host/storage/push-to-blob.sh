#!/bin/bash

export LOCAL_FOLDER=$1
export BUCKET=$2
export AWS_FOLDER=$3

aws s3 sync $LOCAL_FOLDER s3://${BUCKET}/$AWS_FOLDER
