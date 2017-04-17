#!/usr/bin/env bash

function usage {
     echo """
     This script is to upload the website components of the sample demo app to the s3 bucket created to host
     the website. To use, pass the profile name and s3 bucket name after the script name.

     upload_website.sh <profile> <s3_bucket_name>

     ex:
     upload_website.sh profile-name some-demo-app-bucket
     """
 }

AWS_PROFILE='default'
S3_BUCKET=''

 # Get the table name
 if [ $# -eq 0 ]; then
     usage;
     exit;
 else
     AWS_PROFILE="$1"
     S3_BUCKET="$2"
 fi

aws --profile ${AWS_PROFILE} s3 cp ./website/ "s3://${S3_BUCKET}" --recursive --exclude "*.yaml"
