from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct


class CommitmentTrackerStack(Stack):
    """
    CDK Stack for the CommitmentTracker application.
    
    This stack creates:
    - DynamoDB table for storing commitment goals
    - Lambda function for generating motivational messages
    - EventBridge rule for daily automated execution
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table for storing goals
        self.goals_table = dynamodb.Table(
            self, "CommitmentTrackerGoals",
            partition_key=dynamodb.Attribute(
                name="GoalID",
                type=dynamodb.AttributeType.STRING
            ),
            point_in_time_recovery=True
        )
        
        # Add GSI for querying by UserID
        self.goals_table.add_global_secondary_index(
            index_name="UserIDIndex",
            partition_key=dynamodb.Attribute(
                name="UserID",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Lambda function for generating motivational messages
        motivation_lambda = lambda_.Function(
            self, "MotivationGenerator",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambda_src")
        )

        # Grant DynamoDB permissions
        self.goals_table.grant_read_write_data(motivation_lambda)

        # Grant Bedrock permissions
        motivation_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"]
            )
        )

        # EventBridge rule to trigger Lambda daily at 8:00 AM UTC
        daily_rule = events.Rule(
            self, "DailyMotivationRule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="8",
                month="*",
                week_day="*",
                year="*"
            )
        )

        # Add Lambda as target
        daily_rule.add_target(targets.LambdaFunction(motivation_lambda))
