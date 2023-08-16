# AWS Delete All  Script

## Introduction
This script is designed to clean up various resources within specific AWS regions in parallel using Python threading. This script uses `boto3`, the AWS SDK for Python, and checks the version of `boto3` currently installed on your system against the latest available version.

Before deleting any resources, it will create threads for each AWS region, and perform the deletion of resources in each region concurrently.

## AWS CLI Setup
Before you can use `boto3`, you need to set up authentication credentials for your AWS account using the AWS CLI. 

You can install AWS CLI using pip:

```bash
pip install awscli
```
```bash
aws configure
```

**`AWS Access Key ID`** and `AWS Secret Access Key`: You can find these on your AWS account. If you don't have one, you can generate it from the AWS Management Console.

`Default region name`: The region to which AWS CLI directs its requests. You can set any region you want. For example, us-west-2.

**`Default output format`**: The output format for AWS CLI. You can set json.


## Dependencies
```bash
pip install boto3 requests loguru
```



## Usage
To use this script, simply run it.

```bash
python main.py
```




WARNING: Be very cautious when using this script as it deletes resources.


Resources Deleted
This script deletes the following AWS resources in every AWS region:

- Sagemaker Notebook Instances
- EC2 Elastic IP Addresses
- ECS Clusters
- ECS Tasks
- ECR Repositories
- EC2 Instances
- Kinesis Firehose Delivery Streams
- Kinesis Data Streams
- Redshift Clusters
- Redshift Subnet Groups
- Peering Connections
- Load Balancers
- Target Groups
- Lambda Functions
- Lambda Layers
- EFS Systems
- DB Instances
- RDS Systems
- RDS Subnet Groups
- RDS Option Groups
- RDS Parameter Groups
- DB Cluster Parameter Groups
- DB Cluster Snapshots
- DB Instance Automated Backups
- API Gateway Endpoints
- Route Tables
- Network Interfaces
- Subnets
- Security Groups
- Internet Gateways
- VPCs
- S3 buckets
- IAM Roles
- ECS Namespaces
- delete_all_sqs ([furkanbilgin](https://github.com/furkanbilgin))


License
This project is licensed under the MIT License. See the LICENSE file for details.
