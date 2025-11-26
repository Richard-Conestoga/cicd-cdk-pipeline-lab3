from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct


class CicdCdkPipelineLab3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function
        hello_fn = _lambda.Function(
            self,
            "HelloFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="hello.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment={
                "STAGE": "dev",
            },
        )

        # API Gateway REST API
        api = apigw.RestApi(
            self,
            "HelloApi",
            rest_api_name="HelloApi",
            description="API Gateway fronting Lambda hello function",
            deploy_options=apigw.StageOptions(
                stage_name="dev",
            ),
        )

        # /hello GET -> Lambda
        hello_resource = api.root.add_resource("hello")
        hello_resource.add_method(
            http_method="GET",
            integration=apigw.LambdaIntegration(hello_fn),
        )
