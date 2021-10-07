from chalice import Chalice
from cb_brain import db

import os
import boto3

app = Chalice(app_name='icfesbot')
app.debug = True
_DB = None

def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBLogs(
            boto3.resource('dynamodb').Table(os.environ['APP_TABLE_NAME'])
        )
    return _DB


### Routes

# Create a message
@app.route('/logs', methods=['POST'])
def add_new_msg():
    body = app.current_request.json_body
    return get_app_db().add_item(
        description=body['description'],
        metadata=body.get('metadata'),
    )

# Get all messages
@app.route('/logs', methods=['GET'])
def get_logs():
    return get_app_db().list_items()

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
        state=body.get('state'),
        metadata=body.get('metadata'))







########

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/hello/{name}')
def hello_name(name):
   return {'hello': name}

@app.route('/users', methods=['POST'])
def create_user():
    user_as_json = app.current_request.json_body
    return {'user': user_as_json}

OBJECTS = {
}

@app.route('/objects/{key}', methods=['GET', 'PUT'])
def myobject(key):
    request = app.current_request
    if request.method == 'PUT':
        OBJECTS[key] = request.json_body
    elif request.method == 'GET':
        try:
            return {key: OBJECTS[key]}
        except KeyError:
            raise NotFoundError(key)

