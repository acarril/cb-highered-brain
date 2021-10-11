from chalice import Chalice
from cb_brain import db
from chalice import NotFoundError

import os
import boto3

app = Chalice(app_name='icfesbot')
app.debug = True
_DB = None
_USER_DB = None

def get_app_db():
    '''Get chatbot database using DynamoDBLogs backend'''
    global _DB
    if _DB is None:
        _DB = db.DynamoDBLogs(
            boto3.resource('dynamodb').Table(os.environ['LOGS_TABLE_NAME'])
        )
    return _DB

def get_users_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = db.DynamoDBUsers(
            boto3.resource('dynamodb').Table(os.environ['USERS_TABLE_NAME'])
        )
            
    return _USER_DB

### Routes

# Create a message
@app.route('/logs', methods=['POST'])
def add_new_msg():
    body = app.current_request.json_body
    return get_app_db().add_item(
        description=body['description'],
        metadata=body.get('metadata'),
        sessions=body.get('sessions'),
        session_id=body.get('session_id')
    )

# Get all messages
@app.route('/logs', methods=['GET'])
def get_logs():
    return get_app_db().list_all_items()

# Get specific message
@app.route('/logs/{user_id}', methods=['GET'])
def get_msg(user_id):
    return get_app_db().get_item(user_id)

# Delete specific message
@app.route('/logs/{user_id}', methods=['DELETE'])
def delete_msg(user_id):
    return get_app_db().delete_item(user_id)

# Update specific message
@app.route('/logs/{user_id}', methods=['PUT'])
def update_todo(user_id):
    body = app.current_request.json_body
    get_app_db().update_item(
        user_id,
        description=body.get('description'),
        metadata=body.get('metadata'),
        sessions=body.get('sessions'))



### Users

@app.route('/users', methods=['POST'])
def add_new_user():
    '''Add new user to users database'''
    body = app.current_request.json_body
    return get_users_db().add_item(
        hash_key=body.get('user_id'),
        session_time=body.get('session_time'),
        session_id=body.get('session_id'),
        user_type=body.get('user_type')
    )

@app.route('/users', methods=['GET'])
def get_all_users():
    '''Get all users'''
    return get_users_db().list_all_items()

@app.route('/users/{user_id}', methods=['GET'])
def get_user(user_id):
    '''Get all sessions from specific user_id'''
    return get_users_db().list_item(primary_key={'user_id': user_id})

@app.route('/users/{user_id}', methods=['DELETE'])
def delete_user(user_id):
    '''Delete all sessions of specific user'''
    return get_users_db().delete_item(primary_key={'user_id': user_id})