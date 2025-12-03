# AWS CDK Deployment Guide

## Current Status

✅ **Completed:**
- Python dependencies installed
- Node.js and npm installed
- AWS CDK CLI installed (v2.1033.0)
- CloudFormation template synthesized successfully

❌ **Issue:** AWS credentials not configured

## Configure AWS Credentials

You need to set up your AWS credentials before deploying. Here are your options:

### Option 1: AWS CLI Configure (Recommended)

1. Install AWS CLI if not already installed:
   - Download from: https://aws.amazon.com/cli/
   
2. Run the configuration command:
   ```powershell
   aws configure
   ```

3. Enter your credentials when prompted:
   ```
   AWS Access Key ID: [Your Access Key]
   AWS Secret Access Key: [Your Secret Key]
   Default region name: us-east-1  (or your preferred region)
   Default output format: json
   ```

### Option 2: Environment Variables

Set environment variables in PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### Option 3: AWS SSO (If your organization uses SSO)

```powershell
aws sso login --profile your-profile-name
```

## Getting AWS Credentials

If you don't have AWS credentials:

1. Log in to AWS Console: https://console.aws.amazon.com/
2. Go to IAM → Users → Your User
3. Click "Security credentials" tab
4. Click "Create access key"
5. Download and save the credentials securely

**Important:** Never share or commit your AWS credentials!

## Verify Credentials

After configuring, verify with:

```powershell
aws sts get-caller-identity
```

You should see output like:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

## Deploy the Stack

Once credentials are configured:

### Step 1: Bootstrap CDK (First time only)

```powershell
cdk bootstrap
```

This creates necessary S3 buckets and IAM roles for CDK deployments.

### Step 2: Deploy

```powershell
cdk deploy
```

Or skip approval prompts:

```powershell
cdk deploy --require-approval never
```

## Expected Deployment Time

- Bootstrap: 2-3 minutes
- Deploy: 3-5 minutes

## What Gets Deployed

1. **DynamoDB Table**: CommitmentTrackerGoals
   - Partition Key: GoalID (String)
   - GSI: UserIDIndex with UserID partition key
   - Point-in-Time Recovery enabled

2. **Lambda Function**: MotivationGenerator
   - Runtime: Python 3.12
   - Permissions: DynamoDB read/write, Bedrock InvokeModel

3. **EventBridge Rule**: DailyMotivationRule
   - Schedule: Daily at 8:00 AM UTC
   - Target: MotivationGenerator Lambda

4. **IAM Roles**: Automatically created with least-privilege permissions

## After Deployment

### View Resources

```powershell
# List all stacks
cdk list

# View stack outputs
aws cloudformation describe-stacks --stack-name CommitmentTrackerStack
```

### Test the Lambda Function

1. Go to AWS Lambda Console
2. Find "MotivationGenerator" function
3. Click "Test" tab
4. Create a test event (use default EventBridge event)
5. Click "Test"

### Add Sample Data

```powershell
aws dynamodb put-item `
    --table-name CommitmentTrackerGoals `
    --item '{\"GoalID\": {\"S\": \"goal-001\"}, \"UserID\": {\"S\": \"user-123\"}, \"GoalName\": {\"S\": \"Exercise Daily\"}, \"TargetDate\": {\"S\": \"2025-12-31\"}, \"ProgressDetails\": {\"S\": \"Completed 5 out of 7 days this week\"}}'
```

## Troubleshooting

### "Unable to resolve AWS account"
- Run `aws configure` to set up credentials
- Verify with `aws sts get-caller-identity`

### "Access Denied" errors
- Ensure your IAM user has necessary permissions:
  - CloudFormation full access
  - IAM role creation
  - DynamoDB, Lambda, EventBridge, S3 access

### Bootstrap fails
- Check AWS credentials
- Ensure you have permissions to create S3 buckets and IAM roles
- Try specifying region: `cdk bootstrap aws://ACCOUNT-ID/REGION`

### Deployment fails
- Check CloudFormation console for detailed error messages
- Ensure Bedrock is available in your region (us-east-1, us-west-2, etc.)
- Check service quotas for Lambda, DynamoDB

## Cleanup

To remove all deployed resources:

```powershell
cdk destroy
```

Type `y` to confirm deletion.

## Cost Estimate

With moderate usage:
- DynamoDB: ~$1-2/month (free tier: 25 GB, 25 WCU/RCU)
- Lambda: ~$0.20/month (free tier: 1M requests)
- EventBridge: Free (state change events)
- Bedrock: ~$2-3/month (Claude 3 Haiku)

**Total: ~$3-7/month** (mostly Bedrock usage)

## Next Steps

1. Configure AWS credentials
2. Run `cdk bootstrap`
3. Run `cdk deploy`
4. Test the Lambda function
5. Add sample goals to DynamoDB
6. Monitor CloudWatch Logs for Lambda execution
