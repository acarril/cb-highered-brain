from botocore.session import get_session
from chalice import Chalice
from cb_brain import db
from chalice import NotFoundError

import os
import boto3

app = Chalice(app_name='cb-highered-brain')
app.debug = True
_SESSIONS_DB = None
_LOGS_DB = None

def get_sessions_db():
    global _SESSIONS_DB
    if _SESSIONS_DB is None:
        _SESSIONS_DB = db.DynamoDBSessions(
            boto3.resource('dynamodb').Table(os.environ['SESSIONS_TABLE_NAME'])
        )
    return _SESSIONS_DB

def get_logs_db():
    global _LOGS_DB
    if _LOGS_DB is None:
        _LOGS_DB = db.DynamoDBLogs(
            boto3.resource('dynamodb').Table(os.environ['LOGS_TABLE_NAME'])
        )
    return _LOGS_DB

### Routes

## SESSIONS

# Get all sessions
@app.route('/sessions', methods=['GET'])
def get_sessions():
    '''Get all sessions'''
    return get_sessions_db().list_all_items()

@app.route('/sessions/{user_id}', methods=['POST'])
def add_new_session(user_id):
    '''Add new session associated to `user_id`'''
    body = app.current_request.json_body
    return get_sessions_db().add_item(
        user_id=user_id,
        session_time=body.get('session_time') if body is not None else None
    )

@app.route('/sessions/{user_id}', methods=['GET'])
def get_user_session(user_id):
    '''Get all sessions of `user_id` (requires `user_id` as GSI)'''
    return get_sessions_db().get_user(user_id=user_id)

## LOGS

# Get all messages
@app.route('/logs', methods=['GET'])
def get_logs():
    '''Get all sessions'''
    return get_logs_db().list_all_items()

@app.route('/logs/{session_id}', methods=['POST'])
def add_new_message(session_id):
    '''Add new session to database'''
    body = app.current_request.json_body
    return get_logs_db().add_item(
        session_id=session_id,
        log_label=body.get('log_label')
    )






########

# # Create a message
# @app.route('/logs', methods=['POST'])
# def add_new_msg():
#     body = app.current_request.json_body
#     return get_app_db().add_item(
#         description=body['description'],
#         metadata=body.get('metadata'),
#         sessions=body.get('sessions'),
#         session_id=body.get('session_id')
#     )

# # Get all messages
# @app.route('/logs', methods=['GET'])
# def get_logs():
#     return get_app_db().list_all_items()

# # Get specific message
# @app.route('/logs/{user_id}', methods=['GET'])
# def get_msg(user_id):
#     return get_app_db().get_item(user_id)

# # Delete specific message
# @app.route('/logs/{user_id}', methods=['DELETE'])
# def delete_msg(user_id):
#     return get_app_db().delete_item(user_id)

# # Update specific message
# @app.route('/logs/{user_id}', methods=['PUT'])
# def update_todo(user_id):
#     body = app.current_request.json_body
#     get_app_db().update_item(
#         user_id,
#         description=body.get('description'),
#         metadata=body.get('metadata'),
#         sessions=body.get('sessions'))



# ### Users

# @app.route('/users', methods=['POST'])
# def add_new_user():
#     '''Add new user to users database'''
#     body = app.current_request.json_body
#     return get_users_db().add_item(
#         hash_key=body.get('user_id'),
#         session_time=body.get('session_time'),
#         session_id=body.get('session_id'),
#         user_type=body.get('user_type')
#     )

# @app.route('/users', methods=['GET'])
# def get_all_users():
#     '''Get all users'''
#     return get_users_db().list_all_items()

# @app.route('/users/{user_id}', methods=['GET'])
# def get_user(user_id):
#     '''Get all sessions from specific user_id'''
#     return get_users_db().list_item(primary_key={'user_id': user_id})

# @app.route('/users/{user_id}', methods=['DELETE'])
# def delete_user(user_id):
#     '''Delete all sessions of specific user'''
#     return get_users_db().delete_item(primary_key={'user_id': user_id})