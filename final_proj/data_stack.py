from aws_cdk import (
    Duration,
    Stack,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
)
from aws_solutions_constructs import aws_cloudfront_s3 as cfs3
from constructs import Construct

from cdk.util import settings, Props


class DataStack(Stack):
    aurora_db: rds.ServerlessCluster
    s3_public_images: s3.Bucket
    s3_private_images: s3.Bucket
    cloudfront_public_images: cloudfront.Distribution
    cloudfront_private_images: cloudfront.Distribution

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

        self.file_system = efs.FileSystem(
            self, "WebRoot",
            vpc=props.network_vpc,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode=efs.ThroughputMode.BURSTING,
        )



