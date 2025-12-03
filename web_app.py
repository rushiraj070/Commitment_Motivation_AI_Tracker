"""
CommitmentTracker Web Application
Flask web interface for managing goals and testing the Lambda function
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import boto3
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# AWS Configuration
TABLE_NAME = 'CommitmentTrackerStack-CommitmentTrackerGoalsE83AA8EF-1LYY8IHI461KQ'
LAMBDA_FUNCTION = 'CommitmentTrackerStack-MotivationGenerator4F042592-n4SGQX4mPdT4'
AWS_REGION = 'us-east-1'

# Disable SSL verification (for development only)
os.environ['NODE_TLS_REJECT_UNAUTHORIZED'] = '0'

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, verify=False)
lambda_client = boto3.client('lambda', region_name=AWS_REGION, verify=False)
table = dynamodb.Table(TABLE_NAME)


@app.route('/test')
def test():
    """Test page to verify server is working"""
    return render_template('test.html')


@app.route('/simple')
def simple():
    """Simple diagnostic page"""
    try:
        response = table.scan()
        goals = response.get('Items', [])
        return render_template('simple.html', goals=goals)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"


@app.route('/')
def index():
    """Home page - display all goals"""
    try:
        response = table.scan()
        goals = response.get('Items', [])
        print(f"DEBUG: Found {len(goals)} goals")
        return render_template('index.html', goals=goals)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        flash(f'Error loading goals: {str(e)}', 'error')
        return render_template('index.html', goals=[])


@app.route('/add', methods=['GET', 'POST'])
def add_goal():
    """Add a new goal"""
    if request.method == 'POST':
        try:
            goal_id = f"goal-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            item = {
                'GoalID': goal_id,
                'UserID': request.form['user_id'],
                'GoalName': request.form['goal_name'],
                'GoalCategory': request.form['goal_category'],
                'GoalDescription': request.form.get('goal_description', ''),
                'TargetDate': request.form['target_date'],
                'StartDate': request.form.get('start_date', datetime.now().strftime('%Y-%m-%d')),
                'Priority': request.form['priority'],
                'Status': request.form.get('status', 'Active'),
                'ProgressPercentage': int(request.form.get('progress_percentage', 0)),
                'ProgressDetails': request.form['progress_details'],
                'Milestones': request.form.get('milestones', ''),
                'Obstacles': request.form.get('obstacles', ''),
                'SuccessCriteria': request.form.get('success_criteria', ''),
                'CreatedAt': datetime.now().isoformat(),
                'UpdatedAt': datetime.now().isoformat()
            }
            
            table.put_item(Item=item)
            flash('Goal added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding goal: {str(e)}', 'error')
    
    return render_template('add_goal.html')


@app.route('/edit/<goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    """Edit an existing goal"""
    if request.method == 'POST':
        try:
            table.update_item(
                Key={'GoalID': goal_id},
                UpdateExpression='''SET UserID = :uid, GoalName = :gn, GoalCategory = :gc, 
                                    GoalDescription = :gd, TargetDate = :td, StartDate = :sd,
                                    Priority = :pr, #st = :status, ProgressPercentage = :pp,
                                    ProgressDetails = :pd, Milestones = :ms, Obstacles = :ob,
                                    SuccessCriteria = :sc, UpdatedAt = :ua''',
                ExpressionAttributeNames={
                    '#st': 'Status'
                },
                ExpressionAttributeValues={
                    ':uid': request.form['user_id'],
                    ':gn': request.form['goal_name'],
                    ':gc': request.form['goal_category'],
                    ':gd': request.form.get('goal_description', ''),
                    ':td': request.form['target_date'],
                    ':sd': request.form.get('start_date', ''),
                    ':pr': request.form['priority'],
                    ':status': request.form.get('status', 'Active'),
                    ':pp': int(request.form.get('progress_percentage', 0)),
                    ':pd': request.form['progress_details'],
                    ':ms': request.form.get('milestones', ''),
                    ':ob': request.form.get('obstacles', ''),
                    ':sc': request.form.get('success_criteria', ''),
                    ':ua': datetime.now().isoformat()
                }
            )
            flash('Goal updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating goal: {str(e)}', 'error')
    
    # Get goal data
    try:
        response = table.get_item(Key={'GoalID': goal_id})
        goal = response.get('Item')
        return render_template('edit_goal.html', goal=goal)
    except Exception as e:
        flash(f'Error loading goal: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/delete/<goal_id>')
def delete_goal(goal_id):
    """Delete a goal"""
    try:
        table.delete_item(Key={'GoalID': goal_id})
        flash('Goal deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting goal: {str(e)}', 'error')
    
    return redirect(url_for('index'))


@app.route('/generate-motivation')
def generate_motivation():
    """Trigger Lambda function to generate motivational messages"""
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION,
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        result = json.loads(response['Payload'].read())
        
        if response.get('FunctionError'):
            flash(f'Lambda error: {result.get("errorMessage", "Unknown error")}', 'error')
        else:
            flash('Motivational messages generated successfully!', 'success')
        
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error invoking Lambda: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/view/<goal_id>')
def view_goal(goal_id):
    """View goal details including motivational message"""
    try:
        response = table.get_item(Key={'GoalID': goal_id})
        goal = response.get('Item')
        return render_template('view_goal.html', goal=goal)
    except Exception as e:
        flash(f'Error loading goal: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    print("=" * 60)
    print("CommitmentTracker Web Application")
    print("=" * 60)
    print(f"DynamoDB Table: {TABLE_NAME}")
    print(f"Lambda Function: {LAMBDA_FUNCTION}")
    print(f"Region: {AWS_REGION}")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
