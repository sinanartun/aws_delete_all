import json
import string
import sys
from loguru import logger
import threading
import time
from datetime import datetime
import boto3
import botocore
import requests
from botocore.exceptions import ClientError
from botocore.exceptions import WaiterError

logger.remove()

logger.add(
    sink=sys.stdout,
    format="<level>{time:HH:mm:ss}</level>|<level>{level: <8}</level>|{line: <4}| <level>{message}</level>",
    level="DEBUG"
)

max_retries = 10


def get_latest_available_version(package_name):
    url = f"https://pypi.python.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching package info: {response.status_code}")
        return None

    data = response.json()
    latest_version = data['info']['version']
    return latest_version


latest_available_version = get_latest_available_version('boto3')
if str(latest_available_version) != str(boto3.__version__):
    logger.warning(f"Latest available version of boto3 is: {latest_available_version}")
    logger.warning(f"you can upgrade boto3 using this command:")
    logger.warning(f"pip install --upgrade boto3")

logger.success("Current boto3 version: " + boto3.__version__)
logger.success("Please remember to check correct boto3 version documentation !!!")
logger.success("Boto3 Docs " + boto3.__version__ + " documentation")
letters = string.ascii_lowercase


def pt():
    date_time = datetime.fromtimestamp(int(time.time()))
    return date_time.strftime("%H:%M:%S")


common_regions = [
    'eu-north-1',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3'
]


def get_aws_account_id():
    sts = boto3.client('sts', region_name='us-east-1')
    response = sts.get_caller_identity()
    return response['Account']


def run():
    aws_account_id = get_aws_account_id()
    if not aws_account_id:
        logger.error("Failed to retrieve AWS account ID")
        return

    logger.info("Starting to delete AWS resources")

    # Initialize EC2 client in a specific region
    ec2 = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2.describe_regions()
    except Exception as e:
        logger.error(f"Failed to describe AWS regions: {e}")
        return

    threads = []
    for region in response['Regions']:
        region_name = region['RegionName']
        logger.info(f"Working on {region_name}")

        # Create a new thread to delete resources in the specified region
        t = threading.Thread(target=delete_resources, args=(region_name, aws_account_id))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Delete S3 buckets and IAM roles
    delete_s3_buckets()
    # delete_all_roles() // bunu iptal ettim cunku beklenmedik hatalarsa sebep oluyor.






def delete_resources(region_name, aws_account_id):
    delete_all_notebook_instances(region_name)
    delete_ecs_cluster(region_name)
    delete_ecs_tasks(region_name)
    delete_ecr(region_name)
    delete_instances(region_name)
    delete_firehose_delivery_streams(region_name)
    delete_all_kinesis_data_streams(region_name)
    delete_all_redshift_clusters(region_name)
    delete_redshift_subnet_groups(region_name)
    delete_all_firehose_streams(region_name)
    delete_ecs_clusters(region_name)
    delete_dynamodb_tables(region_name)
    delete_dynamodb_backups(region_name)
    delete_peering_connection(region_name)
    delete_load_balancer(region_name)
    delete_target_groups(region_name)
    delete_lambda_functions(region_name)
    delete_lambda_layers(region_name)
    delete_efs(region_name)
    delete_db_instances(region_name)
    delete_rds(region_name)
    delete_rds_subnet_groups(region_name)
    delete_rds_option_groups(region_name)
    delete_rds_parameter_groups(region_name)
    delete_db_cluster_parameter_groups(region_name)
    delete_db_cluster_snapshots(region_name)
    delete_db_instance_automated_backups(region_name)
    delete_endpoint(region_name)
    delete_route_tables(region_name)
    delete_network_interface(region_name)
    delete_subnets(region_name)
    delete_sgr(region_name)
    delete_sg(region_name)
    delete_elastic_ip(region_name)
    delete_internet_gateway(region_name)
    delete_vpc(region_name)
    delete_all_sqs(region_name)
    delete_namespaces(region_name)
    delete_redshift_serverless_namespace(region_name)
    delete_efs_file_systems(region_name)
    delete_launch_templates(region_name)
    delete_key_pairs(region_name)
    delete_amis(region_name, aws_account_id)
    delete_all_secrets(region_name)
    delete_rest_apis(region_name)
    delete_http_apis(region_name)
    delete_alarms(region_name)
    delete_log_groups(region_name)
    delete_eventbridge_rules(region_name)
    delete_elastic_ip(region_name)
    delete_cognito_user_pools(region_name)
    delete_cognito_identity_pools(region_name)
    delete_sns_topics(region_name)






def delete_eventbridge_rules(region_name):
    events = boto3.client('events', region_name=region_name)
    buses = events.list_event_buses()
    bus_names = [bus['Name'] for bus in buses['EventBuses']]
    for event_bus_name in bus_names:
        rules = events.list_rules(EventBusName=event_bus_name)
        rule_names = [rule['Name'] for rule in rules['Rules']]
        if not rule_names:
            continue
        logger.warning(f"{len(rule_names)} rules found for event bus: {event_bus_name}.")
        for rule_name in rule_names:
            targets = events.list_targets_by_rule(Rule=rule_name, EventBusName=event_bus_name)
            target_ids = [target['Id'] for target in targets['Targets']]
            if target_ids:
                try:
                    events.remove_targets(Rule=rule_name, EventBusName=event_bus_name, Ids=target_ids)
                except Exception as e:
                    logger.info(f"Info: removing targets for rule {rule_name} on event bus {event_bus_name}: {e}")
                    continue
            try:
                events.delete_rule(Name=rule_name, EventBusName=event_bus_name)
                logger.success(f"Deleted rule: {rule_name} for event bus: {event_bus_name}")
            except Exception as e:
                logger.info(f"Error deleting rule {rule_name} on event bus {event_bus_name}: {e}")


def delete_log_groups(region_name):
    client = boto3.client('logs', region_name=region_name)
    log_group_names = []

    paginator = client.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        log_group_names.extend([log_group['logGroupName'] for log_group in page['logGroups']])

    if not log_group_names:
        return
    logger.warning(f"CloudWatch Log Groups Found: count({len(log_group_names)})")
    for log_group_name in log_group_names:
        client.delete_log_group(logGroupName=log_group_name)
        logger.success(f"Deleted log group: {log_group_name}")


def delete_alarms(region_name):
    client = boto3.client('cloudwatch', region_name=region_name)
    alarms = client.describe_alarms()
    alarm_names = [alarm['AlarmName'] for alarm in alarms['MetricAlarms']]

    if not alarm_names:
        return
    logger.warning(f"CloudWatch Alarms Found: count({len(alarm_names)})")

    client.delete_alarms(AlarmNames=alarm_names)
    logger.success(f"Deleted {len(alarm_names)} alarms.")


def delete_http_apis(region_name):
    client = boto3.client('apigatewayv2', region_name=region_name)
    apis = client.get_apis()['Items']

    if not apis:
        return
    logger.warning(f"Api Gateway HTTP APIs Found: count({len(apis)})")
    for api in apis:
        api_id = api['ApiId']
        api_name = api.get('Name', 'Unnamed API')  # Name might not always be present

        try:
            client.delete_api(ApiId=api_id)
            logger.success(f"Successfully deleted HTTP API:{region_name}=> {api_name} ({api_id})")

        except client.exceptions.NotFoundException:
            logger.warning(
                f"HTTP API {region_name}=>{api_name} ({api_id}) not found. It might have been already deleted.")
        except Exception as e:
            logger.error(f"Error deleting HTTP API {region_name}=> {api_name} ({api_id}): {e}")


def delete_rest_apis(region_name):
    client = boto3.client('apigateway', region_name=region_name)

    apis = client.get_rest_apis()['items']

    if not apis:
        return
    logger.warning(f"Api Gateway REST APIs Found: count({len(apis)})")
    for api in apis:
        api_id = api['id']
        api_name = api['name']

        try:
            client.delete_rest_api(restApiId=api_id)
            logger.info(f"Successfully deleted API:{region_name}=> {api_name} ({api_id})")

        except client.exceptions.ResourceNotFoundException:
            logger.warning(f"API {api_name} ({api_id}) not found. It might have been already deleted.")
        except Exception as e:
            logger.error(f"Error deleting API {api_name} ({api_id}): {e}")



def delete_all_secrets(region_name):
    client = boto3.client('secretsmanager', region_name=region_name)
    paginator = client.get_paginator('list_secrets')

    for page in paginator.paginate():
        for secret in page['SecretList']:
            secret_name = secret['Name']
            try:
                response = client.describe_secret(SecretId=secret_name)
                replication_status_list = response.get('ReplicationStatus')
                
                if replication_status_list is not None:
                    for replication_status in replication_status_list:
                        region = replication_status.get('Region')
                        status = replication_status.get('Status')
                        
                        if status == 'InSync':
                            logger.info(f"Replica found for secret {region_name} => {secret_name} in region {region}. Removing replica before deletion.")
                            client.remove_regions_from_replication(SecretId=secret_name, RemoveReplicaRegions=[region])
                            logger.info(f"Replica removed successfully for secret {region_name} => {secret_name} in region {region}.")
                        else:
                            logger.warning(f"Failed to delete secret {region_name} => {secret_name} in region {region}. Replicas still exist.")

                    # After removing replicas, describe the secret again to get updated replication status
                    response = client.describe_secret(SecretId=secret_name)
                    replication_status_list = response.get('ReplicationStatus')
                    if replication_status_list is not None:
                        all_replicas_removed = all(replication_status.get('Status') != 'InSync' for replication_status in replication_status_list)
                    else:
                        all_replicas_removed = True

                    if all_replicas_removed:
                        logger.info(f"All replicas of secret {region_name} => {secret_name} have been successfully removed. Deleting the secret.")
                        client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
                        logger.success(f"Successfully deleted secret: {region_name} => {secret_name}")
                    else:
                        logger.warning(f"Failed to delete secret {region_name} => {secret_name}. Replicas still exist.")
                else:
                    # logger.warning(f"No replication status found for secret {region_name} => {secret_name}.")
                    # If there are no replicas, try deleting the secret directly
                    client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
                    logger.success(f"Successfully deleted secret: {region_name} => {secret_name}")
                    
            except client.exceptions.ResourceNotFoundException:
                logger.warning(f"Secret {secret_name} not found. It might have been already deleted.")
            except Exception as e:
                logger.error(f"Error deleting secret {region_name} => {secret_name}: {e}")





# def delete_all_secrets(region_name):
#     client = boto3.client('secretsmanager', region_name=region_name)
#     paginator = client.get_paginator('list_secrets')

#     for page in paginator.paginate():
#         for secret in page['SecretList']:
#             secret_name = secret['Name']
#             try:
#                 try:
#                     client.cancel_rotate_secret(SecretId=secret_name)
#                     logger.info(f"Rotation cancelled for secret:{region_name}=> {secret_name}")
#                 except client.exceptions.ResourceNotFoundException:
#                     pass

#                 client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
#                 logger.success(f"Successfully deleted secret:{region_name}=> {secret_name}")

#             except client.exceptions.ResourceNotFoundException:
#                 logger.warning(f"Secret {secret_name} not found. It might have been already deleted.")
#             except Exception as e:
#                 logger.error(f"Error deleting secret {region_name}=>{secret_name}: {e}")


def delete_amis(region_name, aws_account_id):
    ec2 = boto3.client('ec2', region_name=region_name)

    response = ec2.describe_images(Owners=[aws_account_id])
    amis = response['Images']

    if not amis:
        return
    logger.warning(f"EC2 AMIs Found: count({len(amis)})")
    for ami in amis:
        ami_id = ami['ImageId']
        logger.warning(f"Deregistering AMI: {region_name}=>{ami_id}")

        try:
            ec2.deregister_image(ImageId=ami_id)
            logger.success(f"Successfully deregistered AMI:{region_name}=>{ami_id}")

            # Optionally, delete associated snapshots
            for device in ami.get('BlockDeviceMappings', []):
                snapshot_id = device.get('Ebs', {}).get('SnapshotId')
                if snapshot_id:
                    logger.info(f"Deleting snapshot: {snapshot_id} associated with AMI:{region_name}=>{ami_id}")
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    logger.success(f"Successfully deleted snapshot:{region_name}=>{snapshot_id}")

        except ec2.exceptions.ClientError as e:
            logger.error(f"Error deregistering AMI {ami_id}: {e}")


def delete_key_pairs(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    response = ec2.describe_key_pairs()
    key_pairs = response['KeyPairs']

    if not key_pairs:
        return
    logger.warning(f"EC2 Key Pairs Found: count({len(key_pairs)})")
    for kp in key_pairs:
        key_name = kp['KeyName']
        logger.warning(f"Deleting key pair: {key_name}")

        try:
            ec2.delete_key_pair(KeyName=key_name)
            logger.success(f"Successfully deleted key pair:{region_name}=>{key_name}")
        except ec2.exceptions.ClientError as e:
            logger.error(f"Error deleting key pair {region_name}=>{key_name}: {e}")


def delete_launch_templates(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    response = ec2.describe_launch_templates()
    launch_templates = response['LaunchTemplates']

    if not launch_templates:
        return
    logger.warning(f"EC2 Launch templates Found: count({len(launch_templates)})")

    for lt in launch_templates:
        lt_id = lt['LaunchTemplateId']
        lt_name = lt['LaunchTemplateName']
        logger.warning(f"Deleting launch template: {region_name}=>{lt_name} ({lt_id})")

        try:
            ec2.delete_launch_template(LaunchTemplateId=lt_id)
            logger.success(f"Successfully deleted launch template: {region_name}=>{lt_name} ({lt_id})")
        except ec2.exceptions.ClientError as e:
            logger.error(f"Error deleting launch template {region_name}=>{lt_name} ({lt_id}): {e}")


def delete_efs_file_systems(region_name):
    efs = boto3.client('efs', region_name=region_name)
    file_systems = efs.describe_file_systems()["FileSystems"]

    if not file_systems:
        return

    logger.warning(f"Namespaces Found: count({len(file_systems)})")
    for fs in file_systems:
        fs_id = fs['FileSystemId']
        try:
            efs.delete_file_system(FileSystemId=fs_id)
            while True:
                try:
                    efs.describe_file_systems(FileSystemId=fs_id)
                    time.sleep(5)
                except efs.exceptions.FileSystemNotFound:
                    logger.success(f"EFS file system {fs_id} deleted successfully.")
                    break

        except efs.exceptions.FileSystemInUse:
            logger.warning(f"Cannot delete EFS file system {fs_id} as it's in use.")
        except efs.exceptions.BadRequest:
            logger.error(f"Bad request for EFS file system {fs_id}. Check request parameters.")
        except efs.exceptions.InternalServerError:
            logger.error(f"Internal server error when deleting EFS file system {fs_id}.")
        except efs.exceptions.FileSystemNotFound:
            logger.info(f"EFS file system {fs_id} not found. It might have been already deleted.")
        except Exception as e:
            logger.error(f"Error deleting EFS file system {fs_id}: {e}")


def delete_redshift_serverless_namespace(region_name):
    client = boto3.client('redshift-serverless', region_name=region_name)
    
    if 'list_namespaces' in dir(client):
        try:
            response = client.list_namespaces()
        except Exception as e:
            logger.info(f"Debug: listing namespaces:{region_name} {e}")
            return

        namespaces = response.get('namespaces', [])

        for row in namespaces:
            namespace_name = row.get('namespaceName')
            status = row.get('status')

            if status == 'DELETING':
                logger.info(f"Skipping {namespace_name} as it's already in DELETING status.")
                continue

            if namespace_name is None:
                logger.warning(f"Skipping an entry due to missing namespaceName: {row}")
                continue

            try:
                res = client.delete_namespace(namespaceName=namespace_name)
                res_status = res.get('status')

                if res_status == 'DELETING':
                    logger.success(f"Redshift serverless Namespace Successfully Deleted: {namespace_name}")
                else:
                    logger.warning(f"Unexpected status after deletion request for {namespace_name}: {res_status}")
            except Exception as e:
                logger.error(f"Error deleting Redshift serverless Namespace {namespace_name}: {e}")
                continue
    else:
        logger.error("The method list_namespaces does not exist for the redshift-serverless client.")

def delete_namespaces(region_name):
    client = boto3.client('servicediscovery', region_name=region_name)
    response = client.list_namespaces()
    if len(response["Namespaces"]) < 1:
        # logger.info("No automated backups to delete")
        return
    logger.warning(f"Namespaces Found: count({len(response['Namespaces'])})")
    for namespace in response["Namespaces"]:
        try:

            client.delete_namespace(Id=namespace['Id'])
        except Exception as e:
            logger.error(f"Error deleting Namespace {namespace['Id']}: {e}")
            raise

    logger.success("All Namespaces deleted successfully!")


def delete_db_instance_automated_backups(region_name):
    rds = boto3.client('rds', region_name=region_name)

    res = rds.describe_db_instance_automated_backups()
    if len(res["DBInstanceAutomatedBackups"]) < 1:
        # logger.info("No automated backups to delete")
        return
    logger.warning(f"Automated Backups Found: count({len(res['DBInstanceAutomatedBackups'])})")

    for backup in res["DBInstanceAutomatedBackups"]:
        backup_arn = backup["DBInstanceArn"]
        backup_id = backup["DBInstanceAutomatedBackupsArn"].split(":")[-1]
        logger.info(f"Deleting automated backup {backup_id}")
        try:
            rds.delete_db_instance_automated_backup(
                DbiResourceId=backup_arn,
                DbiResourceIdForRestore=backup_arn,
                BackupRetentionPeriod=0
            )
        except Exception as e:
            logger.error(f"Error deleting automated backup {backup_id}: {e}")
            raise

    logger.success("All automated backups deleted successfully!")


def wait_for_role_deletion(iam, role_name):
    waiter_delay = 5
    max_attempts = 12
    last_response = None

    for _ in range(max_attempts):
        try:
            last_response = iam.get_role(RoleName=role_name)
        except iam.exceptions.NoSuchEntityException:
            return

        time.sleep(waiter_delay)

    raise WaiterError(name="RoleDeletionWaiter", reason="Role deletion waiter timed out", last_response=last_response)


def delete_all_roles():
    iam = boto3.client('iam')
    response = iam.list_roles()

    for role in response['Roles']:
        role_name = role['RoleName']

        if role['Arn'].startswith('arn:aws:iam::aws:role/') or role['Path'].startswith('/aws-service-role/'):
            # logger.info(f"Skipping deletion of protected role: {role_name}")
            continue

        # Detach and delete inline policies
        response_policies = iam.list_role_policies(RoleName=role_name)
        policy_names = response_policies['PolicyNames']

        for policy_name in policy_names:
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)

        # Detach managed policies
        response_attached_policies = iam.list_attached_role_policies(RoleName=role_name)
        attached_policies = response_attached_policies['AttachedPolicies']

        for policy in attached_policies:
            policy_arn = policy['PolicyArn']
            iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        # Remove the role from associated instance profiles
        response_instance_profiles = iam.list_instance_profiles_for_role(RoleName=role_name)
        instance_profiles = response_instance_profiles['InstanceProfiles']

        for instance_profile in instance_profiles:
            instance_profile_name = instance_profile['InstanceProfileName']
            iam.remove_role_from_instance_profile(
                InstanceProfileName=instance_profile_name,
                RoleName=role_name
            )
            time.sleep(1)  # Wait for a second to allow the removal to propagate

        iam.delete_role(RoleName=role_name)

        try:
            wait_for_role_deletion(iam, role_name)
        except WaiterError as e:
            logger.error(f"Failed to delete role: {role_name}. Error: {str(e)}")

    # logger.success("All roles deleted successfully!")


def delete_db_cluster_snapshots(region_name):
    rds = boto3.client('rds', region_name=region_name)

    # Get a list of all DB cluster snapshots
    res = rds.describe_db_cluster_snapshots(SnapshotType='manual')

    # Check if there are any snapshots to delete
    if len(res['DBClusterSnapshots']) < 1:
        # logger.info("No DB cluster snapshots to delete")
        return
    logger.warning(f"DB cluster snapshots found: count({len(res['DBClusterSnapshots'])})")

    # Delete each snapshot
    for snapshot in res['DBClusterSnapshots']:
        snapshot_id = snapshot['DBClusterSnapshotIdentifier']

        # Check if the snapshot is a manual snapshot
        if snapshot['SnapshotType'] == 'manual':
            logger.info(f"Deleting DB cluster snapshot: {snapshot_id}")
            try:
                rds.delete_db_cluster_snapshot(DBClusterSnapshotIdentifier=snapshot_id)
            except Exception as e:
                logger.error(f"Error deleting DB cluster snapshot {snapshot_id}: {e}")
                raise
        else:
            logger.info(f"Skipping automatic DB cluster snapshot: {snapshot_id}")

    logger.success("All manual DB cluster snapshots deleted successfully!")


def delete_all_rds_automated_backups(region_name):
    rds = boto3.client('rds', region_name=region_name)

    marker = None
    while True:
        # Retrieve a batch of automated backups (max 100)
        response = rds.describe_db_instance_automatic_snapshots(MaxRecords=100, Marker=marker)

        # Extract the snapshot identifiers from the response
        snapshot_ids = [snap['DBSnapshotIdentifier'] for snap in response['DBInstanceAutomatedSnapshots']]

        # If no snapshots were found, break out of the loop
        if not snapshot_ids:
            break

        # Delete the snapshots
        for snapshot_id in snapshot_ids:
            try:
                rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
                print(f"Deleted snapshot {snapshot_id}")
            except Exception as e:
                print(f"Error deleting snapshot {snapshot_id}: {e}")

        # Update the marker for the next batch of snapshots (if any)
        marker = response.get('Marker')


def delete_rds_option_groups(region_name):
    rds = boto3.client('rds', region_name=region_name)

    res = rds.describe_option_groups()
    if len(res["OptionGroupsList"]) < 1:
        # logger.info("No Option Groups to delete")
        return
    # logger.warning(f"Option Groups Found: count({len(res['OptionGroupsList'])})")

    for group in res["OptionGroupsList"]:
        group_name = group["OptionGroupName"]
        group_description = group["OptionGroupDescription"]
        if group_description.startswith("Provides a") or group_description.startswith("Default"):
            # logger.info(f"Skipping default Option Group (default option group can not be deleted): {group_name}")
            continue
        logger.info(f"Deleting Option Group: {group_name}")
        try:
            rds.delete_option_group(OptionGroupName=group_name)
        except Exception as e:
            logger.error(f"Error deleting Option Group {group_name}: {e}")
            raise

    # logger.success("All Option Groups deleted successfully!")


def delete_lambda_layers(region_name):
    client = boto3.client('lambda', region_name=region_name)
    response = client.list_layers()
    layers = response['Layers']

    if not layers:
        # logger.info('No Lambda layers found to delete.')
        return
    logger.warning(f'Lambda layers found: {len(layers)}')
    for layer in layers:
        layer_arn = layer['LayerArn']
        logger.warning(f'Deleting Lambda layer: {layer_arn}')
        try:
            client.delete_layer_version(
                LayerName=layer_arn.split(':')[-1],
                VersionNumber=layer['LatestMatchingVersion']['Version']
            )
        except Exception as e:
            logger.error(f'Error deleting Lambda layer: {e}')
            raise

    logger.success(f'Successfully deleted {len(layers)} Lambda layers.')


def delete_db_cluster_parameter_groups(region_name):
    rds = boto3.client('rds', region_name=region_name)
    res = rds.describe_db_cluster_parameter_groups()
    if len(res["DBClusterParameterGroups"]) < 1:
        # logger.info("No DB Cluster Parameter Groups to delete")
        return
    # logger.warning(f"DB Cluster Parameter Groups Found: count({len(res['DBClusterParameterGroups'])})")
    for group in res['DBClusterParameterGroups']:
        if not group["DBClusterParameterGroupName"].startswith("default"):
            rds.delete_db_cluster_parameter_group(DBClusterParameterGroupName=group["DBClusterParameterGroupName"])
            logger.success(f"Successfully Deleted DB cluster parameter group {group['DBClusterParameterGroupName']}")


def delete_rds_parameter_groups(region_name):
    rds = boto3.client('rds', region_name=region_name)

    res = rds.describe_db_parameter_groups()
    if len(res["DBParameterGroups"]) < 1:
        # logger.info("No DB Parameter Groups to delete")
        return
    # logger.warning(f"DB Parameter Groups Found: count({len(res['DBParameterGroups'])})")

    for group in res["DBParameterGroups"]:
        group_name = group["DBParameterGroupName"]
        if group_name.startswith("default"):
            # logger.info(
            #     f"Skipping default RDS parameter group (default parameter groups can not be deleted): {group_name}")
            continue
        logger.info(f"Deleting DB Parameter Group: {group_name}")
        try:
            rds.delete_db_parameter_group(DBParameterGroupName=group_name)
        except Exception as e:
            logger.error(f"Error deleting DB Parameter Group {group_name}: {e}")
            raise

    # logger.success("All DB Parameter Groups deleted successfully!")


def delete_rds_subnet_groups(region_name):
    rds = boto3.client('rds', region_name=region_name)

    res = rds.describe_db_subnet_groups()
    if len(res["DBSubnetGroups"]) < 1:
        # logger.info("No DB Subnet Groups to delete")
        return
    logger.warning(f"DB Subnet Groups Found: count({len(res['DBSubnetGroups'])})")

    for group in res["DBSubnetGroups"]:
        group_name = group["DBSubnetGroupName"]
        logger.warning(f"Deleting DB Subnet Group: {group_name}")
        try:
            rds.delete_db_subnet_group(DBSubnetGroupName=group_name)
            logger.success(f"DB Subnet Group deleted successfully!: {group_name}")
        except Exception as e:
            logger.error(f"Error deleting DB Subnet Group {group_name}: {e}")
            raise


def delete_ecs_tasks(region_name):
    ecs_client = boto3.client('ecs', region_name=region_name)
    status_list = ['ACTIVE', 'INACTIVE']
    for status in status_list:
        response = ecs_client.list_task_definitions(status=status)

        task_arns = response['taskDefinitionArns']
        if len(task_arns) < 1:
            # logger.info("No ECS task Found")
            continue
        logger.warning(f"ECR task Found: count({len(task_arns)})")
        for task_arn in task_arns:
            logger.warning('Deregister ECS task: {}'.format(task_arn))
            ecs_client.deregister_task_definition(taskDefinition=task_arn)

        ecs_client.delete_task_definitions(
            taskDefinitions=task_arns
        )
        logger.warning('Deleting ECS tasks: {}'.format(len(task_arns)))
        logger.success('All ECS tasks in region {} have been deleted.'.format(region_name))


def delete_ecs_cluster(region_name):
    ecs_client = boto3.client('ecs', region_name=region_name)

    # Get list of cluster arns
    response = ecs_client.list_clusters()
    cluster_arns = response['clusterArns']
    if len(cluster_arns) < 1:
        return

    for cluster_arn in cluster_arns:
        # list services for each cluster
        services = ecs_client.list_services(cluster=cluster_arn)

        for service in services['serviceArns']:
            # update the service to have 0 desired tasks
            ecs_client.update_service(cluster=cluster_arn, service=service, desiredCount=0)

            # delete the service
            ecs_client.delete_service(cluster=cluster_arn, service=service)

        # list tasks for each cluster
        tasks = ecs_client.list_tasks(cluster=cluster_arn)

        for task in tasks['taskArns']:
            # stop the task
            response = ecs_client.stop_task(cluster=cluster_arn, task=task)

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.success(f"Stopped task: {task} successfully in cluster: {cluster_arn}")
            else:
                logger.error(f"Failed to stop task: {task} in cluster: {cluster_arn}")

    logger.warning(f"ECR cluster Found: count({len(cluster_arns)})")

    # Delete each cluster and wait for completion
    while len(cluster_arns) > 0:
        for cluster_arn in cluster_arns:
            ecs_client.delete_cluster(cluster=cluster_arn)
            logger.warning('Deleting ECS cluster: {}'.format(cluster_arn))

        time.sleep(10)

        # Get updated list of cluster arns
        response = ecs_client.list_clusters()
        cluster_arns = response['clusterArns']

    logger.success('All ECS clusters in region {} have been deleted.'.format(region_name))


# def delete_ecs_cluster(region_name):
#     ecs_client = boto3.client('ecs', region_name=region_name)
#
#     # Get list of cluster arns
#     response = ecs_client.list_clusters()
#     cluster_arns = response['clusterArns']
#     if len(cluster_arns) < 1:
#         # logger.info("No ECR cluster Found")
#         return
#
#     for cluster_arn in cluster_arns:
#         # list tasks for each cluster
#         tasks = ecs_client.list_tasks(cluster=cluster_arn)
#
#         for task in tasks['taskArns']:
#             # stop the task
#             response = ecs_client.stop_task(cluster=cluster_arn, task=task)
#
#             if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#                 logger.success(f"Stopped task: {task} successfully in cluster: {cluster_arn}")
#             else:
#                 logger.error(f"Failed to stop task: {task} in cluster: {cluster_arn}")
#
#     logger.warning(f"ECR cluster Found: count({len(cluster_arns)})")
#     # Delete each cluster and wait for completion
#     while len(cluster_arns) > 0:
#         for cluster_arn in cluster_arns:
#             ecs_client.delete_cluster(cluster=cluster_arn)
#             logger.warning('Deleting ECS cluster: {}'.format(cluster_arn))
#
#         time.sleep(10)
#
#         # Get updated list of cluster arns
#         response = ecs_client.list_clusters()
#         cluster_arns = response['clusterArns']
#
#     logger.success('All ECS clusters in region {} have been deleted.'.format(region_name))


def delete_ecr(region_name):
    ecr_client = boto3.client('ecr', region_name=region_name)

    # Get list of repository names
    response = ecr_client.describe_repositories()
    repositories = response['repositories']
    if len(repositories) < 1:
        # logger.info("No ECR repository Found")
        return
    logger.warning(f"ECR repository Found: count({len(repositories)})")
    # Delete each repository and wait for completion
    while len(repositories) > 0:
        for repository in repositories:
            repository_name = repository['repositoryName']
            ecr_client.delete_repository(repositoryName=repository_name, force=True)
            logger.warning('Deleting ECR repository: {}'.format(repository_name))

        time.sleep(10)

        # Get updated list of repository names
        response = ecr_client.describe_repositories()
        repositories = response['repositories']


# def delete_s3_buckets(region_name):
#     # Create S3 client
#     s3 = boto3.client('s3', region_name=region_name)
#
#     # Get list of all buckets in region
#     response = s3.list_buckets()
#     buckets = response['Buckets']
#
#     if len(buckets) < 1:
#         #logger.info("No S3 Buckets Found")
#         return
#     logger.warning(f"S3 Buckets Found: count({len(buckets)})")
#     # Delete each bucket
#     for bucket in buckets:
#         try:
#             # Delete all objects in the bucket
#             response = s3.list_objects_v2(Bucket=bucket['Name'])
#             objects = response.get('Contents', [])
#             if len(objects) > 0:
#                 keys = [{'Key': obj['Key']} for obj in objects]
#                 s3.delete_objects(Bucket=bucket['Name'], Delete={'Objects': keys})
#                 logger.warning(f"All objects in bucket {bucket['Name']} deleted successfully.")
#                 waiter = s3.get_waiter('object_not_exists')
#                 waiter.wait(Bucket=bucket['Name'], Key=keys[0]['Key'])
#
#             # Delete the bucket
#             s3.delete_bucket(Bucket=bucket['Name'])
#             waiter = s3.get_waiter('bucket_not_exists')
#             waiter.wait(Bucket=bucket['Name'])
#             logger.success(f"Successfully Deleted Bucket: {bucket['Name']}")
#
#         except Exception as e:
#             logger.error(f"Error deleting bucket {bucket['Name']}: {e}")

def delete_s3_buckets():
    # Create S3 client
    s3 = boto3.client('s3')

    # Get list of all buckets in region
    response = s3.list_buckets()
    buckets = response['Buckets']

    if len(buckets) < 1:
        # logger.info("No S3 Buckets Found")
        return
    logger.warning(f"S3 Buckets Found: count({len(buckets)})")

    # Delete each bucket
    for bucket in buckets:
        try:
            # Delete all objects and all object versions in the bucket
            paginator = s3.get_paginator('list_object_versions')
            for page in paginator.paginate(Bucket=bucket['Name']):
                if 'Versions' in page:
                    for version in page['Versions']:
                        s3.delete_object(Bucket=bucket['Name'], Key=version['Key'], VersionId=version['VersionId'])
                if 'DeleteMarkers' in page:
                    for delete_marker in page['DeleteMarkers']:
                        s3.delete_object(Bucket=bucket['Name'], Key=delete_marker['Key'],
                                         VersionId=delete_marker['VersionId'])

            # Delete the bucket
            s3.delete_bucket(Bucket=bucket['Name'])
            waiter = s3.get_waiter('bucket_not_exists')
            waiter.wait(Bucket=bucket['Name'])
            logger.success(f"Successfully Deleted Bucket: {bucket['Name']}")

        except Exception as e:
            logger.error(f"Error deleting bucket {bucket['Name']}: {e}")


def delete_dynamodb_tables(region_name):
    dynamodb = boto3.client('dynamodb', region_name=region_name)

    tables = dynamodb.list_tables()['TableNames']

    if not tables:
        return
    logger.warning(f"DynamoDB table Found: count({len(tables)})")
    for table in tables:
        logger.warning(f"Deleting DynamoDB table: {table}")

        try:
            dynamodb.delete_table(TableName=table)
            logger.success(f"Successfully deleted DynamoDB table: {table}")
        except dynamodb.exceptions.ResourceNotFoundException:
            logger.warning(f"DynamoDB table {table} not found. It might have been already deleted.")
        except Exception as e:
            logger.error(f"Error deleting DynamoDB table {table}: {e}")


def delete_dynamodb_backups(region_name):
    dynamodb = boto3.client('dynamodb', region_name=region_name)

    backups = dynamodb.list_backups()['BackupSummaries']

    if not backups:
        return
    logger.warning(f"DynamoDB table Found: count({len(backups)})")
    for backup in backups:
        backup_arn = backup['BackupArn']
        logger.info(f"Deleting DynamoDB backup: {backup_arn}")

        try:
            dynamodb.delete_backup(BackupArn=backup_arn)
            logger.success(f"Successfully deleted DynamoDB backup: {backup_arn}")
        except dynamodb.exceptions.ResourceNotFoundException:
            logger.warning(f"DynamoDB backup {backup_arn} not found. It might have been already deleted.")
        except Exception as e:
            logger.error(f"Error deleting DynamoDB backup {backup_arn}: {e}")


def delete_all_kinesis_data_streams(region_name):
    kinesis = boto3.client('kinesis', region_name=region_name)
    # Get all Kinesis Data Streams in the region
    streams = kinesis.list_streams()
    if len(streams['StreamNames']) < 1:
        # logger.info("No Kinesis Data Streams to delete")
        return

    logger.warning(f"Kinesis Data Streams Found: count({len(streams['StreamNames'])})")
    waiter = kinesis.get_waiter('stream_not_exists')
    # Delete each Kinesis Data Stream
    for stream_name in streams['StreamNames']:
        logger.warning(f"Deleting Kinesis Data Stream {stream_name}")
        try:
            kinesis.delete_stream(StreamName=stream_name, EnforceConsumerDeletion=True)
            waiter.wait(StreamName=stream_name)
            logger.success(f"Kinesis Data Stream Successfully deleted: {stream_name}")
        except Exception as e:
            logger.error(f"Error deleting Kinesis Data Stream {stream_name}: {e}")
            raise


def delete_firehose_delivery_streams(region_name):
    firehose = boto3.client('firehose', region_name=region_name)

    streams = firehose.list_delivery_streams()

    for stream_name in streams['DeliveryStreamNames']:
        logger.info(f"Deleting delivery stream: {stream_name}")
        firehose.delete_delivery_stream(DeliveryStreamName=stream_name)

        # Poll for the delivery stream to be deleted
        stream_deleted = False
        while not stream_deleted:
            try:
                firehose.describe_delivery_stream(DeliveryStreamName=stream_name)
            except firehose.exceptions.ResourceNotFoundException:
                stream_deleted = True
                logger.success(f"Delivery stream {stream_name} deleted.")
            else:
                logger.info(f"Delivery stream: {stream_name} still exists. Waiting for deletion to complete.")
                time.sleep(1)


def delete_redshift_subnet_groups(region_name):
    redshift = boto3.client('redshift', region_name=region_name)
    subnet_groups = redshift.describe_cluster_subnet_groups()

    if len(subnet_groups['ClusterSubnetGroups']) < 1:
        # logger.info("No Redshift subnet group")
        return
    logger.warning(f'Deleting Redshift subnet groups: count({len(subnet_groups["ClusterSubnetGroups"])}')
    # Loop through each subnet group and delete it
    for group in subnet_groups['ClusterSubnetGroups']:
        subnet_group_name = group['ClusterSubnetGroupName']
        logger.warning(f"Deleting subnet group: {subnet_group_name}")
        redshift.delete_cluster_subnet_group(ClusterSubnetGroupName=subnet_group_name)

        # Poll for the subnet group to be deleted
        subnet_group_deleted = False
        while not subnet_group_deleted:
            try:
                redshift.describe_cluster_subnet_groups(
                    ClusterSubnetGroupName=subnet_group_name
                )
                time.sleep(1)
            except redshift.exceptions.ClusterSubnetGroupNotFoundFault:
                subnet_group_deleted = True

        logger.success(f"Redshift subnet group {subnet_group_name} deleted successfully")


def delete_all_redshift_clusters(region_name):
    client = boto3.client('redshift', region_name=region_name)

    # Describe all Redshift clusters
    response = client.describe_clusters()

    # Check if there are any clusters to delete
    if len(response['Clusters']) == 0:
        # logger.info("No Redshift clusters found")
        return
    logger.warning(f'Deleting Redshift clusters: count({len(response["Clusters"])})')
    # Delete each Redshift cluster
    for cluster in response['Clusters']:
        cluster_identifier = cluster['ClusterIdentifier']
        logger.warning(f"Deleting Redshift cluster:{cluster_identifier} (~ 90 seconds)")
        try:
            waiter = client.get_waiter('cluster_deleted')
            client.delete_cluster(
                ClusterIdentifier=cluster_identifier,
                SkipFinalClusterSnapshot=True
            )
            # Wait for cluster to be deleted

            waiter.wait(
                ClusterIdentifier=cluster_identifier,
                WaiterConfig={
                    'Delay': 10,
                    'MaxAttempts': 60
                }
            )
            logger.success(f"Redshift cluster {cluster_identifier} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting Redshift cluster {cluster_identifier}: {str(e)}")


def delete_all_firehose_streams(region_name):
    # Create a Kinesis Firehose client
    firehose_client = boto3.client('firehose', region_name=region_name)

    # List all delivery streams
    response = firehose_client.list_delivery_streams()

    if len(response['DeliveryStreamNames']) < 1:
        # logger.info("No Firehose Delivery Streams")
        return False
    logger.warning(f'Deleting Firehose Delivery Streams: count({len(response["Clusters"])}')

    # Delete each delivery stream
    waiter = firehose_client.get_waiter('stream_deleted')
    for stream_name in response['DeliveryStreamNames']:
        firehose_client.delete_delivery_stream(DeliveryStreamName=stream_name)
        waiter.wait(StreamName=stream_name)

    # Check for more delivery streams and delete them as well
    while 'NextDeliveryStreamName' in response:
        response = firehose_client.list_delivery_streams(
            ExclusiveStartDeliveryStreamName=response['NextDeliveryStreamName'])
        for stream_name in response['DeliveryStreamNames']:
            firehose_client.delete_delivery_stream(DeliveryStreamName=stream_name)

        # Wait for delivery streams to be deleted
        for stream_name in response['DeliveryStreamNames']:
            waiter.wait(StreamName=stream_name)


def delete_peering_connection(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    peering_connections = ec2.describe_vpc_peering_connections(Filters=[
        {
            'Name': 'status-code',
            'Values': [
                'provisioning',
                'active',
                'rejected',
                'expired',
                'failed'
            ]
        },
    ])

    pc_count = len(peering_connections['VpcPeeringConnections'])

    if pc_count < 1:
        # logger.info("No VpcPeeringConnections")
        return False

    for peering_connection in peering_connections['VpcPeeringConnections']:
        logger.info("Peering Connection found !!!: " + peering_connection['VpcPeeringConnectionId'])
        logger.info("Trying to delete ...")
        try:
            ec2.delete_vpc_peering_connection(
                VpcPeeringConnectionId=peering_connection['VpcPeeringConnectionId']
            )

            waiter = ec2.get_waiter('vpc_peering_connection_deleted')
            try:
                waiter.wait(Filters=[{'Name': 'status-code', 'Values': ['deleted']}])
                logger.success('Peering Connection deleted: ' + peering_connection['VpcPeeringConnectionId'])
            except botocore.exceptions.WaiterError as e:
                logger.critical('Error waiting for Peering Connection to be deleted:', e)
                logger.critical('Failed while deleting Peering Connection:',
                                peering_connection['VpcPeeringConnectionId'])

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidStateTransition':
                logger.warning(
                    f'Skipped deleting Peering Connection: {peering_connection["VpcPeeringConnectionId"]} due to Invalid State Transition')
            else:
                raise


def delete_load_balancer_listener(region_name):
    client = boto3.client('elbv2', region_name=region_name)

    res = client.describe_load_balancers()

    lb_count = len(res["LoadBalancers"])

    if lb_count < 1:
        # logger.info("No LoadBalancer Listener")
        return False

    for lb in res['LoadBalancers']:
        listeners_response = client.describe_listeners(LoadBalancerArn=lb['LoadBalancerArn'])

        for listener in listeners_response['Listeners']:
            logger.info('Checking listener:', listener['ListenerArn'])

            client.delete_listener(ListenerArn=listener['ListenerArn'])

            # Custom waiting logic
            while True:
                try:
                    client.describe_listeners(ListenerArn=listener['ListenerArn'])
                    time.sleep(5)  # Wait for 5 seconds before checking again
                except client.exceptions.ListenerNotFoundException:
                    logger.error('Listener deleted:', listener['ListenerArn'])
                    break  # Listener has been deleted, so break the loop
                except Exception as e:
                    logger.critical('Error waiting for listener to be deleted:', e)
                    break  # Some other error occurred, so break the loop


def delete_load_balancer(region_name):
    delete_load_balancer_listener(region_name)

    client = boto3.client('elbv2', region_name=region_name)

    res = client.describe_load_balancers()

    rt_count = len(res["LoadBalancers"])
    # logger.info(pt(), json.dumps(res, indent=4, sort_keys=True, default=str))
    # res = client.describe_target_groups()
    # logger.info(pt(), json.dumps(res, indent=4, sort_keys=True, default=str))
    if rt_count < 1:
        # logger.info("No LoadBalancer")
        return False
    for x in res["LoadBalancers"]:

        if x.get("LoadBalancerArn") is not None:
            res1 = client.delete_load_balancer(
                LoadBalancerArn=x.get("LoadBalancerArn")
            )

            logger.info(json.dumps(res1, indent=2, sort_keys=True, default=str))


# def delete_target_groups(region_name):
#     try:
#         client = boto3.client('elbv2', region_name=region_name)
#
#         res = client.describe_target_groups()
#
#         rt_count = len(res["TargetGroups"])
#         if rt_count < 1:
#             # logger.info("No target_groups")
#             return False
#
#         for x in res["TargetGroups"]:
#             if x.get("TargetGroupArn") is not None:
#                 client.delete_target_group(TargetGroupArn=x.get("TargetGroupArn"))
#                 waiter = client.get_waiter('target_group_deleted')
#                 waiter.wait(TargetGroupArns=[x.get("TargetGroupArn")])
#                 logger.info(f"Successfully Deleted TargetGroup: {x.get('TargetGroupArn')}")
#
#     except Exception as e:
#         logger.error(f"An error occurred while deleting target groups in region {region_name}: {e}")
def delete_target_groups(region_name):
    try:
        client = boto3.client('elbv2', region_name=region_name)

        res = client.describe_target_groups()

        rt_count = len(res["TargetGroups"])
        if rt_count < 1:
            return False

        for x in res["TargetGroups"]:
            if x.get("TargetGroupArn") is not None:
                client.delete_target_group(TargetGroupArn=x.get("TargetGroupArn"))

                # Retry deletion until the target group is deleted
                for _ in range(30):  # retry for 5 minutes
                    try:
                        client.describe_target_groups(TargetGroupArns=[x.get("TargetGroupArn")])
                    except client.exceptions.TargetGroupNotFoundException:
                        logger.info(f"Successfully Deleted TargetGroup: {x.get('TargetGroupArn')}")
                        break
                    time.sleep(10)  # wait 10 seconds before retrying

    except Exception as e:
        logger.error(f"An error occurred while deleting target groups in region {region_name}: {e}")


def delete_route_tables(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    route_tables = ec2.describe_route_tables()['RouteTables']
    if len(route_tables) < 1:
        # logger.info("No RouteTables")
        return False
    logger.warning("RouteTables FOUND !!!")
    for table in route_tables:
        for association in table['Associations']:
            if not association['Main']:
                ec2.disassociate_route_table(AssociationId=association['RouteTableAssociationId'])
                logger.success(f"Successfully disassociated route table: {association['RouteTableAssociationId']}")
        if not table['Associations'] or ('Main' in table['Associations'][0] and not table['Associations'][0]['Main']):
            ec2.delete_route_table(RouteTableId=table['RouteTableId'])
            logger.success(f"Successfully deleted route table: {table['RouteTableId']}")
        # else:
        #     logger.warning(f"Cannot delete main route table: {table['RouteTableId']}")


def delete_network_interface(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    network_interfaces = ec2.describe_network_interfaces()
    if len(network_interfaces['NetworkInterfaces']) < 1:
        # logger.info("No NetworkInterfaces")
        return False
    for network_interface in network_interfaces['NetworkInterfaces']:
        ni_id = network_interface['NetworkInterfaceId']
        logger.warning(f"Deleting network interface {ni_id}...")

        try:
            ec2.delete_network_interface(NetworkInterfaceId=ni_id)
            logger.success(f"Network interface {ni_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting network interface: {ni_id} : {e}")


def delete_sg(region_name: str, dry_run: bool = False) -> bool:
    """
    Delete non-default security groups in the specified AWS region.

    Parameters:
    - region_name (str): The AWS region where the security groups are located.
    - dry_run (bool): If True, checks whether you have the required permissions to delete security groups without actually deleting them.

    Returns:
    - bool: Returns True if the operation is successful, False otherwise.
    """
    # Input validation
    if not isinstance(region_name, str) or not region_name:
        logger.error("Invalid region name")
        return False

    # Initialize AWS EC2 client
    try:
        ec2 = boto3.client('ec2', region_name=region_name)
    except Exception as e:
        logger.error(f"Failed to initialize EC2 client: {e}")
        return False

    # Describe security groups
    try:
        res = ec2.describe_security_groups()
    except Exception as e:
        logger.error(f"Failed to describe security groups: {e}")
        return False

    # Check if there are security groups to delete
    if not res.get("SecurityGroups"):
        return False

    # Delete non-default security groups
    for sg in res["SecurityGroups"]:
        if sg["GroupName"] != "default":
            try:
                if not dry_run:
                    ec2.delete_security_group(GroupId=sg['GroupId'])
                    logger.info(f"Security group {sg['GroupId']} deleted successfully")
                else:
                    logger.info(f"Dry run: Security group {sg['GroupId']} would be deleted")
            except Exception as e:
                logger.error(f"Failed to delete security group {sg['GroupId']}: {e}")

    return True


def delete_sgr(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    # Get all security groups in the specified region
    response = ec2.describe_security_groups()
    # logger.info(json.dumps(response, indent=4, sort_keys=True, default=str))
    # exit()

    # Loop through all security groups and delete all inbound and outbound rules
    for security_group in response['SecurityGroups']:
        group_id = security_group['GroupId']
        if len(security_group['IpPermissions']) > 0:
            logger.warning(f"Deleting all ingress rule for security group {group_id}")
            ec2.revoke_security_group_ingress(GroupId=group_id, IpPermissions=security_group['IpPermissions'])

        if len(security_group['IpPermissionsEgress']) > 0:
            logger.warning(f"Deleting all Egress rule for security group {group_id}")
            ec2.revoke_security_group_egress(GroupId=group_id, IpPermissions=security_group['IpPermissionsEgress'])

        response = ec2.describe_security_groups(GroupIds=[group_id])
        if response['SecurityGroups'][0]['IpPermissions'] or response['SecurityGroups'][0]['IpPermissionsEgress']:
            logger.critical(f"ERROR: Security group rules for {group_id} were not deleted!")



def get_cognito_role_name(region_name):
    """
    Retrieve the IAM role name used by Amazon Cognito to send SMS messages.
    """
    iam_client = boto3.client('iam', region_name=region_name)
    response = iam_client.list_roles()
    for role in response['Roles']:
        if 'AmazonCognito' in role['RoleName']:
            return role['RoleName']
    return None

def get_sns_caller_arn(region_name):
    """
    Retrieve the ARN of the IAM role used by Amazon Cognito to send SMS messages.
    """
    iam_client = boto3.client('iam', region_name=region_name)
    role_name = get_cognito_role_name(region_name)
    if role_name:
        response = iam_client.get_role(RoleName=role_name)
        return response['Role']['Arn']
    else:
        return None

def get_sns_region():
    """
    Retrieve the AWS region where your SNS topic is located.
    """
    return boto3.session.Session().region_name




def delete_cognito_user_pools(region_name: str):
    client = boto3.client('cognito-idp', region_name=region_name)
    user_pools = client.list_user_pools(MaxResults=60)['UserPools']

    for pool in user_pools:
        pool_id = pool['Id']
        try:
            # Retrieve current settings
            pool_details = client.describe_user_pool(UserPoolId=pool_id)
            current_auto_verified_attributes = pool_details['UserPool'].get('AutoVerifiedAttributes', [])

            # If phone_number is in AutoVerifiedAttributes, remove it to avoid the SMS configuration requirement
            # new_auto_verified_attributes = [attr for attr in current_auto_verified_attributes if attr != 'phone_number']

            # Apply updated settings
            client.update_user_pool(
                UserPoolId=pool_id,
                AutoVerifiedAttributes=current_auto_verified_attributes,
                DeletionProtection='INACTIVE'
                # SmsConfiguration can be added here if needed
            )

            logger.info(
                f"Updated settings and disabled deletion protection for User Pool: {pool_id} in region {region_name}")
            client.delete_user_pool(UserPoolId=pool_id)
            logger.success(f"Successfully deleted User Pool: {pool_id} in region {region_name}")
        except Exception as e:
            logger.error(f"Failed to delete User Pool {pool_id} in region {region_name}: {e}")


def delete_cognito_identity_pools(region_name: str):
    """
    Delete all Cognito Identity Pools in a specified AWS region.

    Parameters:
    - region_name (str): AWS region name.
    """
    client = boto3.client('cognito-identity', region_name=region_name)

    # List all identity pools in the specified region
    identity_pools = client.list_identity_pools(MaxResults=60)['IdentityPools']

    # Iterate over each identity pool and delete it
    for pool in identity_pools:
        pool_id = pool['IdentityPoolId']
        try:
            client.delete_identity_pool(IdentityPoolId=pool_id)
            logger.success(f"Successfully deleted Identity Pool: {pool_id} in region {region_name}")
        except Exception as e:
            logger.error(f"Failed to delete Identity Pool {pool_id} in region {region_name}: {e}")


def delete_sns_topics(region_name: str):
    sns_client = boto3.client('sns', region_name=region_name)

    def get_all_topics():
        """Retrieve all SNS topics in the specified region, handling pagination."""
        next_token = None
        while True:
            if next_token:
                response = sns_client.list_topics(NextToken=next_token)
            else:
                response = sns_client.list_topics()
            yield from response.get('Topics', [])
            next_token = response.get('NextToken')
            if not next_token:
                break

    for topic in get_all_topics():
        topic_arn = topic['TopicArn']
        try:
            sns_client.delete_topic(TopicArn=topic_arn)
            logger.info(f"Successfully deleted SNS Topic: {topic_arn} in region {region_name}")
        except sns_client.exceptions.NotFoundException:
            logger.warning(f"SNS Topic {topic_arn} not found in region {region_name}")
        except Exception as e:
            logger.error(f"Failed to delete SNS Topic {topic_arn} in region {region_name}: {e}")


def delete_vpc(region_name):
    max_attempts = 10
    ec2 = boto3.client('ec2', region_name=region_name)
    res = ec2.describe_vpcs()
    vpc_count = len(res["Vpcs"])
    if vpc_count < 1:
        # logger.info("No Vpcs")
        return False
    logger.warning("VPC FOUND !!!")
    vpc_ids = [vpc['VpcId'] for vpc in res['Vpcs']]

    # Delete all VPCs in the region
    for vpc_id in vpc_ids:
        attempts = 0
        while attempts < max_attempts:
            try:
                ec2.delete_vpc(VpcId=vpc_id)
            except ec2.exceptions.ClientError as e:
                if 'DependencyViolation' in str(e):
                    logger.warning(f"Cannot delete VPC {vpc_id} in {region_name} yet. Retrying in 10 seconds.")
                    time.sleep(10)
                else:
                    logger.warning(f"Error deleting VPC {vpc_id} in {region_name}: {e}")
            try:
                ec2.describe_vpcs(VpcIds=[vpc_id])
            except ec2.exceptions.ClientError as e:
                if 'InvalidVpcID.NotFound' in str(e):
                    logger.success(f"VPC {vpc_id} deleted successfully in region {region_name}")
                    break
                else:
                    logger.warning(f"Error describing VPC {vpc_id} in {region_name}: {e}")
            attempts += 1
        if attempts == max_attempts:
            logger.critical(f"Could not delete VPC {vpc_id} in region {region_name} after {attempts} attempts.")


def delete_subnets(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    response = ec2.describe_subnets()
    subnets = response['Subnets']
    if len(subnets) < 1:
        return False

    subnet_ids = [subnet['SubnetId'] for subnet in subnets]

    for subnet_id in subnet_ids:
        logger.warning(f"Deleting subnet {subnet_id}")
        try:
            logger.warning(f"Waiting for subnets to be deleted in {region_name}")
            ec2.delete_subnet(SubnetId=subnet_id)
            logger.success("All subnets have been deleted.")
        except Exception as e:
            logger.error(f"Subnet deletion failed with exception: {str(e)}")


def delete_endpoint(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    endpoints = ec2.describe_vpc_endpoints()
    if len(endpoints["VpcEndpoints"]) < 1:
        # logger.info("No VpcEndpoints")
        return False
    logger.warning("VpcEndpoints FOUND !!!")
    for endpoint in endpoints['VpcEndpoints']:
        ec2.delete_vpc_endpoints(VpcEndpointIds=[endpoint['VpcEndpointId']])
        # waiter = ec2.get_waiter('vpc_endpoint_deleted')
        # waiter.wait(VpcEndpointIds=[endpoint['VpcEndpointId']])
        logger.warning(f"VpcEndpoint successfully deleted VpcEndpointId: {endpoint['VpcEndpointId']}")


# def delete_db_instances(region):
#     # create a client for RDS in the specified region
#     rds_client = boto3.client('rds', region_name=region)
#
#     # get a list of all RDS instances
#     res = rds_client.describe_db_instances()
#
#     if len(res['DBInstances']) < 1:
#         #logger.info("No RDS instance")
#         return
#     logger.warning(f"RDS instance Found: count({len(res['DBInstances'])})")
#
#     # iterate through each instance and delete it
#     for instance in res['DBInstances']:
#         instance_identifier = instance['DBInstanceIdentifier']
#         rds_client.delete_db_instance(DBInstanceIdentifier=instance_identifier, SkipFinalSnapshot=True)
#
#         # wait for the instance to be deleted
#         logger.warning(f"Waiting for RDS instance {instance_identifier} to be deleted...(apx 9 minutes)")
#         try:
#             rds_client.get_waiter('db_instance_deleted').wait(DBInstanceIdentifier=instance_identifier)
#             logger.success(f"RDS instance {instance_identifier} deleted successfully.")
#         except WaiterError as e:
#             logger.error(f"Error deleting RDS instance {instance_identifier}: {e}")

# def delete_db_instances(region):
#     # create a client for RDS in the specified region
#     rds_client = boto3.client('rds', region_name=region)
#
#     # get a list of all RDS instances
#     res = rds_client.describe_db_instances()
#
#     # filter instances that are in the 'available' state
#     available_instances = [instance for instance in res['DBInstances'] if instance['DBInstanceStatus'] == 'available']
#
#     if len(available_instances) < 1:
#         # logger.info("No RDS instance")
#         return
#     logger.warning(f"RDS instance Found: count({len(available_instances)})")
#
#     # iterate through each instance and delete it
#     for instance in available_instances:
#         instance_identifier = instance['DBInstanceIdentifier']
#         rds_client.delete_db_instance(DBInstanceIdentifier=instance_identifier, SkipFinalSnapshot=True)
#
#         # wait for the instance to be deleted
#         logger.warning(f"Waiting for RDS instance {instance_identifier} to be deleted...(apx 9 minutes)")
#         try:
#             rds_client.get_waiter('db_instance_deleted').wait(DBInstanceIdentifier=instance_identifier)
#             logger.success(f"RDS instance {instance_identifier} deleted successfully.")
#         except WaiterError as e:
#             logger.error(f"Error deleting RDS instance {instance_identifier}: {e}")
def delete_db_instances(region):
    rds_client = boto3.client('rds', region_name=region)

    try:
        # Fetching RDS instances
        res = rds_client.describe_db_instances()
    except ClientError as e:
        logger.error(f"Error fetching RDS instances: {e}")
        return

    # Filtering available instances
    available_instances = [instance for instance in res['DBInstances'] if instance['DBInstanceStatus'] == 'available']

    if not available_instances:
        # logger.info("No available RDS instance found.")
        return

    logger.warning(f"Found {len(available_instances)} available RDS instance(s).")

    for instance in available_instances:
        instance_identifier = instance['DBInstanceIdentifier']

        # Attempt to delete with retries
        for attempt in range(max_retries):
            try:
                # Disabling deletion protection
                rds_client.modify_db_instance(
                    DBInstanceIdentifier=instance_identifier,
                    DeletionProtection=False
                )
                logger.info(f"Deletion protection disabled for RDS instance {instance_identifier}.")

                # Deleting instance
                rds_client.delete_db_instance(
                    DBInstanceIdentifier=instance_identifier,
                    SkipFinalSnapshot=True
                )
                logger.info(f"Initiated deletion for RDS instance {instance_identifier}.")

                # Waiting for deletion to complete
                rds_client.get_waiter('db_instance_deleted').wait(DBInstanceIdentifier=instance_identifier)
                logger.success(f"RDS instance {instance_identifier} deleted successfully.")
                break  # Break out of the retry loop if deletion is successful

            except ClientError as e:
                if "DeletionProtection" in str(e):
                    logger.warning(
                        f"Deletion protection still active for RDS instance {instance_identifier}. Retrying...")
                elif "InvalidParameterCombination" in str(e) and attempt < max_retries - 1:
                    logger.warning(
                        f"Temporary issue deleting RDS instance {instance_identifier}. Retrying in 60 seconds...")
                    time.sleep(60)  # Waiting before retrying
                else:
                    logger.error(f"Error deleting RDS instance {instance_identifier}: {e}")
                    break  # Break out of the retry loop if a non-retryable error occurs


def delete_all_notebook_instances(region_name):
    client = boto3.client('sagemaker', region_name=region_name)

    # Get list of notebook instances
    response = client.list_notebook_instances()

    if 'NotebookInstances' not in response or len(response['NotebookInstances']) < 1:
        # logger.info("No notebook instances to delete.")
        return
    logger.info(f"Notebook instances found count ({len(response['NotebookInstances'])}).")
    # Iterate over each notebook instance
    for notebook in response['NotebookInstances']:
        notebook_name = notebook['NotebookInstanceName']
        notebook_status = notebook['NotebookInstanceStatus']

        if notebook_status in ['Stopping', 'Stopped', 'Failed']:
            # If the notebook instance is already stopped or in the process of stopping, delete it
            client.delete_notebook_instance(NotebookInstanceName=notebook_name)
            logger.success(f"Deleted notebook instance: {notebook_name}")
        elif notebook_status in ['InService', 'Pending', 'Updating']:
            # If the notebook instance is running, stop it first before deleting
            client.stop_notebook_instance(NotebookInstanceName=notebook_name)
            logger.info(f"Stopping notebook instance: {notebook_name}")
            waiter = client.get_waiter('notebook_instance_stopped')
            waiter.wait(NotebookInstanceName=notebook_name)
            client.delete_notebook_instance(NotebookInstanceName=notebook_name)
            logger.info(f"Deleted notebook instance: {notebook_name}")

    logger.success(f"Finished deleting all notebook instances in region {region_name}.")


def delete_rds(region_name):
    rds = boto3.client('rds', region_name=region_name)
    waiter1 = rds.get_waiter('db_cluster_available')
    waiter2 = rds.get_waiter('db_cluster_deleted')

    res = rds.describe_db_clusters(IncludeShared=False)
    dbc_count = len(res["DBClusters"])
    if dbc_count < 1:
        return
    logger.warning(f'DB Clusters Found: count({len(res["DBClusters"])})')
    for x in res["DBClusters"]:
        logger.warning(f'Deleting DBCluster:{x["DBClusterIdentifier"]}')
        if x.get("DeletionProtection"):
            logger.info("Updating DBCluster DeletionProtection to False. Please wait ...")
            rds.modify_db_cluster(
                DBClusterIdentifier=x["DBClusterIdentifier"],
                ApplyImmediately=True,
                DeletionProtection=False
            )
            waiter1.wait(
                DBClusterIdentifier=x["DBClusterIdentifier"],
                IncludeShared=True,
                WaiterConfig={
                    'Delay': 1,
                    'MaxAttempts': 900
                }
            )
            logger.info("Updating DBCluster DeletionProtection to False Finished.")

    waiter3 = rds.get_waiter('db_instance_deleted')
    res2 = rds.describe_db_instances()
    dbi_count = len(res2["DBInstances"])
    if dbi_count > 0:
        for x in res2["DBInstances"]:
            try:
                logger.warning(
                    "deleting DB Instance: " + x["DBInstanceIdentifier"] + ". Please wait... (apx 5-12 minutes)")
                rds.delete_db_instance(
                    DBInstanceIdentifier=x["DBInstanceIdentifier"],
                    SkipFinalSnapshot=True,
                    DeleteAutomatedBackups=True
                )
                waiter3.wait(
                    DBInstanceIdentifier=x["DBInstanceIdentifier"],
                    WaiterConfig={
                        'Delay': 1,
                        'MaxAttempts': 1200
                    }
                )
                logger.success("deleting DB Instance: " + x["DBInstanceIdentifier"] + ". Finished")
            except rds.exceptions.InvalidDBInstanceStateFault:
                logger.info("DB Instance: " + x["DBInstanceIdentifier"] + " is already being deleted, continuing...")
                continue

    if dbc_count > 0:
        for x in res["DBClusters"]:
            logger.warning("Deleting DBCluster: " + x["DBClusterIdentifier"] + ". Please wait ... (apx 80 seconds)")
            rds.delete_db_cluster(
                DBClusterIdentifier=x["DBClusterIdentifier"],
                SkipFinalSnapshot=True
            )
            waiter2.wait(
                DBClusterIdentifier=x["DBClusterIdentifier"],
                IncludeShared=True,
                WaiterConfig={
                    'Delay': 1,
                    'MaxAttempts': 900
                }
            )
            logger.success("Deleting DBCluster: " + x["DBClusterIdentifier"] + ". Finished")


def delete_lambda_functions(region_name):
    lambda_client = boto3.client('lambda', region_name=region_name)

    response = lambda_client.list_functions()
    function_names = [function['FunctionName'] for function in response['Functions']]

    if len(function_names) < 1:
        # logger.info("No Lambda Function")
        return
    logger.warning(f"Lambda Function Found: Count({len(function_names)})")
    # Detach the Lambda function from its VPC (if it is attached)
    for function_name in function_names:
        try:
            response = lambda_client.get_function_configuration(FunctionName=function_name)
            if 'VpcConfig' in response:
                vpc_config = response['VpcConfig']
                if vpc_config['VpcId']:
                    logger.warning(f"Detaching function {function_name} from VPC...")
                    lambda_client.update_function_configuration(
                        FunctionName=function_name,
                        VpcConfig={
                            'SecurityGroupIds': [],
                            'SubnetIds': []
                        }
                    )
                    waiter = lambda_client.get_waiter('function_updated')
                    waiter.wait(FunctionName=function_name)
                    logger.success(f"Function {function_name} detached from VPC.")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Function {function_name} not found.")
            else:
                logger.error(f"Error detaching function {function_name} from VPC: {e}")
        # Delete the Lambda function

    try:
        # Create a Boto3 client for AWS Lambda in the specified region.
        lambda_client = boto3.client('lambda', region_name=region_name)

        # Get a list of all Lambda functions in the region.
        functions = lambda_client.list_functions()['Functions']

        # Loop through the functions and delete each one.
        for function in functions:
            lambda_client.delete_function(FunctionName=function['FunctionName'])

        # Wait until all the functions have been deleted.
        while True:
            response = lambda_client.list_functions()['Functions']
            if not response:
                break

        logger.success(f"All ({len(functions)}) Lambda functions deleted from {region_name}")

    except Exception as e:
        logger.error(f"An error occurred while deleting Lambda functions in {region_name}: {e}")


def delete_internet_gateway(region_name, timeout=180):
    ec2 = boto3.client('ec2', region_name=region_name)

    res = ec2.describe_internet_gateways()
    if len(res["InternetGateways"]) < 1:
        return
    logger.warning(f"Internet Gateway Found: count({len(res['InternetGateways'])})")

    def wait_for_deletion(igw_id2):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                logger.error(f"Timed out waiting for Internet Gateway {igw_id2} to be deleted")
                break

            try:
                ec2.describe_internet_gateways(InternetGatewayIds=[igw_id2])
            except ec2.exceptions.ClientError as e2:
                error_code = e2.response['Error']['Code']
                if error_code in ('InvalidInternetGatewayId.Malformed', 'InvalidInternetGatewayID.NotFound'):
                    logger.success(f"Internet Gateway {igw_id2} deleted successfully")
                    break
                else:
                    logger.error(f"Unexpected error while checking Internet Gateway {igw_id2}: {e2}")
                    break
            except Exception as e2:  # Catch other exceptions
                logger.error(f"Unexpected error while checking Internet Gateway {igw_id2}: {e2}")
                break

            logger.info(
                f"Waiting for Internet Gateway {igw_id2} to be deleted... (elapsed time: {elapsed_time:.2f} seconds)")
            time.sleep(3)

    for igw in res["InternetGateways"]:
        igw_id = igw["InternetGatewayId"]
        for att in igw["Attachments"]:
            vpc_id = att["VpcId"]

            try:
                ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id, DryRun=False)
            except ec2.exceptions.ClientError as e:
                logger.error(f"Error detaching Internet Gateway {igw_id} from VPC {vpc_id}: {e}")
                continue  # Skip to the next attachment or IGW instead of raising an exception

        try:
            ec2.delete_internet_gateway(InternetGatewayId=igw_id, DryRun=False)
        except ec2.exceptions.ClientError as e:
            logger.error(f"Error deleting Internet Gateway {igw_id}: {e}")
            continue  # Skip to the next IGW instead of raising an exception

        # Wait for the Internet Gateway to be deleted
        wait_for_deletion(igw_id)


def delete_instances(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    # Get all running instances_in the region
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}])
    if len(instances['Reservations']) < 1:
        # logger.info("No running instances to terminate")
        return
    logger.warning(f"Instances Found: count({len(instances['Reservations'])})")
    waiter = ec2.get_waiter('instance_terminated')
    # Terminate each instance
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            logger.warning(f"Terminating instance {instance_id}")
            try:
                ec2.terminate_instances(InstanceIds=[instance_id])
            except Exception as e:
                logger.error(f"Error terminating instance {instance_id}: {e}")
                raise

    waiter.wait(InstanceIds=[i['InstanceId'] for r in instances['Reservations'] for i in r['Instances']])
    logger.success("All instances terminated successfully")


def delete_efs(region_name):
    efs = boto3.client('efs', region_name=region_name)

    file_systems = efs.describe_file_systems()

    # Delete all EFS file systems and their associated mount targets
    for fs in file_systems['FileSystems']:
        file_system_id = fs['FileSystemId']

        # Get all mount targets for the file system
        try:
            mount_targets = efs.describe_mount_targets(FileSystemId=file_system_id)
        except ClientError as e:
            logger.info(f'Error describing mount targets for {file_system_id}: {e}')
            continue

        # Delete all mount targets for the file system
        for mt in mount_targets['MountTargets']:
            mount_target_id = mt['MountTargetId']

            try:

                efs.delete_mount_target(MountTargetId=mount_target_id)
                waiter = efs.get_waiter('mount_target_deleted')
                waiter.wait(MountTargetId=mount_target_id)
                logger.success(f'Mount target {mount_target_id} deleted successfully.')
            except ClientError as e:
                logger.info(f'Error deleting mount target {mount_target_id}: {e}')

        # Delete the file system
        try:

            efs.delete_file_system(FileSystemId=file_system_id)
            waiter = efs.get_waiter('file_system_deleted')
            waiter.wait(FileSystemId=file_system_id)
            logger.success(f'File system {file_system_id} deleted successfully.')
        except ClientError as e:
            logger.error(f'Error deleting file system {file_system_id}: {e}')


def delete_elastic_ip(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    res = ec2.describe_addresses(DryRun=False)
    eip_count = len(res["Addresses"])
    if eip_count < 1:
        # logger.info("No Elastic IP Addresses")
        return False
    logger.warning("Elastic IP Addresses FOUND !!!")
    for x in res["Addresses"]:
        if x.get("AssociationId") is not None:
            logger.info("disassociate_address", x["PublicIp"])
            ec2.disassociate_address(
                AssociationId=x["AssociationId"],
                DryRun=False
            )

    for x in res["Addresses"]:
        if x.get("AllocationId") is not None:
            logger.info("release_address", x["PublicIp"])
            res2 = ec2.release_address(
                AllocationId=x["AllocationId"],
                NetworkBorderGroup=x["NetworkBorderGroup"],
                DryRun=False
            )

            if res2["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.success('Successfully release_address')


def delete_ecs_clusters(region_name):
    ecs = boto3.client('ecs', region_name=region_name)
    response = ecs.list_clusters()

    cluster_arns = response['clusterArns']

    cc = len(cluster_arns)
    if cc < 1:
        # logger.info("No ECS cluster")
        return False

    while response.get('nextToken'):
        response = ecs.list_clusters(nextToken=response['nextToken'])
        cluster_arns.extend(response['clusterArns'])

    for cluster_arn in cluster_arns:
        logger.info(f"Stopping tasks in ECS cluster: {cluster_arn}")
        tasks = ecs.list_tasks(cluster=cluster_arn)['taskArns']
        while tasks:
            task_arn = tasks.pop()
            ecs.stop_task(cluster=cluster_arn, task=task_arn)

            waiter = ecs.get_waiter('tasks_stopped')
            waiter.wait(
                cluster=cluster_arn,
                tasks=[task_arn],
                WaiterConfig={
                    'Delay': 5,
                    'MaxAttempts': 30
                }
            )
            logger.success(f"tasks stopped: {task_arn}")

        logger.info(f"Deleting ECS cluster: {cluster_arn}")
        ecs.delete_cluster(cluster=cluster_arn)

        waiter = ecs.get_waiter('cluster_deleted')
        waiter.wait(
            cluster=cluster_arn,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 30
            }
        )
        logger.info(f"Waiter finished for ECS cluster: {cluster_arn}")


def delete_all_sqs(region_name):
    sqs_client = boto3.client('sqs', region_name=region_name)

    try:
        response = sqs_client.list_queues()
    except Exception as e:
        logger.error(f"Error listing SQS queues in region {region_name}: {e}")
        return

    queue_urls = response.get('QueueUrls')

    if queue_urls:
        logger.warning(f"Deleting queue start for region: {region_name}")
        # Delete each queue
        for queue_url in queue_urls:
            try:
                sqs_client.delete_queue(QueueUrl=queue_url)
                logger.info(f"Deleted queue: {queue_url}")
            except Exception as e:
                logger.error(f"Error deleting queue {queue_url}: {e}")
                continue
        logger.success(f"Deleting queue end for region: {region_name}")


if __name__ == "__main__":
    run()
