# Design Document

## Overview

The AWS CDK CommitmentTracker project initialization creates a standard Python-based CDK application structure. The design follows AWS CDK best practices for Python projects, establishing a clear separation between the application entry point (app.py) and the stack definition (commitment_stack.py). The project uses a modular structure where the commitment_tracker package contains the infrastructure code, making it easy to extend with additional stacks and constructs as the application grows.

## Architecture

The project follows a standard CDK application architecture:

```
CommitmentTracker/
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git exclusions
└── commitment_tracker/             # Python package
    ├── __init__.py                 # Package initializer
    └── commitment_stack.py         # Main stack definition
```

The architecture separates concerns:
- **app.py**: Instantiates the CDK app and stack(s)
- **commitment_tracker/**: Contains all infrastructure definitions
- **commitment_stack.py**: Defines the CloudFormation stack and resources

## Components and Interfaces

### 1. CDK Application (app.py)

**Purpose**: Entry point for the CDK application that creates the app instance and instantiates stacks.

**Interface**:
```python
# Creates CDK App instance
app = cdk.App()

# Instantiates CommitmentTrackerStack
CommitmentTrackerStack(app, "CommitmentTrackerStack")

# Synthesizes CloudFormation template
app.synth()
```

### 2. CommitmentTrackerStack (commitment_stack.py)

**Purpose**: Defines the main CloudFormation stack for the CommitmentTracker application.

**Interface**:
```python
class CommitmentTrackerStack(Stack):
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
```

**Parameters**:
- `scope`: The parent construct (typically the CDK App)
- `construct_id`: Unique identifier for this stack
- `**kwargs`: Optional stack properties (env, description, etc.)

**Resources Created**:
- DynamoDB Table: CommitmentTrackerGoals with GoalID partition key and UserIDIndex GSI
- Lambda Function: MotivationGenerator with Python 3.12 runtime and DynamoDB/Bedrock access
- EventBridge Rule: Daily trigger at 8:00 AM UTC for MotivationGenerator

### 3. Lambda Function (MotivationGenerator)

**Purpose**: Generates motivational content for commitment tracking goals.

**Configuration**:
```python
from aws_cdk import aws_iam as iam

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
```

**Properties**:
- Runtime: Python 3.12
- Code Location: ./lambda_src directory
- Handler: index.handler (default)
- Permissions: 
  - Full read/write access to CommitmentTrackerGoals table
  - Bedrock InvokeModel access for all models

### 4. EventBridge Rule (Daily Trigger)

**Purpose**: Automatically triggers the MotivationGenerator Lambda function daily at 8:00 AM UTC.

**Configuration**:
```python
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets

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

daily_rule.add_target(targets.LambdaFunction(motivation_lambda))
```

**Properties**:
- Schedule: Cron expression `cron(0 8 * * ? *)` - Daily at 8:00 AM UTC
- Target: MotivationGenerator Lambda function
- Permissions: Automatically grants EventBridge permission to invoke the Lambda

### 3. Configuration (cdk.json)

**Purpose**: Tells the CDK toolkit how to execute the application.

**Structure**:
```json
{
  "app": "python app.py",
  "context": {
    // CDK feature flags
  }
}
```

### 4. Dependencies (requirements.txt)

**Purpose**: Specifies Python package dependencies.

**Contents**:
- `aws-cdk-lib`: Core CDK library (v2.x)
- `constructs`: Base construct library
- `boto3`: AWS SDK for Python

## Data Models

### Stack Configuration

The stack accepts standard CDK Stack properties:

```python
{
    "env": {
        "account": str,  # AWS account ID
        "region": str    # AWS region
    },
    "stack_name": str,   # CloudFormation stack name
    "description": str,  # Stack description
    "tags": dict         # Resource tags
}
```

### DynamoDB Table Schema

**Table Name**: CommitmentTrackerGoals

**Primary Key**:
- Partition Key: `GoalID` (String) - Unique identifier for each goal

**Global Secondary Indexes**:
- `UserIDIndex`:
  - Partition Key: `UserID` (String) - Allows querying all goals for a specific user

**Table Properties**:
- Point-in-Time Recovery: Enabled
- Billing Mode: Default (PAY_PER_REQUEST or PROVISIONED based on CDK defaults)

**Example Item Structure**:
```python
{
    "GoalID": "goal-123",      # Partition key
    "UserID": "user-456",      # GSI partition key
    "Title": "Exercise daily",
    "Description": "...",
    "CreatedAt": "2025-12-03T10:00:00Z",
    "Status": "active"
}
```

### Lambda Function Configuration

**Function Name**: MotivationGenerator

**Runtime**: Python 3.12

**Code Structure**:
```
lambda_src/
└── index.py          # Lambda handler code
```

**Handler Function**:
```python
import boto3
import os
import json
from datetime import datetime

TABLE_NAME = 'CommitmentTrackerGoals'

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    bedrock_runtime = boto3.client('bedrock-runtime')
    table = dynamodb.Table(TABLE_NAME)
    
    # Scan table for all goals
    response = table.scan()
    goals = response['Items']
    
    processed_count = 0
    
    for goal in goals:
        # Construct Bedrock prompt
        prompt = f"""Generate a short, personalized motivational message for this goal:
        Goal: {goal.get('GoalName', 'Unknown')}
        Target Date: {goal.get('TargetDate', 'Not set')}
        Progress: {goal.get('ProgressDetails', 'No details')}
        
        Keep the message encouraging and under 100 words."""
        
        # Call Bedrock API
        bedrock_response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        # Extract message
        response_body = json.loads(bedrock_response['body'].read())
        message = response_body['content'][0]['text']
        
        # Update DynamoDB
        table.update_item(
            Key={'GoalID': goal['GoalID']},
            UpdateExpression='SET MotivationalMessage = :msg, LastEncouragementDate = :date',
            ExpressionAttributeValues={
                ':msg': message,
                ':date': datetime.utcnow().isoformat()
            }
        )
        
        processed_count += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {processed_count} goals')
    }
```

**IAM Permissions**:

DynamoDB Permissions:
- `dynamodb:GetItem` - Read individual items from CommitmentTrackerGoals
- `dynamodb:PutItem` - Write items to CommitmentTrackerGoals
- `dynamodb:UpdateItem` - Update existing items
- `dynamodb:DeleteItem` - Delete items
- `dynamodb:Query` - Query the table
- `dynamodb:Scan` - Scan the table

Bedrock Permissions:
- `bedrock:InvokeModel` - Invoke Amazon Bedrock models for AI-generated motivational content
- Resource: `*` (all Bedrock models)

### EventBridge Rule Configuration

**Rule Name**: DailyMotivationRule

**Schedule**: Cron expression for daily execution at 8:00 AM UTC
- Minute: 0
- Hour: 8
- Day of Month: * (every day)
- Month: * (every month)
- Day of Week: * (every day of week)
- Year: * (every year)

**Target**: MotivationGenerator Lambda function

**Permissions**: EventBridge automatically receives permission to invoke the Lambda function when added as a target

## Lambda Function Workflow

### Motivation Generation Process

The MotivationGenerator Lambda function follows this workflow:

1. **Initialize AWS Clients**
   - Create DynamoDB resource client
   - Create Bedrock Runtime client

2. **Retrieve Goals**
   - Scan the CommitmentTrackerGoals table
   - Retrieve all goal items with GoalName, TargetDate, ProgressDetails

3. **Process Each Goal**
   - Construct personalized prompt with goal details
   - Call Bedrock API (invoke_model) with Claude model
   - Parse response to extract motivational message

4. **Update Database**
   - Update each goal item with generated message
   - Add LastEncouragementDate timestamp

5. **Return Results**
   - Return success response with count of processed goals

### Bedrock Integration

**Model**: anthropic.claude-3-haiku-20240307-v1:0 (fast, cost-effective)

**Request Format**:
```json
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 200,
  "messages": [
    {
      "role": "user",
      "content": "Generate a short, personalized motivational message..."
    }
  ]
}
```

**Response Format**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Your motivational message here..."
    }
  ]
}
```

### CDK Context

Configuration values stored in cdk.json:

```python
{
    "app": str,                    # Command to run the app
    "context": {
        "@aws-cdk/core:newStyleStackSynthesis": bool,
        # Additional feature flags
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After reviewing all acceptance criteria, I've identified that most are specific examples of project initialization rather than universal properties. Since this is a project scaffolding task, the criteria are primarily about verifying that specific files exist with specific content after initialization. These are best tested as examples rather than properties that hold across all inputs.

The acceptance criteria are all "example" tests because:
- They verify specific file creation (app.py, cdk.json, etc.)
- They check specific file contents (specific dependencies, specific configuration values)
- They validate one-time initialization behavior rather than ongoing system properties

There are no redundant properties to eliminate since each criterion checks a distinct aspect of the project structure.

### Correctness Properties

Since this feature involves project initialization and scaffolding, the acceptance criteria are primarily example-based tests rather than universal properties. The correctness of the system is validated by checking that the initialization process creates the expected files with the expected content.

**Example Test 1: Project structure completeness**
After initialization, all required files and directories should exist: app.py, cdk.json, requirements.txt, .gitignore, commitment_tracker/__init__.py, and commitment_tracker/commitment_stack.py
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 3.1, 5.1**

**Example Test 2: Dependencies specification**
The requirements.txt file should contain all three required dependencies: aws-cdk-lib, constructs, and boto3
**Validates: Requirements 2.2, 2.3, 2.4**

**Example Test 3: CDK configuration correctness**
The cdk.json file should specify "python app.py" as the app entry point and include a context object
**Validates: Requirements 3.2, 3.3**

**Example Test 4: Stack class structure**
The CommitmentTrackerStack class should inherit from Stack and have an __init__ method that accepts scope, construct_id, and **kwargs parameters
**Validates: Requirements 4.1, 4.2, 4.3**

**Example Test 5: Gitignore patterns**
The .gitignore file should contain patterns for Python cache (__pycache__, *.pyc), CDK output (cdk.out), and virtual environments (venv, .venv)
**Validates: Requirements 5.2, 5.3, 5.4**

**Example Test 6: CDK synthesis**
Running "cdk synth" should successfully synthesize CloudFormation templates without errors
**Validates: Requirements 1.5, 3.4, 4.4**

**Example Test 7: DynamoDB table configuration**
The synthesized CloudFormation template should contain a DynamoDB table resource named CommitmentTrackerGoals with GoalID as the partition key (String type) and Point-in-Time Recovery enabled
**Validates: Requirements 6.1, 6.2, 6.5**

**Example Test 8: Global Secondary Index configuration**
The DynamoDB table in the CloudFormation template should include a Global Secondary Index named UserIDIndex with UserID as the partition key (String type)
**Validates: Requirements 6.3, 6.4**

**Example Test 9: Lambda function configuration**
The synthesized CloudFormation template should contain a Lambda function resource named MotivationGenerator with Python 3.12 runtime and code sourced from lambda_src directory
**Validates: Requirements 7.1, 7.2, 7.3**

**Example Test 10: Lambda DynamoDB permissions**
The Lambda function's IAM execution role should have policies granting read permissions (GetItem, Query, Scan) and write permissions (PutItem, UpdateItem, DeleteItem) to the CommitmentTrackerGoals table
**Validates: Requirements 7.4, 7.5**

**Example Test 11: Lambda Bedrock permissions**
The Lambda function's IAM execution role should have a policy statement allowing bedrock:InvokeModel action on all resources (*)
**Validates: Requirements 7.6**

**Example Test 12: EventBridge rule configuration**
The synthesized CloudFormation template should contain an EventBridge rule with a cron expression for 8:00 AM UTC daily (cron(0 8 * * ? *)) and the MotivationGenerator Lambda as a target
**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

**Example Test 13: Lambda DynamoDB scan operation**
When the Lambda handler executes, it should call the DynamoDB scan operation on the CommitmentTrackerGoals table and retrieve GoalName, TargetDate, and ProgressDetails for each goal
**Validates: Requirements 9.1, 9.2**

**Example Test 14: Lambda goal processing**
When the Lambda handler processes goals, it should iterate through each goal, construct a Bedrock prompt with goal details, call invoke_model, extract the message, and update DynamoDB with the message and timestamp
**Validates: Requirements 9.3, 10.1, 10.2, 10.3, 10.4, 10.5**

**Example Test 15: Lambda response format**
When the Lambda handler completes, it should return a response with statusCode 200 and a body indicating the number of goals processed
**Validates: Requirements 9.4**

## Error Handling

### File System Errors

**Issue**: Directory or file creation fails due to permissions or existing files
**Handling**: 
- Check if files/directories already exist before creation
- Provide clear error messages indicating which file/directory caused the issue
- Ensure the process is idempotent where possible

### Dependency Installation Errors

**Issue**: pip install fails due to network issues or incompatible versions
**Handling**:
- Specify version ranges in requirements.txt to ensure compatibility
- Document Python version requirements (Python 3.7+)
- Provide clear error messages if installation fails

### CDK Synthesis Errors

**Issue**: CDK synthesis fails due to invalid stack configuration
**Handling**:
- Validate stack class structure before synthesis
- Ensure all required CDK imports are present
- Provide helpful error messages pointing to the issue

### Invalid Configuration

**Issue**: cdk.json contains invalid JSON or incorrect configuration
**Handling**:
- Use valid JSON formatting when creating cdk.json
- Include only well-tested CDK context flags
- Validate JSON structure after creation

## Testing Strategy

### Unit Testing Approach

Since this is a project initialization feature, unit tests will focus on verifying the correctness of generated files and project structure:

1. **File Existence Tests**: Verify all required files are created
2. **File Content Tests**: Verify files contain expected content and structure
3. **Python Syntax Tests**: Verify generated Python files are syntactically valid
4. **JSON Validity Tests**: Verify cdk.json is valid JSON with correct structure

### Property-Based Testing Approach

This feature is not well-suited for property-based testing because:
- It's a one-time initialization process, not a function with varying inputs
- The output is deterministic and specific (exact file structure)
- There are no universal properties that should hold across different inputs

Instead, we'll use example-based integration tests that verify the complete initialization process.

### Integration Testing

**Test Framework**: pytest for Python testing

**Integration Test Approach**:
1. Create a temporary directory
2. Run the initialization process
3. Verify all files exist with correct content
4. Install dependencies in a virtual environment
5. Run `cdk synth` to verify the project works end-to-end
6. Clean up temporary directory

**Key Integration Tests**:
- Complete initialization creates all required files
- Generated project can synthesize CloudFormation templates
- Dependencies can be installed and imported
- Stack class is properly structured and functional

### Test Execution

Tests should be run:
- After initial implementation
- After any modifications to the initialization logic
- As part of CI/CD pipeline if this becomes a reusable tool

### Success Criteria

All tests pass, demonstrating:
- Complete project structure is created
- All files contain correct content
- CDK synthesis succeeds
- Dependencies are correctly specified
