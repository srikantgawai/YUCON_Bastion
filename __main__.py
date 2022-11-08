"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

size = 't3.micro'

user_data = """#!/bin/bash
echo "Hello, World!" > index.html
nohup python -m SimpleHTTPServer 8080 &
"""

ami = aws.ec2.get_ami(most_recent=True,
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["amzn2-ami-hvm-2.0.20210326.0-x86_64-gp2"],
        ),
    ],
    owners=["918594053736"])

my_vpc = aws.ec2.Vpc.get(resource_name="ACTH-BACKSTAGE-POC-VPC", id="vpc-045c0b4b99e2962cb")

my_subnet =  aws.ec2.get_subnet(filters=[aws.ec2.GetSubnetFilterArgs(
    name="tag:Name",
    values=["ACTH-BACKSTAGE-PUB-SUBNET-AZ1A"],
)])

group = aws.ec2.SecurityGroup('pulumi_allow_8080',
            vpc_id=my_vpc.id,
            description='Enable access to port 8080',
            ingress=[
                { 'protocol': 'tcp', 'from_port': 8080, 'to_port': 8080, 'cidr_blocks': ['0.0.0.0/0'] },
                { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] }
            ])

server = aws.ec2.Instance('bastion',
    instance_type=size,
    vpc_security_group_ids=[group.id],
    ami=ami.id,
    subnet_id=my_subnet.id,
    user_data = user_data,
    tags = { "Name": "Pulumi_Bastion_EC2" },
    )

pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)

