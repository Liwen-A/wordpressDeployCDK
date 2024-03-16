import string
from typing import Dict, Optional

from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_route53 as r53,
    aws_s3 as s3,
    aws_efs as efs
)

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "final-proj"
    DNS_ROOT: str = "viralcascade.com"
    REGION:  str = "us-west-2"
    CDK_DEFAULT_ACCOUNT: str = "253577135241"


settings = Settings()

class Props:
    network_vpc: ec2.IVpc
    network_backend_certificate: acm.ICertificate
    network_frontend_certificate: acm.ICertificate
    network_hosted_zone: r53.IHostedZone
    data_aurora_db: rds.ServerlessCluster
    file_system: efs.FileSystem
