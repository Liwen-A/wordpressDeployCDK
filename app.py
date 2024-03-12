#!/usr/bin/env python3
import os

import aws_cdk as cdk

from final_proj.dns_stack import DnsStack
from final_proj.network_stack import NetworkStack
from final_proj.data_stack import DataStack
from final_proj.compute_stack import ComputeStack

from final_proj.util import settings, Props
app = cdk.App()


props = Props()
env = cdk.Environment(account=settings.CDK_DEFAULT_ACCOUNT, region=settings.REGION)

dns_stack = DnsStack(app,  f"{settings.PROJECT_NAME}-dns-stack", env=env)
props.network_hosted_zone = dns_stack.hosted_zone

network_stack = NetworkStack(
    app,  f"{settings.PROJECT_NAME}-network-stack", props, env=env
)
props.network_vpc = network_stack.vpc
props.network_backend_certificate = network_stack.backend_certificate
# props.network_frontend_certificate = network_stack.frontend_certificate

data_stack = DataStack(app, f"{settings.PROJECT_NAME}-data-stack", props, env=env)
props.data_aurora_db = data_stack.aurora_db
props.file_system = data_stack.file_system
# props.data_s3_public_images = data_stack.s3_public_images
# props.data_s3_private_images = data_stack.s3_private_images
# props.data_cloudfront_public_images = data_stack.cloudfront_public_images
# props.data_cloudfront_private_images = data_stack.cloudfront_private_images

compute_stack = ComputeStack(
    app, f"{settings.PROJECT_NAME}-compute-stack", props, env=env
)

data_stack.add_dependency(network_stack)
compute_stack.add_dependency(data_stack)

app.synth()

