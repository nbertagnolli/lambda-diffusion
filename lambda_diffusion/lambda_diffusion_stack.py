from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_ecr_assets as ecr_assets,
)
import os
import aws_cdk as cdk


class LambdaDiffusionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a Log Group for the Lambda function
        self.log_group = logs.LogGroup(
            self,
            "DiffusionLambdaLogGroup",
            log_group_name=f"/aws/lambda/DiffusionFunction",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Define the Lambda function with a very simple Hello World response inline
        self.diffusion_fn = _lambda.DockerImageFunction(
            self,
            "DiffusionFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                os.path.join(os.path.dirname(__file__), "lambda"),
                platform=ecr_assets.Platform.LINUX_AMD64,
            ),
            timeout=cdk.Duration.seconds(600),
            memory_size=10240,
            log_group=self.log_group,
        )

        # Create a function URL that we can call to invoke the lambda function.
        self.diffusion_fn_url = self.diffusion_fn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.AWS_IAM
        )

        # Create an IAM user with permissions to invoke the Lambda function
        iam_user = iam.User(self, "LambdaInvokerUser")
        policy = iam.Policy(
            self,
            "LambdaInvokePolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["lambda:InvokeFunctionUrl"],
                    resources=[self.diffusion_fn.function_arn],
                )
            ],
        )
        iam_user.attach_inline_policy(policy)

        # Create access keys for the IAM user
        access_key = iam.AccessKey(
            self, "DiffusionLambdaInvokerUserAccessKey", user=iam_user
        )

        # Store the access keys in Secrets Manager
        secret = secretsmanager.Secret(
            self,
            id="DiffusionLambdaInvokerUserCredentials",
            secret_object_value={
                "AWS_ACCESS_KEY_ID": cdk.SecretValue.unsafe_plain_text(
                    access_key.access_key_id
                ),
                "AWS_SECRET_ACCESS_KEY": access_key.secret_access_key,
            },
        )

        # Write out the lambda url to the stack output for easy access.
        CfnOutput(self, "LambdaUrl", value=self.diffusion_fn_url.url)
        CfnOutput(self, "SecretArn", value=secret.secret_arn)
