from boto3 import session
from botocore.session import get_session
from chalice import Chalice
from chalice import NotFoundError, BadRequestError
from cb_brain import db
from cb_brain.creditos import gen_oferta_creditos
from cb_brain.utils import add_random_index

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


# Students DB

@app.route('/students/{web_id}', methods=['GET'], cors=True)
def route_students_get(web_id):
    """Get information of specific student

    Args:
        web_id (str): web ID (i.e. student ID)

    Raises:
        NotFoundError: web ID not found in students table

    Returns:
        dict: attributes associated to input web ID
    """    
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
    """List all sessions (note this might be resource-intensive)

    Returns:
        list: list of dicts of attributes associated to all session IDs
    """    
    return get_sessions_db().list_all_items()

@app.route('/sessions/{session_id}', methods=['GET'], cors=True)
def route_sessions_get(session_id):
    """Get specific session

    Args:
        session_id (str): session ID

    Raises:
        NotFoundError: session ID not found in sessions table`

    Returns:
        dict: attributes associated to input session ID
    """        
    try:
        response = get_sessions_db().get_item(session_id).pop()
    except IndexError:
        raise NotFoundError(f"session_id={session_id} not found")
    return response

@app.route('/sessions/user/{web_id}', methods=['GET'], cors=True)
def route_sessions_user_get(web_id):
    """Get all sessions of specific user

    Args:
        web_id (str): web ID

    Returns:
        list: list of dicts with session information
    """    
    return get_sessions_db().get_user(user_id=web_id)

@app.route('/sessions/user/{web_id}', methods=['POST'], cors=True)
def route_sessions_user_post(web_id):
    """Generate new session associated to `web_id`

    Args:
        web_id (str): user ID

    Returns:
        session_id: session ID
    """    
    body = app.current_request.json_body
    response = get_sessions_db().add_item(
        user_id=web_id,
        session_time=body.get('session_time') if body is not None else None
    )
    return response

@app.route('/sessions/{session_id}', methods=['PUT'], cors=True)
def route_sessions_put(session_id):
    """Put attributes

    Args:
        session_id ([type]): [description]

    Raises:
        BadRequestError: [description]

    Returns:
        [type]: [description]
    """    
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

@app.route('/options_table/{table_stub}', methods=['GET'])
def route_options_get(table_stub):
    """Get attributes of specific table related to options

    Args:
        table_stub (str): table stub, one of [areas, institutions, levels, locations, majors, programs]

    Returns:
        dict: attributes of table
    """    
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).list_all_items()


# Credit Check

@app.route('/credits/oferta_creditos/{session_id}', methods=['POST'], cors=True)
def route_credits_oferta_creditos_get(session_id):
    """Post student grade and return credit offer

    Args:
        session_id (str): session ID

    Returns:
        list: list of credit offer with credit attributes
    """
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
    credit_list = get_credits_db().get_credit_offer(credit_id_list)
    credit_list = add_random_index(credit_list)
    return credit_list

@app.route('/credits/caracteristicas_credito/{session_id}', methods=['POST'], cors=True)
def route_credits_caracteristicas_credito_post(session_id):
    body = app.current_request.json_body


@app.route('/credits/creencia_pago_mensual/{session_id}', methods=['GET'], cors=True)
def route_credits_creencia_pago_mensual_get(session_id):
    dummy = {
        "p200": "1.000.000",
        "p100": "500.000",
        "p50": "250.000",
        "p10": "100.000"
    }
    return dummy

@app.route('/credits/creencia_pago_mensual/{session_id}', methods=['POST'], cors=True)
def route_credits_creencia_pago_mensual(session_id):
    get_sessions_db().add_reply(session_id, 'creencia_pago_mensual')
    dummy = {
        'precio_carrera': '$6.000.000',
        'seleccion_credito_nombre': 'nombre_linea',
        'pago_mensual': '$110.000',
        'tiempo_postgrad': '4'
    }
    return dummy