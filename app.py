from boto3 import session
from botocore.session import get_session
from chalice import Chalice
from cb_brain import db
from cb_brain.creditos import gen_oferta_creditos
from chalice import NotFoundError, BadRequestError

import os
import boto3

app = Chalice(app_name='cb-highered-brain')
app.debug = True
app.api.cors = True

_SESSIONS_DB = None
_STUDENTS_DB = None
_CREDITS_DB = None

def get_sessions_db():
    global _SESSIONS_DB
    if _SESSIONS_DB is None:
        _SESSIONS_DB = db.DynamoDBSessions(
            boto3.resource('dynamodb').Table(os.environ['SESSIONS_TABLE_NAME'])
        )
    return _SESSIONS_DB

def get_students_db():
    global _STUDENTS_DB
    if _STUDENTS_DB is None:
        _STUDENTS_DB = db.DynamoDBStudents(
            boto3.resource('dynamodb').Table(os.environ['STUDENTS_TABLE_NAME'])
        )
    return _STUDENTS_DB

def get_credits_db():
    global _CREDITS_DB
    if _CREDITS_DB is None:
        _CREDITS_DB = db.DynamoDBCredits(
            boto3.resource('dynamodb').Table(os.environ['CREDITS_TABLE_NAME'])
        )
    return _CREDITS_DB

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
    '''Get specific session'''
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

@app.route('/options/{node_label}/{session_id}', methods=['PUT'], cors=True)
def route_options_post(node_label, session_id):
    body = app.current_request.json_body
    try:
        return get_sessions_db().put_attributes(
            partition_key_value=session_id,
            attrs_dict=body
        )
    except AttributeError:
        raise BadRequestError("expected a JSON body to POST")

@app.route('/options/{table_stub}', methods=['GET'])
def route_options_get(table_stub):
    def get_options_db(table_name):
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).list_all_items()


# Credit Check

@app.route('/credits/{session_id}', methods=['POST'], cors=True)
def route_credits_get(session_id):
    session_info = get_sessions_db().get_item(session_id).pop() # d0fda7d82cf741ae812a8f303f105b69
    web_id = session_info.get('web_id')
    student_info = get_students_db().get_item(web_id).pop()
    nota_string = app.current_request.json_body.get('credito_pregunta_notas')
    nota_int = {'sobre34': 34, 'bajo34':30, 'bajo30':20}.get(nota_string)
    credit_id_list = gen_oferta_creditos(
        estrato=int(student_info.get('estrato')),
        sisben_bajoC8=int(student_info.get('sisben_bajoC8')),
        nota=nota_int,
        saber11=300,
        indigena=bool(int(student_info.get('indigena')))
    )
    return get_credits_db().get_credit_offer(credit_id_list)

@app.route('/credits/creencia_pago_mensual', methods=['GET'], cors=True)
def route_credits_creencia_pago_mensual():
    return {
        "p200": "1.000.000",
        "p100": "500.000",
        "p50": "250.000",
        "p10": "100.000"
    }

@app.route('/credits/creencia_pago_mensual/{session_id}', methods=['POST'], cors=True)
def route_credits_creencia_pago_mensual(session_id):
    return
