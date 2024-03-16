from aws_cdk import (
    Stack,
    aws_route53 as r53,
)
from constructs import Construct
from final_proj.util import settings, Props

class DnsStack(Stack):
    hosted_zone: r53.IHostedZone

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.hosted_zone = r53.HostedZone.from_hosted_zone_attributes(self,hosted_zone_id="Z04763523A5N05AAFVZW0",zone_name="viralcascade.com",id="wordpressHZ")