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
    Duration,
    aws_efs as efs
)
from constructs import Construct
import json
from final_proj.util import settings, Props


class ComputeStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, props: Props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(
            self, f"{settings.PROJECT_NAME}-cluster", vpc=props.network_vpc
        )


        fargate_task_definition = ecs.FargateTaskDefinition(
            self,
            f"{settings.PROJECT_NAME}-fargate-task-definition",
            cpu = 1024,
            memory_limit_mib = 3072,
            runtime_platform = ecs.RuntimePlatform(operating_system_family=ecs.OperatingSystemFamily.LINUX,cpu_architecture=ecs.CpuArchitecture.ARM64),
        )

        props.data_aurora_db.secret.grant_read(fargate_task_definition.task_role)
        props.file_system.grant_read_write(fargate_task_definition.task_role)
        props.file_system.grant_root_access(fargate_task_definition.task_role)
        props.file_system.grant(fargate_task_definition.task_role, "elasticfilesystem:DescribeMountTargets")
        image = ecs.ContainerImage.from_registry('bitnami/wordpress')

        container = fargate_task_definition.add_container(
            f"{settings.PROJECT_NAME}-app-container",
            container_name = f"{settings.PROJECT_NAME}-app-container",
            image = image,
            logging = ecs.AwsLogDriver(stream_prefix=f"{settings.PROJECT_NAME}-fargate",log_retention=logs.RetentionDays.ONE_WEEK),
            environment = {
                "MARIADB_HOST": props.data_aurora_db.cluster_endpoint.hostname,
                "PHP_MEMORY_LIMIT": "512M",
                "enabled": "false",
                "ALLOW_EMPTY_PASSWORD": "yes",
                "HTTPS":"on"
            },
            secrets={
                'WORDPRESS_DATABASE_USER': ecs.Secret.from_secrets_manager(props.data_aurora_db.secret, field="username"),
                'WORDPRESS_DATABASE_PASSWORD': ecs.Secret.from_secrets_manager(props.data_aurora_db.secret, field="password"),
                'WORDPRESS_DATABASE_NAME': ecs.Secret.from_secrets_manager(props.data_aurora_db.secret, field="dbname"),
            },
            port_mappings = [ecs.PortMapping(container_port = 8080)],
         )

        ap = props.file_system.add_access_point("AccessPoint",
            path="/bitnami/wordpress",
            create_acl=efs.Acl(
                owner_uid="1001",
                owner_gid="1001",
                permissions="755"
            ),
            posix_user=efs.PosixUser(
                uid="1001",
                gid="1001"
            )
        ) #remove

        fargate_task_definition.add_volume(
            name="wordpressVolume",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=props.file_system.file_system_id,
                authorization_config=ecs.AuthorizationConfig(
                    access_point_id=ap.access_point_id, #remove
                    iam="ENABLED"
                ),
                transit_encryption='ENABLED'
            ),
         )

        container_volume_mount_point = ecs.MountPoint(
            read_only=False,
            container_path="/bitnami/wordpress",
            source_volume="wordpressVolume"
        )

        container.add_mount_points(container_volume_mount_point) #remove

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{settings.PROJECT_NAME}-fargate-service",
            cluster = cluster,
            domain_name = f"wordpress.{settings.DNS_ROOT}",
            domain_zone = props.network_hosted_zone,
            certificate = props.network_backend_certificate,
            redirect_http = True,
            task_definition = fargate_task_definition,
            desired_count=2
        )

        fargate_service.service.connections.allow_to(
            props.data_aurora_db, ec2.Port.tcp(3306), "DB access"
        )

        fargate_service.service.connections.allow_to(props.file_system, ec2.Port.tcp(2049),"EFS access")


        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=5
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        
 