from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_s3 as s3,
)
from constructs import Construct


class FunFactsBackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the Landmarks table
        landmarks_table = dynamodb.Table(
            self, "Landmark",
            table_name="Landmark",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Define the FunFacts table
        fun_facts_table = dynamodb.Table(
            self, "FunFact",
            table_name="FunFact",
            partition_key=dynamodb.Attribute(name="landmarkId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="funFactId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Define the User table
        user_table = dynamodb.Table(
            self, "User",
            table_name="User",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Define the UserInteractions table
        # user_interactions_table = dynamodb.Table(
        #     self, "UserInteraction",
        #     table_name="UserInteraction",
        #     partition_key=dynamodb.Attribute(name="funFactId", type=dynamodb.AttributeType.STRING),
        #     sort_key=dynamodb.Attribute(name="interactionId", type=dynamodb.AttributeType.STRING),
        #     billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        #     removal_policy=RemovalPolicy.RETAIN
        # )
        #
        # # Add a global secondary index for fetching interactions by user
        # user_interactions_table.add_global_secondary_index(
        #     index_name="userIdIndex",
        #     partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
        #     sort_key=dynamodb.Attribute(name="createdAt", type=dynamodb.AttributeType.STRING),
        #     projection_type=dynamodb.ProjectionType.ALL,
        # )

        # Define an S3 bucket
        bucket = s3.Bucket(self,
                           "FunFactsImages",
                           bucket_name="fun-facts-images",
                           versioned=True,
                           removal_policy=RemovalPolicy.RETAIN,
                           public_read_access=False,  # Turn off public read access
                           )

        # Permissions for accessing the bucket and objects
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("apigateway.amazonaws.com")]
        ))

        # Define the Lambda function for GET operations
        get_lambda = _lambda.Function(
            self, "GetFunFactHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="get_fun_fact.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FUN_FACTS_TABLE_NAME": fun_facts_table.table_name,
                "LANDMARKS_TABLE_NAME": landmarks_table.table_name,
                "USERS_TABLE_NAME": user_table.table_name,
            }
        )

        # Grant the Lambda function read access to the DynamoDB table
        fun_facts_table.grant_read_data(get_lambda)
        landmarks_table.grant_read_data(get_lambda)
        user_table.grant_read_data(get_lambda)

        # Grant the Lambda function read access to the S3 bucket
        bucket.grant_read(get_lambda)

        # Define the Lambda function for ADD operations
        add_lambda = _lambda.Function(
            self, "AddFunFactHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="add_fun_fact.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FUN_FACTS_TABLE_NAME": fun_facts_table.table_name,
                "LANDMARKS_TABLE_NAME": landmarks_table.table_name,
                "USERS_TABLE_NAME": user_table.table_name,
            }
        )

        # Grant the Lambda function write access to the DynamoDB table
        fun_facts_table.grant_write_data(add_lambda)
        landmarks_table.grant_write_data(add_lambda)
        user_table.grant_write_data(add_lambda)

        # Define the Lambda function for user metadata operations
        user_lambda = _lambda.Function(
            self, "UserHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="user_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "USERS_TABLE_NAME": user_table.table_name,
            }
        )

        # Grant the Lambda function read/write access to the User table
        user_table.grant_read_write_data(user_lambda)

        # Create the API Gateway
        api = apigateway.RestApi(
            self, "funFactsApi",
            rest_api_name="Fun Facts Service",
            description="This service serves fun facts."
        )

        # Create the /funFacts resource
        fun_facts = api.root.add_resource("funFacts")

        # Integrate GET Lambda function
        get_integration = apigateway.LambdaIntegration(get_lambda)
        fun_facts.add_method("GET", get_integration, request_parameters={
            'method.request.querystring.landmarkId': True
        })

        # Create the /landmarks resource
        landmarks = api.root.add_resource("landmarks")

        # Integrate GET Lambda function
        get_integration = apigateway.LambdaIntegration(get_lambda)
        landmarks.add_method("GET", get_integration, request_parameters={
            'method.request.querystring.pageSize': False
        })

        # Integrate ADD Lambda function
        add_integration = apigateway.LambdaIntegration(add_lambda)
        api.root.add_method("POST", add_integration)

        # Create the /users resource
        users = api.root.add_resource("users")

        # Integrate User Lambda function for user metadata
        user_integration = apigateway.LambdaIntegration(user_lambda)
        users.add_method("POST", user_integration)

        # Output the API endpoint
        CfnOutput(self, "ApiEndpoint", value=api.url)

        # Output the table names and bucket name
        CfnOutput(self, "LandmarksTableName", value=landmarks_table.table_name)
        CfnOutput(self, "FunFactsTableName", value=fun_facts_table.table_name)
        CfnOutput(self, "UserTableName", value=user_table.table_name)
        # CfnOutput(self, "UserInteractionsTableName", value=user_interactions_table.table_name)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
