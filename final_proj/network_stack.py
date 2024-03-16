from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_ec2 as ec2,
    aws_route53 as r53,
)
from constructs import Construct

from final_proj.util import settings,Props

class NetworkStack(Stack):
    backend_certificate: acm.ICertificate
    frontend_certificate: acm.ICertificate
    vpc: ec2.IVpc

    def __init__(
        self, scope: Construct, construct_id: str, props: Props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # FILLMEIN: VPC
        self.vpc = ec2.Vpc(
            self,
            f"{settings.PROJECT_NAME}-vpc",
            availability_zones = ["us-west-2a","us-west-2b"],
            ip_addresses = ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration = [
                ec2.SubnetConfiguration(
                    name = "Public",
                    subnet_type = ec2.SubnetType.PUBLIC,
                    cidr_mask = 24
                ),
                ec2.SubnetConfiguration(
                    name = "PrivateOutbound",
                    subnet_type = ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask = 24
                ),
                ec2.SubnetConfiguration(
                    name = "PrivateIsolated",
                    subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask = 24
                )
            ]
        )

        self.backend_certificate = acm.Certificate.from_certificate_arn(self, "domainCert", "arn:aws:acm:us-west-2:253577135241:certificate/16a4fa58-1b56-44c9-b414-99707fde37b6")