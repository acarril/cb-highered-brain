from boto3 import session
from botocore.session import get_session
from chalice import Chalice
from chalice import NotFoundError, BadRequestError
from cb_brain import db
from cb_brain import utils
from cb_brain.creditos import gen_oferta_creditos
from cb_brain.utils import add_random_index

import requests

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


@app.route('/student_percentile/{session_id}/{puntaje}', methods=['GET'], cors=True)
def route_student_percentil(session_id, puntaje):
    puntaje = int(puntaje)
    get_sessions_db().add_reply(session_id, 'puntaje', puntaje)
    inv_percentile = utils.compute_2020_inv_percentile(puntaje)
    return {"inv_percentil": inv_percentile}

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

# Options

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

# @app.route('/options_table/{table_stub}', methods=['GET'])
# def route_options_get(table_stub):
#     """Get attributes of specific table related to options

#     Args:
#         table_stub (str): table stub, one of [areas, institutions, levels, locations, majors, programs]

#     Returns:
#         dict: attributes of table
#     """    
#     def get_options_db(table_name):
#         """Get table from DDB"""
#         return db.DynamoDBOptions(
#             boto3.resource('dynamodb').Table(table_name)
#         )
#     table_name = f'icfesbot-{table_stub}-2021'
#     return get_options_db(table_name).list_all_items()

@app.route('/options_table/areas', methods=['GET'], cors=True)
def route_options_table_areas_get():
    path = app.current_request.path
    table_stub = path.split('/').pop()
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).list_all_items()

@app.route('/options_table/institutions', methods=['GET'], cors=True)
def route_options_table_areas_get():
    path = app.current_request.path
    table_stub = path.split('/').pop()
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).list_all_items()

@app.route('/options_table/majors', methods=['GET'], cors=True)
def route_options_table_areas_get():
    path = app.current_request.path
    table_stub = path.split('/').pop()
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).list_all_items()

@app.route('/options_table/programs/{institution_id}', methods=['GET'], cors=True)
def route_options_table_areas_get(institution_id):
    path = app.current_request.path
    table_stub = 'programs'
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    return get_options_db(table_name).get_programs_of_institution(institution_id)

@app.route('/options_table/program_ids', methods=['POST'], cors=True)
def route_options_table_program_ids_get():
    table_stub = 'programs'
    def get_options_db(table_name):
        """Get table from DDB"""
        return db.DynamoDBOptions(
            boto3.resource('dynamodb').Table(table_name)
        )
    table_name = f'icfesbot-{table_stub}-2021'
    body = app.current_request.json_body
    options_id_lst = body.get('options_id_lst')
    return get_options_db(table_name).get_programs_by_id(options_id_lst)


# Credit Check

@app.route('/credits/oferta_creditos/{session_id}', methods=['POST'], cors=True)
def route_credits_oferta_creditos_get(session_id):
    """Post student grade and return credit offer

    Args:
        session_id (str): session ID

    Returns:
        list: list of credit offer with credit attributes
    """
    # Add reply (grades)
    node_name = 'credito_pregunta_notas'
    reply = app.current_request.json_body.get(node_name)
    get_sessions_db().add_reply(session_id, node_name, reply)
    
    # Collect estrato, sisben from session replies
    def credit_attrs_session_flattened(attr_lst=['estrato', 'sisben_bajoC8'], session_id=session_id):
        attrs = {k:get_sessions_db().get_latest_reply(session_id, k) for k in attr_lst}
        replies = {k:(v if v is None else attrs[k]['reply']) for k,v in attrs.items()}
        return replies

    def get_student_info(session_id=session_id):
        session_info = get_sessions_db().get_item(session_id).pop()
        web_id = session_info.get('web_id')
        student_info = get_students_db().get_item(web_id).pop()
        return student_info

    def credit_attrs_student(student_info, attr_lst=['estrato', 'sisben_bajoC8'], session_id=session_id):    
        return dict((k, student_info[k]) for k in attr_lst)

    credit_attrs = credit_attrs_session_flattened()
    # credit_attrs = {'estrato':None, 'sisben_bajoC8':1}
    missing_attrs = [k for k,v in credit_attrs.items() if v is None]
    student_info = get_student_info()
    if missing_attrs:
        student_attrs = credit_attrs_student(student_info, attr_lst=missing_attrs)
        # student_attrs = {'estrato':'', 'sisben_bajoC8':1}
        credit_attrs = {k:(v if v is not None else student_attrs[k]) for k,v in credit_attrs.items()}
    
    # Construct dict of missing attrs (boolean)
    missing_attrs = [k for k,v in credit_attrs.items() if v == '']
    name_map = {'estrato': 'faltaEstrato', 'sisben_bajoC8': 'faltaSisben'}
    missing_attrs_dict = {name_map[k]:(True if k in missing_attrs else False) for k,v in credit_attrs.items()}

    # Generate credit offer
    if not missing_attrs:
        puntaje = app.current_request.json_body.get('puntaje')
        # nota_int = {'sobre34': 34, 'bajo34':30, 'bajo30':20}.get(nota_string)
        credit_id_list = gen_oferta_creditos(
                estrato=int(credit_attrs['estrato']),
                sisben_bajoC8=int(credit_attrs['sisben_bajoC8']),
                saber11=int(puntaje),
                indigena=bool(int(student_info.get('indigena')))
        )
        credit_list = get_credits_db().get_credit_offer(credit_id_list)
        credit_list = add_random_index(credit_list)
    else:
        credit_list = []

    # credit_list = {'creditos': credit_list}
    # response = {**missing_attrs_dict, **credit_list}
    return credit_list


@app.route('/credits/caracteristicas_credito/{session_id}', methods=['POST'], cors=True)
def route_credits_caracteristicas_credito_post(session_id):
    body = app.current_request.json_body
    id_credito = body.get('caracteristicas_credito')
    get_sessions_db().add_reply(session_id, 'caracteristicas_credito', id_credito)


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
    node_name = 'creencia_pago_mensual'
    reply_crencia = app.current_request.json_body.get(node_name)
    get_sessions_db().add_reply(session_id, node_name, reply_crencia)
    seleccion_id_credito = get_sessions_db().get_latest_reply(session_id, 'caracteristicas_credito')['reply']
    info_linea = get_credits_db().get_item(seleccion_id_credito).pop()
    nombre_linea = info_linea.get('nombre_linea_abrev')
    pct_pago_durante = info_linea.get('pct_pago_durante')
    info_repago = utils.calculador_pago_mensual(pct_pago_durante)
    pago_mensual = info_repago.get('cuota_estudios') + ' durante 8 semestres de estudios y ' + info_repago.get('cuota_amort')
    anos_repago = str(int(info_repago.get('plazo_amort')/12))
    response = {
        'precio_carrera': '$5.000.000',
        'seleccion_credito_nombre': nombre_linea,
        'pago_mensual': pago_mensual,
        'tiempo_postgrad': anos_repago
    }
    return response

@app.route('/credits/estrato/{session_id}', methods=['POST'])
def route_credits_estrato(session_id):
    node_name = 'estrato'
    reply = app.current_request.json_body.get(node_name)
    get_sessions_db().add_reply(session_id, node_name, reply)

@app.route('/credits/sisben/{session_id}', methods=['POST'])
def route_credits_sisben(session_id):
    node_name = 'sisben'
    reply = app.current_request.json_body.get(node_name)
    sisben_letter = ''.join([n for n in reply if n.isalpha()])
    sisben_number = ''.join([n for n in reply if n.isdigit()])
    sisben_bajoC8 = int((sisben_letter in ['A', 'B']) or ((sisben_letter in ['C']) and (int(sisben_number) < 8)))
    get_sessions_db().add_reply(session_id, 'sisben_bajoC8', sisben_bajoC8)

# Brain menu maker

@app.route('/brain/menu_carreras_dummy/{session_id}', methods=['POST'], cors=True)
def route_brain_menu_carreras_dummy(session_id):
    body = app.current_request.json_body
    dummy = {
        {"brain": "ML-Targeted", "menu": ["2364", "549", "2974", "5295"], "question": "Wage"}
    }
    return dummy

@app.route('/brain/menu_carreras/{session_id}', methods=['POST'], cors=True)
def route_brain_menu_carreras(session_id):
    body = app.current_request.json_body
    def get_student_info(session_id=session_id):
        session_info = get_sessions_db().get_item(session_id).pop()
        web_id = session_info.get('web_id')
        student_info = get_students_db().get_item(web_id).pop()
        return student_info
    
    # Get student info and create dicts for brain translation
    student_info = get_student_info(session_id)
    genero_dict = {'F': 0, 'M': 1, '': 0}
    sector_private_dict = {'OFICIAL': 0, 'NO OFICIAL': 1, '': 0}
    zona_urban_dict = {'URBANA': 1, 'RURAL':0, '': 1}
    
    # Extract/compute scores and relative pos
    puntaje = int(body.get('puntaje'))
    decil = utils.compute_2020_decile(puntaje)

    fixed_params = {
        "country": "COL"
    }
    random_params = {
        "brain_id": utils.select_random_brain_id()
    }
    user_params = {
        "location": 30, # NOTE! transformar
        "score": puntaje,
        "score_decil": decil,
        "private": sector_private_dict[student_info.get('sector')],
        "urban": zona_urban_dict[student_info.get('zona')],
        "jornada": 1, # no tenemos el dato
        "gender": genero_dict[student_info.get('genero')]
    }
    session_params = {
        'area_of_int': body.get('area_of_int'),
        'level_of_int': body.get('level_of_int'),
        "wage_deviation": utils.process_wage_deviation(body.get('wage_deviation')), # body.get('wage_deviation'),   # real in ~[-10, 10]
        "showed_majors": body.get('showed_programs'), # carreras que hemos mostrado
        "explored_majors": body.get('explored_programs') # carreras que ha hecho click
    }
    dict_for_brains = {
        **fixed_params,
        **random_params,
        **user_params,
        **session_params
    }

    ec2_url = 'http://ec2-3-238-222-45.compute-1.amazonaws.com:5000/'
    brain_response = requests.post(ec2_url, json=dict_for_brains)
    return brain_response.content

# {
#     "wage_deviation": <dif calculada en datoreal_opcion; multiplicada por -1 si subestima, o 0 si está en rango>,
#     "showed_programs": <lista de los `option_id` que se le han mostrado; puede estar vacía>,
#     "explored_programs": <lista de los `option_id` en que ha hecho click; puede estar vacía>,
#     "area_of_int": <area_id de ultima opcion elegida (del inicio o del ultimo menu)>,
#     "level_of_int": <level_id de ultima opcion elegida (del inicio o del ultimo menu)>,
#     "puntaje": <puntaje saber11>
# }ch