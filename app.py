from botocore.session import get_session
from chalice import Chalice
from cb_brain import db
from chalice import NotFoundError, BadRequestError

import os
import boto3

app = Chalice(app_name='cb-highered-brain')
app.debug = True
_SESSIONS_DB = None
_LOGS_DB = None
_STUDENTS_DB = None

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

def get_students_db():
    global _STUDENTS_DB
    if _STUDENTS_DB is None:
        _STUDENTS_DB = db.DynamoDBStudents(
            boto3.resource('dynamodb').Table(os.environ['STUDENTS_TABLE_NAME'])
        )
    return _STUDENTS_DB

### Routes

@app.route('/', methods=['GET'], cors=True)
def hello_world():
    '''Good ol' 'hello world' for testing purposes'''
    return {'hello': 'world'}

# Students DB

@app.route('/students/{web_id}', methods=['GET'], cors=True)
def route_student_get(web_id):
    '''Get student information'''
    params = app.current_request.query_params
    try:
        response = get_students_db().get_item(web_id).pop()
    except IndexError:
        raise NotFoundError(f"web_id={web_id} not found")
    if params is None:
        return response
    else:
        return {k: response[k] for k in [*params]}

# Sessions DB

@app.route('/sessions', methods=['GET'], cors=True)
def route_sessions_get():
    '''Get all sessions'''
    return get_sessions_db().list_all_items()

@app.route('/sessions/{session_id}', methods=['GET'], cors=True)
def route_sessions_get(session_id):
    '''Get all sessions'''
    try:
        response = get_sessions_db().get_item(session_id).pop()
    except IndexError:
        raise NotFoundError(f"session_id={session_id} not found")
    return response

@app.route('/sessions/user/{web_id}', methods=['GET'], cors=True)
def route_sessions_user_get(web_id):
    '''Get all sessions of `user_id`'''
    return get_sessions_db().get_user(user_id=web_id)

@app.route('/sessions/user/{web_id}', methods=['POST'], cors=True)
def route_sessions_user_post(web_id):
    '''Create new session associated to `web_id`'''
    body = app.current_request.json_body
    response = get_sessions_db().add_item(
        user_id=web_id,
        session_time=body.get('session_time') if body is not None else None
    )
    return response

@app.route('/sessions/{session_id}', methods=['PUT'], cors=True)
def route_sessions_put(session_id):
    body = app.current_request.json_body
    try:
        return get_sessions_db().put_attributes(
            partition_key_value=session_id,
            attrs_dict=body
        )
    except AttributeError:
        raise BadRequestError("You have to pass a JSON dict of attributes to PUT")

@app.route('/sessions/{session_id}/nem', methods=['POST'], cors=True)
def route_sessions_grades(session_id):
    body = app.current_request.json_body
    return

# @app.route('/sessions/{session_id}', methods=['DELETE'], cors=True)
# def route_sessions_delete(session_id):
#     '''Delete session identified by `session_id`'''
#     return get_sessions_db().delete_item(session_id=session_id)

# Credit Check

@app.route('/credits/{web_id}', methods=['GET'], cors=True)
def route_credits_get(web_id):
    response = [
            {
                'id_credito': 1,
                'nombre_linea': 'Mi credito 1',
                'tasa_interes': '9% + IPC',
                'pct_durante': '40%',
                'pct_post': '60%',
                'plazo': 'Doble del período de estudios financiado'
            },
            {
                'id_credito': 2,
                'nombre_linea': 'Mi credito 2',
                'tasa_interes': '10% + IPC',
                'pct_durante': '50%',
                'pct_post': '50%',
                'plazo': 'Doble del período de estudios financiado'
            }
        ]
    return response


# # Messages DB

# @app.route('/message', methods=['GET'], cors=True)
# def get_message():
#     '''Get message from backend'''
#     web_id = app.current_request.query_params.get('web_id')
#     session_id = app.current_request.query_params.get('session_id')
#     message_id = app.current_request.query_params.get('message_id')
#     # return {'webID': web_id}
#     response = get_students_db().get_item(web_id)
#     message = response.pop()
#     return message

# # Logs DB

# @app.route('/logs', methods=['GET'], cors=True)
# def get_logs():
#     '''Get all sessions'''
#     return get_logs_db().list_all_items()

# @app.route('/logs/{session_id}', methods=['POST'], cors=True)
# def add_new_message(session_id):
#     '''Add new session to database'''
#     body = app.current_request.json_body
#     return get_logs_db().add_item(
#         session_id=session_id,
#         log_label=body.get('log_label')
#     )
