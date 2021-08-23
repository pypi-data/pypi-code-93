import os
import boto3
import sys
import pytz
import datetime
import argparse
import configparser
import subprocess
from prettytable import PrettyTable


def get_asg_details(all_asg, cluster_name):
    """
    Get all the autoscale groups which match tag key/val
    """

    stdout_msg(f"Searching for all the aws asg associated with cluster: {cluster_name}")
    asg_list = []
    cluster_asg = False
    node_group_asg = False

    for i in range(len(all_asg)):
        all_tags = all_asg[i]["Tags"]
        for j in range(len(all_tags)):
            if (
                all_tags[j]["Key"] == f"kubernetes.io/cluster/{cluster_name}"
                and all_tags[j]["Value"] == "owned"
            ):
                cluster_asg = True
            if all_tags[j]["Key"] == f"eks:nodegroup-name":
                node_group_asg = True

            if cluster_asg and node_group_asg:
                cluster_asg = False
                node_group_asg = False
                if not all_asg[i]["Instances"]:
                    asg_list.append(
                        {
                            "AutoScalingGroupName": all_asg[i]["AutoScalingGroupName"],
                            "MinSize": all_asg[i]["MinSize"],
                            "MaxSize": all_asg[i]["MaxSize"],
                            "DesiredCapacity": all_asg[i]["DesiredCapacity"],
                            "AvailabilityZones": all_asg[i]["AvailabilityZones"],
                        }
                    )
                else:
                    asg_list.append(
                        {
                            "AutoScalingGroupName": all_asg[i]["AutoScalingGroupName"],
                            "InstanceType": all_asg[i]["Instances"][0]["InstanceType"],
                            "MinSize": all_asg[i]["MinSize"],
                            "MaxSize": all_asg[i]["MaxSize"],
                            "DesiredCapacity": all_asg[i]["DesiredCapacity"],
                            "AvailabilityZones": all_asg[i]["AvailabilityZones"],
                        }
                    )

    return asg_list


def get_timezone(region):
    """
    Get timezone mapped to aws region
    """

    tz = "UTC"

    region_tz = {
        "us-east-2": "US/Eastern",
        "ap-southeast-2": "Australia/Sydney",
        "eu-central-1": "CET",
    }

    if region in region_tz:
        tz = region_tz[region]

    return tz


def delete_scheduled_action(asg_client, asg_name, scheduled_action_name):
    """
    Delete scheduled action
    """

    response = asg_client.delete_scheduled_action(
        AutoScalingGroupName=asg_name, ScheduledActionName=scheduled_action_name
    )


def get_scheduled_actions(asg_client, asg_name, max_size=None):
    """
    Get scheduled action details
    """

    scheduled_action_list = []

    response = asg_client.describe_scheduled_actions(AutoScalingGroupName=f"{asg_name}")

    for i in response["ScheduledUpdateGroupActions"]:
        if max_size is None and i["MaxSize"] > 0:
            scheduled_action_list.append(
                {
                    "ScheduledActionName": i["ScheduledActionName"],
                    "Recurrence": i["Recurrence"],
                    "StartTime": i["StartTime"],
                    "MinSize": i["MinSize"],
                    "MaxSize": i["MaxSize"],
                    "DesiredCapacity": i["DesiredCapacity"],
                }
            )
        elif max_size is not None and i["MaxSize"] == 0:
            scheduled_action_list.append(
                {
                    "ScheduledActionName": i["ScheduledActionName"],
                    "Recurrence": i["Recurrence"],
                    "StartTime": i["StartTime"],
                    "MinSize": i["MinSize"],
                    "MaxSize": i["MaxSize"],
                    "DesiredCapacity": i["DesiredCapacity"],
                }
            )

    return scheduled_action_list


def put_scheduled_action(asg_client, asg_name, scheduled_action, updated_start_time):
    """
    Create scheduled actions
    """

    response = asg_client.put_scheduled_update_group_action(
        AutoScalingGroupName=asg_name,
        ScheduledActionName=scheduled_action["ScheduledActionName"],
        Recurrence=scheduled_action["Recurrence"],
        MinSize=scheduled_action["MinSize"],
        MaxSize=scheduled_action["MaxSize"],
        DesiredCapacity=scheduled_action["DesiredCapacity"],
        StartTime=updated_start_time,
    )


def scale_out_asg(asg_client, asg_name, max_size, min_size, desired_capacity):
    """
    Scale out aws autoscalegroup
    """

    respose = asg_client.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
    )


def scale_in_asg(asg_client, asg_name, max_size=0, min_size=0, desired_capacity=0):
    """
    Scale in aws autoscalegroup
    """

    respose = asg_client.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="pcpt-cde",
        description="Utility tool for the pingcloud cde environment",
    )

    parser.add_argument(
        "-p",
        dest="profile_name",
        type=str,
        required=True,
        help="aws profile name, example: coral-stage, coral-stage-eu1",
    )
    parser.add_argument(
        "-s",
        dest="show",
        action="store_true",
        help="show environment details",
    )
    parser.add_argument(
        "-d",
        dest="hours_to_add",
        action="store",
        type=int,
        help="delay start of existing scale-in scheduler by number of hours: range(1,720), example: 720 for 30 days",
    )
    parser.add_argument(
        "-o",
        dest="scale_out",
        action="store_true",
        help="scale-out worker node asg, retrives scale-out values from the existing scheduler",
    )
    parser.add_argument(
        "-i",
        dest="scale_in",
        action="store_true",
        help="scale-in worker node asg, sets min:max to 0:0",
    )
    parser.add_argument("-v", action="version", version="0.5")

    args = parser.parse_args()

    if args.hours_to_add and (args.scale_out or args.scale_in):
        print("Cannot continue, can not use -d with other parameter")
        sys.exit(1)

    if args.scale_out and (args.hours_to_add or args.scale_in):
        print("Cannot continue, can not use -o with other parameter")
        sys.exit(1)

    if args.scale_in and (args.hours_to_add or args.scale_out):
        print("Cannot continue, can not use -i with other parameter")
        sys.exit(1)

    if args.hours_to_add:
        hours_to_add = args.hours_to_add
        if hours_to_add < 1 or hours_to_add > 720:
            print(
                "Cannot continue, value for -d option should within the range(1,720)."
            )
            sys.exit(1)
    else:
        hours_to_add = 0

    if args.scale_out:
        scale_out = 1
    else:
        scale_out = 0

    if args.scale_in:
        scale_in = 1
    else:
        scale_in = 0

    profile_name = args.profile_name

    ssm_operation = True

    # Set aws asg operation to true of corresponding args are set
    if args.scale_in or args.hours_to_add or args.scale_out or args.show:
        ssm_operation = False

    # Check aws configuration
    aws_config = get_aws_config(profile_name)
    if "?" in profile_name:
        splitted = profile_name.split("?")
        profile_initial = None
        if splitted[0]:
            profile_initial = splitted[0]
        elif splitted[1]:
            profile_initial = splitted[1]

        profile_table = PrettyTable()
        profile_table.field_names = ["Profile Name"]
        for profile in aws_config:
            if profile_initial is None:
                profile_table.add_row([profile])
            else:
                if profile.startswith(profile_initial):
                    profile_table.add_row([profile])

        print(profile_table)
        sys.exit(0)

    if aws_config is None:
        print(
            "Please check your aws configuration file, check aws-configuration section in README for further details."
        )
        sys.exit(1)

    # Execute saml2aws for ssm session
    saml = start_saml_session(aws_config)
    if saml:
        sys.exit(1)

    try:
        # Get boto3 session
        session = boto3.session.Session(profile_name=aws_config["profile"])

        if ssm_operation:
            # Get management server node id
            instance_id = get_instance_id(session, "management-server")
            if instance_id:
                start_session(aws_config, instance_id)
            else:
                print("ERROR: Unable to find instance with tag: management-server")
                sys.exit(1)

        else:
            asg_table = PrettyTable()
            eks_table = PrettyTable()
            s3_table = PrettyTable()
            elb_table = PrettyTable()

            # aws loadbalancer details
            elb_list = get_elb(session, aws_config)
            elb_table.field_names = ["Service", "Scheme", "State", "Type", "Load Balancer DNS Name"]

            for elb in elb_list:
                elb_table.add_row(
                    [
                        elb["Service"],
                        elb["Scheme"],
                        elb["State"],
                        elb["Type"],
                        elb["DNSName"],
                    ]
                )

            # aws eks cluster details
            eks_cluster = describe_cluster(session, aws_config)
            eks_table.field_names = ["Cluster Name", "Status", "Version", "created on"]
            if eks_cluster is not None:
                eks_table.add_row(
                    [
                        eks_cluster["name"],
                        eks_cluster["status"],
                        eks_cluster["version"],
                        eks_cluster["createdAt"],
                    ]
                )
            # aws ssm details
            backup_bucket = get_ssm_parameter(
                session, "/pcpt/service/storage/backup/bucketname"
            )
            log_bucket = get_ssm_parameter(
                session, "/pcpt/service/storage/logs/bucketname"
            )
            s3_table.field_names = [
                "Purpose",
                "S3 Bucket Name",
            ]
            if backup_bucket is not None and log_bucket is not None:
                s3_table.add_row(["Backup", backup_bucket])
                s3_table.add_row(["Log", log_bucket])
            # aws worker node asg details
            asg_client = session.client("autoscaling")
            response = asg_client.describe_auto_scaling_groups()
            all_asg = response["AutoScalingGroups"]

            asg_list = get_asg_details(all_asg, aws_config["cluster_name"])

            asg_table.field_names = [
                "WorkerNode asg name",
                "InstanceType",
                "Min",
                "Max",
                "Desired",
                "Scale-in action name",
                "Scale-in action start datetime (UTC)",
            ]
            if not asg_list:
                print(
                    f"Cannot continue, unable to find autoscale groups in this region {aws_config['region']} for cluster {aws_config['cluster_name']}"
                )
                sys.exit(1)

            for asg in asg_list:
                scale_in_action_list = get_scheduled_actions(
                    asg_client, asg["AutoScalingGroupName"], 0
                )
                scale_out_action_list = get_scheduled_actions(
                    asg_client, asg["AutoScalingGroupName"]
                )
                if hours_to_add and not scale_in_action_list:
                    print(
                        f"Skipping, unable to find scale in scheduled action for asg: {asg}"
                    )

                for scale_in_action in scale_in_action_list:
                    if "InstanceType" in asg:
                        asg_table.add_row(
                            [
                                asg["AutoScalingGroupName"],
                                asg["InstanceType"],
                                asg["MinSize"],
                                asg["MaxSize"],
                                asg["DesiredCapacity"],
                                scale_in_action["ScheduledActionName"],
                                scale_in_action["StartTime"],
                            ]
                        )
                    else:
                        asg_table.add_row(
                            [
                                asg["AutoScalingGroupName"],
                                "N/A",
                                asg["MinSize"],
                                asg["MaxSize"],
                                asg["DesiredCapacity"],
                                scale_in_action["ScheduledActionName"],
                                scale_in_action["StartTime"],
                            ]
                        )
                    if hours_to_add:
                        pytz_utc = pytz.timezone("UTC")
                        current_date_time = datetime.datetime.now(pytz_utc)
                        hours_added = datetime.timedelta(hours=hours_to_add)

                        updated_date_time = current_date_time + hours_added

                        delete_scheduled_action(
                            asg_client,
                            asg["AutoScalingGroupName"],
                            scale_in_action["ScheduledActionName"],
                        )

                        put_scheduled_action(
                            asg_client,
                            asg["AutoScalingGroupName"],
                            scale_in_action,
                            updated_date_time,
                        )

                        print(
                            f"Updated, action {scale_in_action['ScheduledActionName']} of asg: {asg['AutoScalingGroupName']} to start on {updated_date_time} current {current_date_time}"
                        )

                if scale_out:
                    if (
                        not scale_out_action_list
                        or not "MaxSize" in scale_out_action_list[0]
                    ):
                        print(
                            f'Skipping - Unable to find existing scale out scheduled action for {asg["AutoScalingGroupName"]}'
                        )
                    else:
                        scale_out_asg(
                            asg_client,
                            asg["AutoScalingGroupName"],
                            scale_out_action_list[0]["MaxSize"],
                            scale_out_action_list[0]["MinSize"],
                            scale_out_action_list[0]["DesiredCapacity"],
                        )
                        print(
                            f"Updated, asg: {asg['AutoScalingGroupName']} to min:max {scale_out_action_list[0]['MaxSize']}:{scale_out_action_list[0]['MinSize']}"
                        )

                if scale_in:
                    scale_in_asg(asg_client, asg["AutoScalingGroupName"])
                    print(f"Updated, asg: {asg['AutoScalingGroupName']} to min:max 0:0")

            if not scale_out and not hours_to_add and not scale_in:
                print(eks_table)
                print(s3_table)
                print(elb_table)
                print(asg_table)

    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)


def get_aws_config(profile_name):
    """
    Check and return aws config
    """

    stdout_msg(f"Checking aws configuration")
    aws_dir = os.path.join(os.environ["HOME"], ".aws")
    credentials_path = os.path.join(aws_dir, "credentials")
    config = configparser.ConfigParser()
    config.read(credentials_path)

    if "?" in profile_name:
        return config

    if profile_name not in config:
        print(f"Unable to find the profile: {profile_name}")
        return None

    if "source_profile" not in config[profile_name]:
        print(f"Unable to find source_profile for profile: {profile_name}")
        return None

    if "region" not in config[profile_name]:
        print(f"Unable to find region set for profile: {profile_name}")
        return None

    cluster_name = profile_name.split("-")[1]
    if cluster_name == "customer":
        cluster_name = "customer-hub"

    aws_config = {
        "profile": profile_name,
        "source_profile": config[profile_name]["source_profile"],
        "region": config[profile_name]["region"],
        "cluster_name": cluster_name,
    }

    return aws_config


def stdout_msg(msg):
    """
    Print message with timestamp.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {msg}")


def start_saml_session(aws_config):
    """
    Execute saml2aws to setup session with platform-hub account.
    """

    stdout_msg("Start saml session")
    cmd = ["saml2aws", "login", "-a", aws_config["source_profile"]]

    env = os.environ.copy()
    env["AWS_PROFILE"] = aws_config["profile"]
    env["AWS_DEFAULT_REGION"] = aws_config["region"]

    p = subprocess.Popen(cmd, env=env)

    stdout = p.communicate()[0]
    exit_code = p.wait()
    if exit_code != 0:
        print(f'\nERROR: when executing: {" ".join(cmd)}')
        print(
            f"Please ref: https://confluence.pingidentity.com/display/PDA/Connect+to+a+CDE+and+CodeCommit+through+SSO+in+command+line"
        )
        return exit_code


def start_session(aws_config, id):
    """
    Execute aws cli to start session with management node
    """

    stdout_msg(f"Starting ssm session with instance: {id}")
    cmd = [
        "aws",
        "--profile",
        aws_config["profile"],
        "ssm",
        "start-session",
        "--target",
        id,
    ]

    env = os.environ.copy()
    env["AWS_PROFILE"] = aws_config["profile"]
    env["AWS_DEFAULT_REGION"] = aws_config["region"]

    p = subprocess.Popen(cmd, env=env)

    while True:
        try:
            p.wait()
            break
        except KeyboardInterrupt as e:
            pass


def get_elb(session, aws_config):
    """
    Retrieve information about an amazon load balancer
    """

    stdout_msg(f'Checking aws load balancer with tag: kubernetes.io/cluster/{aws_config["cluster_name"]}')

    elb_client = session.client("elbv2")

    elb_list = []
    try:
        response = elb_client.describe_load_balancers()
        for elb in response["LoadBalancers"]:
            elb_arn = elb["LoadBalancerArn"]
            tags = elb_client.describe_tags(ResourceArns=[elb_arn])
            for tag_desc in tags["TagDescriptions"]:
                service_name = None
                cluster_tag = False
                for tags in tag_desc["Tags"]:
                    if "kubernetes.io/service-name" in tags["Key"]:
                        service_name = tags["Value"]
                    if (
                        f"kubernetes.io/cluster/{aws_config['cluster_name']}"
                        in tags["Key"]
                    ):
                        cluster_tag = True

                if cluster_tag:
                    elb_list.append(
                        {
                            "DNSName": elb["DNSName"],
                            "Scheme": elb["Scheme"],
                            "Type": elb["Type"],
                            "State": elb["State"]["Code"],
                            "Service": service_name,
                        }
                    )

        return elb_list

    except Exception as e:
        return None


def describe_cluster(session, aws_config):
    """
    Retrieve information about an Amazon EKS cluster
    """

    stdout_msg(f"Checking eks cluster: {aws_config['cluster_name']}")

    eks = session.client("eks")

    try:
        response = eks.describe_cluster(name=aws_config["cluster_name"])
    except Exception as e:
        return None

    return response["cluster"]


def get_ssm_parameter(session, ssm_path):
    """
    Gets the ssm parameter value.
    """

    ssm_client = session.client("ssm")
    response = ssm_client.get_parameter(Name=ssm_path)

    ssm_value = response["Parameter"]["Value"]
    return ssm_value


def get_instance_id(session, tag_val):
    """
    Check and return instance id of management node
    """

    stdout_msg(f"Searching for instance id with tag value suffix: {tag_val}")
    ec2_client = session.client("ec2")
    reservations = ec2_client.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["running"],
            }
        ]
    ).get("Reservations")

    for reservation in reservations:
        for instance in reservation["Instances"]:
            for tag in instance["Tags"]:
                if tag["Value"].endswith(tag_val):
                    return instance["InstanceId"]


if __name__ == "__main__":
    main()
