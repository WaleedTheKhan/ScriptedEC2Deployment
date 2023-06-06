
# Created by: Waleed Khan
# Last modified: June 5, 2023
# The following Python script is part of an assignment to programatically deploy EC2 resources using AWS boto3 SDK.

import boto3

# Method to retrieve the subnet IDs in the default VPC
def retr_subnet_ids():
    # Creating an EC2 resource object
    ec2_resource = boto3.resource('ec2')

    # Retrieving all VPCs before finding the default VPC
    all_vpcs = list(ec2_resource.all_vpcs.all())
    default_vpc = None

    # Finding the default VPC from the list of all VPCs
    for vpc in all_vpcs:
        if vpc.is_default:
            default_vpc = vpc
            break
    
    # If the default VPC is retrieved, pulling IDs of all subnets
    if default_vpc:
        subnet_ids = []
        for subnet in default_vpc.subnets.all():
            subnet_ids.append(subnet.id)
        return subnet_ids

# Method to create and deploy an EC2 instance for each retrieved subnet ID
def deploy_ec2_instances(subnet_ids):
    # Creating an EC2 resource object
    ec2_resource = boto3.resource('ec2')

    # Specifying parameters for the EC2 instances to be deployed
    ec2_inst_parameters = {
        'ImageId': 'ami-0806bc468ce3a22ec', # Latest AMI ID retrieved for us-east-1 for TELE20483's Lab 1
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'UserData': '''
        #!/bin/bash
        sudo yum update -y
        sudo yum install -y httpd.x86_64
        sudo systemctl start httpd.service
        sudo systemctl enable httpd.service
        sudo su
        sudo echo "Hi from $(hostname), deployed by Waleed Khan (991645816)" > /var/www/html/index.html'''
    }

    # Empty list to store the instances' information
    ec2_instances_info = []

    for subnet_id in subnet_ids:
        # Passing the current subnet ID to each corresponding EC2 instance's parameters
        ec2_inst_parameters['SubnetId'] = subnet_id

        ec2_instances = ec2_resource.create_instances(**ec2_inst_parameters)

        # Setting the current instance and waiting until it is running to avoid problems
        current_instance = ec2_instances[0]
        current_instance.wait_until_running()
        current_instance.reload()

        cur_instance_info = {
            'InstanceId': current_instance.id,
            'SubnetId': current_instance.subnet_id,
            'PrivateIpAddress': current_instance.private_ip_address
        }

        # Adding the current instance's information to the instances' information list, then returning it collectively
        ec2_instances_info.append(cur_instance_info)

    return ec2_instances_info

# Calling method to retrieve the default VPC's subnet IDs
subnet_ids = retr_subnet_ids()

# Deploying the EC2 instances in each retrieved subnet
ec2_instances_info = deploy_ec2_instances(subnet_ids)

# Outputting the EC2 instance details
for cur_instance_info in ec2_instances_info:
    print('Instance ID: ', cur_instance_info['InstanceId'])
    print('Subnet ID: ', cur_instance_info['SubnetId'])
    print('Private IPv4 Address: ', cur_instance_info['PrivateIpAddress'])
    print('---')