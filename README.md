# 🎯 CommitmentTracker

A full-stack serverless application for tracking personal goals and commitments with AI-powered motivational messages.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment](#deployment)
- [Web Application](#web-application)
- [AWS Resources](#aws-resources)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Cost Estimate](#cost-estimate)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

CommitmentTracker is a comprehensive goal tracking system that combines:
- **AWS CDK** for infrastructure as code
- **DynamoDB** for data persistence
- **Lambda** for serverless compute
- **Amazon Bedrock** for AI-generated motivational messages
- **EventBridge** for automated daily triggers
- **Flask** web application for user interface

## 🏗️ Architecture

```
┌─────────────────┐
│   Flask Web UI  │ ← User Interface (localhost:5000)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    DynamoDB     │ ← Goal Storage
│  (NoSQL Table)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Lambda Function │ ───► │   Bedrock    │
│ (Python 3.12)   │      │ (Claude AI)  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  EventBridge    │ ← Daily 8 AM UTC Trigger
│     Rule        │
└─────────────────┘
```

## ✨ Features

### Goal Management
- ✅ Create, Read, Update, Delete (CRUD) operations
- 📂 Categorize goals (Health, Career, Personal Development, etc.)
- ⭐ Set priority levels (High, Medium, Low)
- 📊 Track status (Active, Paused, Completed, Cancelled)
- 📈 Visual progress tracking with percentage bars
- 🎯 Define milestones and success criteria
- 🚧 Document obstacles and challenges

### AI-Powered Motivation
- 💪 Generate personalized motivational messages using Amazon Bedrock
- 🤖 Powered by Claude 3 Haiku model
- ⏰ Automated daily motivation at 8:00 AM UTC
- 📅 Timestamp tracking for encouragement history

### Web Interface
- 🎨 Beautiful gradient purple theme
- 📱 Responsive design
- 🔄 Real-time updates
- 📊 Statistics dashboard
- 🎯 Interactive forms with range sliders

## 📦 Prerequisites

### Required Software
- **Python 3.7+** - [Download](https://www.python.org/downloads/)
- **Node.js 14+** - [Download](https://nodejs.org/)
- **AWS CLI** - [Installation Guide](https://aws.amazon.com/cli/)
- **AWS CDK CLI** - Install via: `npm install -g aws-cdk`
- **AWS Account** - [Create Free Account](https://aws.amazon.com/free/)

### AWS Permissions Required
Your IAM user needs these permissions:
- CloudFormation (Full Access)
- DynamoDB (Full Access)
- Lambda (Full Access)
- IAM (Role Creation)
- EventBridge (Full Access)
- S3 (For CDK assets)
- ECR (For CDK bootstrap)
- SSM (Parameter Store)
- Bedrock (InvokeModel)

**Recommended:** Attach `AdministratorAccess` policy for development.

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd CommitmentTracker
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Flask (for Web UI)

```bash
pip install flask
```

### 4. Configure AWS Credentials

```bash
aws configure
```

Enter your credentials:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key
- **Default region**: `us-east-1` (recommended for Bedrock)
- **Output format**: `json`

## 🌐 Deployment

### Step 1: Bootstrap CDK (First Time Only)

```bash
cdk bootstrap
```

This creates necessary S3 buckets and IAM roles for CDK deployments.

### Step 2: Deploy Infrastructure

```bash
cdk deploy --require-approval never
```

This deploys:
- DynamoDB table
- Lambda function
- EventBridge rule
- IAM roles and policies

**Deployment time:** ~3-5 minutes

### Step 3: Verify Deployment

```bash
aws cloudformation describe-stacks --stack-name CommitmentTrackerStack
```

## 💻 Web Application

### Starting the Web Server

```bash
python web_app.py
```

The server will start at: **http://localhost:5000**

### Web Application Features

#### Home Page (`/`)
- View all goals in a card layout
- Statistics dashboard
- Quick actions (Add, Edit, Delete, Generate Motivation)

#### Add Goal (`/add`)
- Comprehensive form with all tracking parameters
- Category selection
- Priority and status dropdowns
- Progress percentage slider
- Milestones and obstacles tracking

#### Edit Goal (`/edit/<goal_id>`)
- Update existing goals
- Modify all parameters
- Track progress over time

#### View Goal (`/view/<goal_id>`)
- Detailed goal information
- View AI-generated motivational messages
- See all milestones and success criteria

#### Generate Motivation (`/generate-motivation`)
- Trigger Lambda function manually
- Generate AI messages for all active goals

## ☁️ AWS Resources

### DynamoDB Table

**Table Name:** `CommitmentTrackerStack-CommitmentTrackerGoalsE83AA8EF-*`

**Schema:**
```json
{
  "GoalID": "String (Partition Key)",
  "UserID": "String",
  "GoalName": "String",
  "GoalCategory": "String",
  "GoalDescription": "String",
  "StartDate": "String (YYYY-MM-DD)",
  "TargetDate": "String (YYYY-MM-DD)",
  "Priority": "String (High/Medium/Low)",
  "Status": "String (Active/Paused/Completed/Cancelled)",
  "ProgressPercentage": "Number (0-100)",
  "ProgressDetails": "String",
  "Milestones": "String",
  "Obstacles": "String",
  "SuccessCriteria": "String",
  "MotivationalMessage": "String",
  "LastEncouragementDate": "String (ISO 8601)",
  "CreatedAt": "String (ISO 8601)",
  "UpdatedAt": "String (ISO 8601)"
}
```

**Global Secondary Index:**
- **Index Name:** `UserIDIndex`
- **Partition Key:** `UserID`

### Lambda Function

**Function Name:** `CommitmentTrackerStack-MotivationGenerator4F042592-*`

**Runtime:** Python 3.12

**Handler:** `index.handler`

**Permissions:**
- DynamoDB: Read/Write access to goals table
- Bedrock: InvokeModel for Claude 3 Haiku

**Trigger:** EventBridge rule (daily at 8 AM UTC)

### EventBridge Rule

**Rule Name:** `DailyMotivationRule`

**Schedule:** `cron(0 8 * * ? *)` - Daily at 8:00 AM UTC

**Target:** MotivationGenerator Lambda function

## 📖 Usage

### Adding a Goal via Web UI

1. Navigate to http://localhost:5000
2. Click "➕ Add Goal"
3. Fill in the form:
   - User ID (e.g., `user-123`)
   - Goal Name (e.g., `Exercise Daily`)
   - Category (select from dropdown)
   - Priority (High/Medium/Low)
   - Target Date
   - Progress details
   - Optional: Milestones, Obstacles, Success Criteria
4. Click "💾 Save Goal"

### Adding a Goal via AWS CLI

```bash
aws dynamodb put-item \
  --table-name <YOUR-TABLE-NAME> \
  --item '{
    "GoalID": {"S": "goal-001"},
    "UserID": {"S": "user-123"},
    "GoalName": {"S": "Learn AWS CDK"},
    "GoalCategory": {"S": "Career & Education"},
    "Priority": {"S": "High"},
    "Status": {"S": "Active"},
    "TargetDate": {"S": "2025-12-31"},
    "ProgressPercentage": {"N": "25"},
    "ProgressDetails": {"S": "Completed basic tutorials"}
  }' \
  --no-verify-ssl
```

### Generating Motivational Messages

**Via Web UI:**
1. Click "✨ Generate Motivation" button
2. Wait for Lambda execution
3. Refresh page to see updated messages

**Via AWS CLI:**
```bash
aws lambda invoke \
  --function-name <YOUR-LAMBDA-NAME> \
  --payload '{}' \
  response.json \
  --no-verify-ssl
```

### Viewing Goals

**Via Web UI:**
- Home page shows all goals in cards
- Click "👁️ View" for detailed view

**Via AWS CLI:**
```bash
aws dynamodb scan \
  --table-name <YOUR-TABLE-NAME> \
  --no-verify-ssl
```

## 📸 Screenshots

### Web Application Interface
![Web UI](screenshots/web-ui.png)

### AWS Console - IAM User
![IAM User](screenshots/iam-user.png)

### AWS Console - DynamoDB Table
![DynamoDB](screenshots/dynamodb-table.png)

### AWS Console - Lambda Function
![Lambda](screenshots/lambda-function.png)

### AWS CLI Configuration
![AWS Configure](screenshots/aws-configure.png)

### Server Running
![Server](screenshots/server-running.png)

## 📁 Project Structure

```
CommitmentTracker/
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── DEPLOYMENT_GUIDE.md             # Detailed deployment guide
├── web_app.py                      # Flask web application
├── commitment_tracker/             # CDK stack package
│   ├── __init__.py
│   └── commitment_stack.py         # Infrastructure definition
├── lambda_src/                     # Lambda function code
│   └── index.py                    # Lambda handler
├── templates/                      # Flask HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── add_goal.html               # Add goal form
│   ├── edit_goal.html              # Edit goal form
│   ├── view_goal.html              # Goal details
│   ├── test.html                   # Test page
│   └── simple.html                 # Simple diagnostic page
└── .kiro/                          # Kiro IDE specs
    └── specs/
        └── aws-cdk-commitment-tracker/
            ├── requirements.md     # Feature requirements
            ├── design.md           # Design document
            └── tasks.md            # Implementation tasks
```

## 🛠️ Technologies Used

### Backend
- **AWS CDK** - Infrastructure as Code
- **Python 3.12** - Programming language
- **AWS Lambda** - Serverless compute
- **Amazon DynamoDB** - NoSQL database
- **Amazon Bedrock** - AI/ML service (Claude 3 Haiku)
- **Amazon EventBridge** - Event scheduling

### Frontend
- **Flask** - Python web framework
- **HTML5/CSS3** - Web technologies
- **Jinja2** - Template engine

### DevOps
- **AWS CloudFormation** - Resource provisioning
- **AWS CLI** - Command-line interface
- **Git** - Version control

## 💰 Cost Estimate

### Monthly Costs (Moderate Usage)

| Service | Usage | Cost |
|---------|-------|------|
| DynamoDB | 25 GB storage, 100 WCU/RCU | $1-2 |
| Lambda | 1000 invocations/month | $0.20 |
| EventBridge | Daily triggers | Free |
| Bedrock (Claude 3 Haiku) | 1000 API calls | $2-3 |
| S3 (CDK Assets) | < 1 GB | $0.02 |
| **Total** | | **~$3-7/month** |

**Free Tier Benefits:**
- DynamoDB: 25 GB storage, 25 WCU, 25 RCU
- Lambda: 1M requests/month, 400,000 GB-seconds
- EventBridge: All state change events free

## 🔧 Troubleshooting

### White Screen in Browser
1. Hard refresh: `Ctrl + Shift + R`
2. Clear browser cache
3. Check browser console (F12) for errors
4. Try: http://localhost:5000/simple

### SSL Certificate Errors
The application uses `--no-verify-ssl` flag for development. This is normal.

### Lambda Timeout
- Default timeout: 3 seconds
- Bedrock calls may take longer
- Increase timeout in `commitment_stack.py` if needed

### DynamoDB Access Denied
- Verify IAM permissions
- Check Lambda execution role
- Ensure table name is correct in `web_app.py`

### CDK Bootstrap Fails
- Ensure AWS credentials are configured
- Check IAM permissions (need CloudFormation, S3, IAM access)
- Try: `cdk bootstrap --verbose`

### Flask Not Starting
```bash
# Install Flask
pip install flask

# Check if port 5000 is available
netstat -ano | findstr :5000

# Try different port
python web_app.py --port 8080
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- AWS CDK Team for excellent infrastructure tools
- Amazon Bedrock for AI capabilities
- Flask community for the web framework
- Claude AI for motivational message generation

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review AWS CloudFormation stack events
- Check Lambda CloudWatch logs
- Open an issue on GitHub

## 🔗 Useful Links

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)

---

**Built with ❤️ using AWS CDK, Python, and AI**

*Last Updated: December 3, 2025*
