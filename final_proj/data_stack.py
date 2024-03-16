from aws_cdk import (
    Duration,
    Stack,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_efs as efs
)
from aws_solutions_constructs import aws_cloudfront_s3 as cfs3
from constructs import Construct

from final_proj.util import settings, Props


class DataStack(Stack):
    aurora_db: rds.ServerlessCluster
    file_system: efs.FileSystem

    def __init__(
        self, scope: Construct, construct_id: str, props: Props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # FILLMEIN: Aurora Serverless Database
        self.aurora_db = rds.ServerlessCluster(
            self,
            f"{settings.PROJECT_NAME}-aurora-serverless",
            engine = rds.DatabaseClusterEngine.AURORA_MYSQL,
            vpc = props.network_vpc,
            default_database_name = "WordpressDatabase",
            vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            credentials = rds.Credentials.from_generated_secret("wordpress",secret_name = "wordpressSecrets")
        )

        efs_security_group = ec2.SecurityGroup(self, "EfsSecurityGroup",
            vpc=props.network_vpc,
            description="Allow efs access",
            allow_all_outbound=True
        )

        efs_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(2049), "allow efs access from the world")

        self.file_system = efs.FileSystem(
            self, "wordpressFS",
            vpc=props.network_vpc,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
            security_group= efs_security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
        )




