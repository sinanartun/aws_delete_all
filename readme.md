# AWS Resource Cleanup Script

## Introduction
This script is designed to clean up various resources within specific AWS regions in parallel using Python threading. This script uses `boto3`, the AWS SDK for Python, and checks the version of `boto3` currently installed on your system against the latest available version.

Before deleting any resources, it will create threads for each AWS region, and perform the deletion of resources in each region concurrently.

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

- Notebook Instances
- Elastic IP Addresses
- ECS Clusters
- ECS Tasks
- ECR Repositories
- EC2 Instances
- Firehose Delivery Streams
- Kinesis Data Streams
- Redshift Clusters
- Redshift Subnet Groups
- Firehose Streams
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


License
This project is licensed under the MIT License. See the LICENSE file for details.