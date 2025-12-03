# Implementation Plan

- [x] 1. Create project structure and configuration files


  - Create root-level directory structure
  - Create commitment_tracker package directory
  - _Requirements: 1.1, 1.2_



- [ ] 2. Create requirements.txt with dependencies
  - Add aws-cdk-lib dependency
  - Add constructs dependency
  - Add boto3 dependency


  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Create cdk.json configuration file


  - Set app entry point to "python app.py"
  - Add CDK context configuration with feature flags
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Create .gitignore file

  - Add Python cache patterns (__pycache__, *.pyc, *.pyo)
  - Add CDK output directory (cdk.out)
  - Add virtual environment patterns (venv/, .venv/, env/)


  - Add IDE and OS specific patterns
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 5. Create commitment_tracker package structure
  - Create __init__.py to make it a valid Python package

  - _Requirements: 1.4_

- [ ] 6. Implement CommitmentTrackerStack in commitment_stack.py
  - Import required CDK modules (Stack, aws_dynamodb)
  - Define CommitmentTrackerStack class inheriting from Stack

  - Implement __init__ method with scope, construct_id, and **kwargs parameters
  - Call super().__init__() with provided parameters
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 7. Add DynamoDB table to the stack
  - Create DynamoDB table resource named CommitmentTrackerGoals
  - Configure GoalID as partition key with String type
  - Enable Point-in-Time Recovery
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 8. Add Global Secondary Index to DynamoDB table
  - Add UserIDIndex GSI to the table
  - Configure UserID as partition key with String type for the GSI
  - _Requirements: 6.3, 6.4_

- [x] 9. Create lambda_src directory and implement Lambda handler



  - Create lambda_src directory in project root
  - Create index.py file
  - _Requirements: 7.3_


- [ ] 9.1. Implement Lambda handler function structure
  - Import boto3, os, json, and datetime modules
  - Define TABLE_NAME constant as 'CommitmentTrackerGoals'
  - Define handler function with event and context parameters
  - Initialize DynamoDB resource and Bedrock Runtime clients
  - _Requirements: 9.1_


- [ ] 9.2. Implement DynamoDB scan operation
  - Use boto3 to scan the CommitmentTrackerGoals table
  - Retrieve all items from the scan response
  - Extract GoalName, TargetDate, and ProgressDetails attributes

  - _Requirements: 9.1, 9.2_

- [ ] 9.3. Implement goal processing loop
  - Iterate through each goal retrieved from DynamoDB

  - Initialize counter for processed goals
  - _Requirements: 9.3_

- [x] 9.4. Implement Bedrock prompt construction

  - For each goal, construct a prompt string with GoalName, TargetDate, and ProgressDetails
  - Include instruction to generate a short personalized motivational message
  - _Requirements: 10.1, 10.2_

- [x] 9.5. Implement Bedrock API call

  - Call bedrock_runtime.invoke_model with Claude model ID
  - Pass properly formatted request body with anthropic_version, max_tokens, and messages
  - Parse response body to extract generated message text
  - _Requirements: 10.3, 10.4_



- [ ] 9.6. Implement DynamoDB update operation
  - Use table.update_item to update each goal with generated message
  - Set MotivationalMessage attribute with generated text
  - Set LastEncouragementDate attribute with current UTC timestamp
  - _Requirements: 10.5_


- [ ] 9.7. Implement handler response
  - Return response with statusCode 200
  - Include body with count of processed goals
  - _Requirements: 9.4_


- [ ] 10. Add Lambda function to the stack
  - Import aws_lambda module from aws_cdk
  - Create Lambda function resource named MotivationGenerator
  - Configure Python 3.12 runtime
  - Set code source to lambda_src directory using Code.from_asset()

  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 11. Grant Lambda function DynamoDB permissions
  - Use grant_read_write_data() method to give Lambda access to goals_table
  - Verify IAM role is automatically created with appropriate policies
  - _Requirements: 7.4, 7.5_




- [ ] 11.1. Grant Lambda function Bedrock permissions
  - Import aws_iam module from aws_cdk
  - Use add_to_role_policy() method to add Bedrock permissions
  - Create PolicyStatement with bedrock:InvokeModel action
  - Set resources to ["*"] to allow access to all Bedrock models
  - _Requirements: 7.6_

- [ ] 12. Add EventBridge rule to the stack
  - Import aws_events and aws_events_targets modules from aws_cdk
  - Create EventBridge Rule resource with cron schedule
  - Configure cron expression for 8:00 AM UTC daily (minute=0, hour=8)
  - Add MotivationGenerator Lambda as target using LambdaFunction target
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 13. Create app.py entry point
  - Import CDK App class and CommitmentTrackerStack
  - Instantiate CDK App
  - Instantiate CommitmentTrackerStack with app as scope
  - Call app.synth() to synthesize CloudFormation template
  - _Requirements: 1.1, 1.5_

- [ ]* 10. Create integration tests for project structure
  - Write test to verify all required files exist
  - Write test to verify requirements.txt contains all dependencies
  - Write test to verify cdk.json has correct configuration
  - Write test to verify .gitignore has correct patterns
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 5.1, 5.2, 5.3, 5.4_

- [ ]* 11. Create tests for stack structure
  - Write test to verify CommitmentTrackerStack class exists and inherits from Stack
  - Write test to verify __init__ method signature
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 13. Create tests for DynamoDB table configuration
  - Write test to verify synthesized CloudFormation contains DynamoDB table
  - Write test to verify table has GoalID partition key with String type
  - Write test to verify Point-in-Time Recovery is enabled
  - Write test to verify UserIDIndex GSI exists with UserID partition key
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 14. Create tests for Lambda function configuration
  - Write test to verify Lambda function exists in CloudFormation template
  - Write test to verify Python 3.12 runtime is configured
  - Write test to verify code is sourced from lambda_src
  - Write test to verify Lambda has read/write permissions to DynamoDB table
  - Write test to verify Lambda has bedrock:InvokeModel permissions
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ]* 15. Create tests for EventBridge rule configuration
  - Write test to verify EventBridge rule exists in CloudFormation template
  - Write test to verify cron expression is set to 8:00 AM UTC daily
  - Write test to verify Lambda function is configured as target
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ]* 16. Create unit tests for Lambda handler
  - Write test for DynamoDB scan operation with mocked table
  - Write test for Bedrock prompt construction
  - Write test for Bedrock API call with mocked client
  - Write test for DynamoDB update operation
  - Write test for handler response format
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ]* 17. Create CDK synthesis integration test
  - Write test that runs "cdk synth" command
  - Verify synthesis completes without errors
  - Verify CloudFormation template is generated
  - _Requirements: 1.5, 3.4, 4.4_
