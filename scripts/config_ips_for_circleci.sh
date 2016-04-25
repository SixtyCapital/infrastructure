#!/bin/bash
# This script takes the IP Addresses in Amazons us-east-1 and us-east-2 block
# and uploads it into the Security Groups in AWS for the SQL Server
# 
# Procedure:
#   1)  Remove all the rules in the Amazon security groups
#   2)  Download the latest IP list from Amazon and save as ip-ranges.json:
#         http://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html#aws-ip-download
#   3)  Run this script
#
# Note that each security group in Amazon AWS can only have 50 rules and each machine can
# only have 5 security groups.  Right now there are 175 IP blocks for east and west so
# that is not a problem, but may become an issue in the future.
# rm usew.txt
jq '.prefixes[] | select(.region=="us-east-1" or .region=="us-west-1").ip_prefix' < ip-ranges.json > usew.txt

cat usew.txt | while read line
do
  echo $((count / 50))

  ((count++))
  aws ec2 authorize-security-group-ingress --group-name CircleCI$((count / 50)) --protocol tcp --port 1433 --cidr  ${line:1:-1}
done
echo "Done"
