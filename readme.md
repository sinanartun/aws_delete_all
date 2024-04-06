![PyPI - Downloads](https://img.shields.io/pypi/dw/aws-delete-all)
![PyPI version](https://img.shields.io/pypi/v/aws-delete-all)
![GitHub License](https://img.shields.io/github/license/sinanartun/aws_delete_all)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/sinanartun/aws_delete_all)
![Github Created At](https://img.shields.io/github/created-at/sinanartun/aws_delete_all)
![GitHub last commit](https://img.shields.io/github/last-commit/sinanartun/aws_delete_all)




# AWS Delete All  Script

## Introduction
This script is designed to clean up various resources within specific AWS regions in parallel using Python threading. This script uses `boto3`, the AWS SDK for Python, and checks the version of `boto3` currently installed on your system against the latest available version.

Before deleting any resources, it will create threads for each AWS region, and perform the deletion of resources in each region concurrently.

![Demo GIF](https://github.com/sinanartun/aws_delete_all/blob/main/images/demo.gif)

## How to Use in AWS CloudShell
AWS CloudShell is a browser-based shell that you can use to manage your AWS resources. Here's how you can use this script in AWS CloudShell:

1- Open AWS CloudShell from the AWS Management Console.
```bash
pip install aws-delete-all
```
2- Run
```bash
aws-delete-all
```

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
pip install boto3 loguru
```



## Usage
To use this script, simply run it.

```bash
python main.py
```




WARNING: Be very cautious when using this script as it deletes resources.


Resources Deleted
This script deletes the following AWS resources in every AWS region:





### **Amazon EC2**:
- delete_instances
- delete_key_pairs
- delete_amis
- delete_launch_templates
- delete_efs_file_systems
- delete_efs
- delete_elastic_ip

### **Amazon VPC**:

- delete_peering_connection
- delete_load_balancer_listener
- delete_load_balancer
- delete_target_groups
- delete_route_tables
- delete_network_interface
- delete_sg
- delete_sgr
- delete_vpc
- delete_subnets
- delete_endpoint
- delete_internet_gateway

### **Amazon Redshift**:

- delete_redshift_serverless_namespace
- delete_all_redshift_clusters
- delete_redshift_subnet_groups


### **Amazon RDS**:

- delete_db_instance_automated_backups
- delete_db_cluster_snapshots
- delete_all_rds_automated_backups
- delete_rds_option_groups
- delete_db_cluster_parameter_groups
- delete_rds_parameter_groups
- delete_rds_subnet_groups
- delete_rds
- delete_db_instances

### **AWS Lambda**:

- delete_lambda_layers
- delete_lambda_functions

### **Amazon ECS**:

- delete_ecs_tasks
- delete_ecs_cluster
- delete_ecs_clusters

### **Amazon ECR**:

- delete_ecr

### **Amazon S3**:

- delete_s3_buckets
- Amazon DynamoDB:

### **Amazon DynamoDB**

- delete_dynamodb_tables
- delete_dynamodb_backup

### **Amazon Kinesis**:

- delete_all_kinesis_data_streams
- delete_firehose_delivery_streams
- delete_all_firehose_streams


### **Amazon SageMaker**:

- delete_all_notebook_instances


### **Amazon SQS**:

- delete_all_sqs ([furkanbilgin](https://github.com/furkanbilgin))

### **Amazon IAM**:

- delete_all_roles(disabled)

### **AWS Cloud Map** 
- delete_namespaces

### **AWS SNS** 
- delete_sns_topics

### **AWS Cognito** 
- delete_cognito_user_pools
- delete_cognito_identity_pools

### **AWS Athena** 
- delete_athena_saved_queries

### **AWS API Gateway** 
- delete_api_gateways

### **AWS Config** 
- delete_config_recorders_and_delivery_channels

License
This project is licensed under the MIT License. See the LICENSE file for details.
