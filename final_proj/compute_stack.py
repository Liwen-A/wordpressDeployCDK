from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    aws_ec2 as ec2,
    aws_ecr_assets as ecr_assets,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_ecr as ecr,
    Duration
)
from constructs import Construct
import json
from cdk.util import settings, Props


class ComputeStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, props: Props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(
            self, f"{settings.PROJECT_NAME}-cluster", vpc=props.network_vpc
        )

        wordpress_volume = ecs.Volume(
            name="WebRoot",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=props.file_system.file_system_id
            )
        )

        fargate_task_definition = ecs.FargateTaskDefinition(
            self,
            f"{settings.PROJECT_NAME}-fargate-task-definition",
            cpu = 512,
            memory_limit_mib = 2048,
            runtime_platform = ecs.RuntimePlatform(operating_system_family=ecs.OperatingSystemFamily.LINUX,cpu_architecture=ecs.CpuArchitecture.ARM64),
            volumes = [wordpress_volume]
        )

        container_volume_mount_point = ecs.MountPoint(
            read_only=False,
            container_path="/var/www/html",
            source_volume=wordpress_volume.name
        )

         props.data_aurora_db.secret.grant_read(fargate_task_definition.task_role)

         image = ecs.ContainerImage.fromRegistry('library/wordpress:latest')

         container = fargate_task_definition.add_container(
            f"{settings.PROJECT_NAME}-app-container",
            container_name = f"{settings.PROJECT_NAME}-app-container",
            image = image,
            logging = ecs.AwsLogDriver(stream_prefix=f"{settings.PROJECT_NAME}-fargate",log_retention=logs.RetentionDays.ONE_WEEK),
            environment = {
                "WORDPRESS_DB_HOST": props.data_aurora_db.cluster_endpoint.hostname,
                'WORDPRESS_TABLE_PREFIX': 'wp_'
            },
            secrets={
                'WORDPRESS_DB_USER': ecs.Secret.from_secrets_manager(props.data_aurora_db.secret, field="username"),
                'WORDPRESS_DB_PASSWORD': ecs.Secret.from_secrets_manager(props.data_aurora_dbsecret, field="password"),
                'WORDPRESS_DB_NAME': ecs.Secret.from_secrets_manager(props.data_aurora_db.secret, field="dbname"),
            }
         )

         container.add_mount_points(container_volume_mount_point)

         fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{settings.PROJECT_NAME}-fargate-service",
            cluster = cluster,
            domain_name = f"wordpress.{settings.DNS_ROOT}",
            domain_zone = props.network_hosted_zone,
            certificate = props.network_backend_certificate,
            redirect_http = True,
            task_definition = fargate_task_definition
        )

        fargate_service.target_group.configure_health_check(path="/api/v1/health")

        fargate_service.service.connections.allow_to(
            props.data_aurora_db, ec2.Port.tcp(5432), "DB access"
        )