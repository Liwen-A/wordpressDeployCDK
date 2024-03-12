import string
from typing import Dict, Optional

from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_route53 as r53,
    aws_s3 as s3,
)


class Settings:
    PROJECT_NAME: "final_proj"
    DNS_ROOT: "viralcascade.com"
    REGION:  "us-west-2"
    CDK_DEFAULT_ACCOUNT: "253577135241"

settings = Settings()

class Props:
    network_vpc: ec2.IVpc
    network_backend_certificate: acm.ICertificate
    network_frontend_certificate: acm.ICertificate
    network_hosted_zone: r53.IHostedZone
    data_aurora_db: rds.ServerlessCluster
    data_s3_public_images: s3.Bucket
    data_s3_private_images: s3.Bucket
    data_cloudfront_public_images: cloudfront.Distribution
    data_cloudfront_private_images: cloudfront.Distribution
