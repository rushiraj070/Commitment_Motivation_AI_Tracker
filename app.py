#!/usr/bin/env python3
"""
CommitmentTracker CDK Application

This is the entry point for the AWS CDK application that deploys
the CommitmentTracker infrastructure including:
- DynamoDB table for storing goals
- Lambda function for generating motivational messages
- EventBridge rule for daily automated execution
"""

import aws_cdk as cdk
from commitment_tracker.commitment_stack import CommitmentTrackerStack


app = cdk.App()

CommitmentTrackerStack(
    app, 
    "CommitmentTrackerStack",
    description="CommitmentTracker infrastructure with DynamoDB, Lambda, and EventBridge"
)

app.synth()
