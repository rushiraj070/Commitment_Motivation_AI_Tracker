import boto3
import os
import json
from datetime import datetime

TABLE_NAME = 'CommitmentTrackerStack-CommitmentTrackerGoalsE83AA8EF-1LYY8IHI461KQ'

def handler(event, context):
    """
    Lambda handler that generates motivational messages for commitment tracking goals.
    
    This function:
    1. Scans DynamoDB for all goals
    2. Generates personalized motivational messages using Amazon Bedrock
    3. Updates each goal with the message and timestamp
    
    Args:
        event: EventBridge event data
        context: Lambda context object
        
    Returns:
        dict: Response with status code and count of processed goals
    """
    # Initialize AWS clients
    dynamodb = boto3.resource('dynamodb')
    bedrock_runtime = boto3.client('bedrock-runtime')
    table = dynamodb.Table(TABLE_NAME)
    
    # Scan table for all goals
    response = table.scan()
    goals = response['Items']
    
    processed_count = 0
    
    # Process each goal
    for goal in goals:
        # Extract goal details
        goal_name = goal.get('GoalName', 'Unknown')
        target_date = goal.get('TargetDate', 'Not set')
        progress_details = goal.get('ProgressDetails', 'No details')
        
        # Construct personalized Bedrock prompt
        prompt = f"""Generate a short, personalized motivational message for this goal:

Goal: {goal_name}
Target Date: {target_date}
Progress: {progress_details}

Keep the message encouraging and under 100 words."""
        
        # Call Bedrock API to generate motivational message
        bedrock_response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        # Extract generated message from response
        response_body = json.loads(bedrock_response['body'].read())
        message = response_body['content'][0]['text']
        
        # Update DynamoDB with generated message and timestamp
        table.update_item(
            Key={'GoalID': goal['GoalID']},
            UpdateExpression='SET MotivationalMessage = :msg, LastEncouragementDate = :date',
            ExpressionAttributeValues={
                ':msg': message,
                ':date': datetime.utcnow().isoformat()
            }
        )
        
        processed_count += 1
    
    # Return success response
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully processed {processed_count} goals')
    }
