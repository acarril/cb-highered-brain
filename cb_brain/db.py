from uuid import uuid4
from datetime import datetime, timezone
import uuid
from boto3.dynamodb.conditions import Key

DEFAULT_USERNAME = 'default'

class ChatBotDB(object):
    '''Class for DynamoDB database of users'''
    def __init__(self, table_resource):
        self._table = table_resource
        self._table.partition_key = self._table.key_schema.pop()['AttributeName']

    def list_all_items(self):
        '''List all items of table'''
        response = self._table.scan()
        return response['Items']

    def list_item(self, primary_key, secondary_key=None, filter=None):
        response = self._table.query(
            KeyConditionExpression=Key(list(primary_key.keys())[0]).eq(list(primary_key.values())[0])
        )
        return response['Items']

    def add_item(self):
        pass

    def put_attributes(self, partition_key_value, sort_key_value=None, attrs_dict=None):
        """Put dict of attributes into DDB table"""
        # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
        # https://stackoverflow.com/questions/34447304/example-of-update-item-in-dynamodb-boto3
        def build_update_expression(attrs_dict):
            """Given a dictionary we generate an update expression and a dict of values
            to update a dynamodb table.

            Params:
                attrs_dict (dict): Parameters to use for formatting.

            Returns:
                update expression, dict of values.
            """
            update_expression = ["set "]
            update_values = {}
            for key, val in attrs_dict.items():
                update_expression.append(f" {key} = :{key},")
                update_values[f":{key}"] = val
            return "".join(update_expression)[:-1], update_values

        key_name = self._table.partition_key
        update_expression, update_values = build_update_expression(attrs_dict)
        response = self._table.update_item(
            Key={
                key_name: partition_key_value
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=update_values,
            ReturnValues="UPDATED_NEW"
        )
        return response

    def get_item(self, partition_key_value, sort_key_value=None):
        response = self._table.query(
            KeyConditionExpression=Key(self._table.partition_key).eq(partition_key_value)
        )
        return response['Items']

    def delete_item(self, primary_key, secondary_key=None, filter=None):
        # return [list(primary_key.keys())[0], list(primary_key.values())[0]]
        self._table.delete_item(
            Key={
                list(primary_key.keys())[0]: list(primary_key.values())[0],
            }
        )

    def update_item(self, user_id,description=None,
                    metadata=None, sessions=None):
        pass


class DynamoDBSessions(ChatBotDB):
    def get_user(self, user_id, response_element=None):
        response_element = response_element if response_element is not None else 'Items'
        response = self._table.query(
            IndexName='web_id-index',
            KeyConditionExpression=Key('web_id').eq(user_id)
        )
        return response[response_element]

    def add_item(self, user_id, session_time, session_id=None):
        self._table.put_item(
            Item={
                'session_id': session_id if session_id is not None else str(uuid4().hex),
                'web_id': user_id,
                'session_time': session_time if session_time is not None else datetime.now(timezone.utc).isoformat(),
                'session_n': self.get_user(user_id, response_element='Count')+1,
            }
        )
    
    def delete_item(self, session_id):
        self._table.delete_item(Key={'session_id': session_id})



class DynamoDBLogs(ChatBotDB):
    def get_item(self):
        pass
    def add_item(self, session_id, log_label, log_time=None, log_id=None):
        self._table.put_item(
            Item={
                'log_id': log_id if log_id is not None else str(uuid4()),
                'session_id': session_id,
                'log_time': log_time if log_time is not None else datetime.now(timezone.utc).isoformat(),
                'log_label': log_label
            }
        )

class DynamoDBStudents(ChatBotDB):
    pass
    # def get_item(self, web_id):
    #     response = self._table.query(KeyConditionExpression=Key('web_id').eq(web_id))
    #     return response['Items']


# class DynamoDBUsers(ChatBotDB):
#     def add_item(self, hash_key, session_id, session_time, user_type=None):
#         self._table.put_item(
#             Item={
#                 'user_id': hash_key if hash_key is not None else str(uuid4()),
#                 'session_time': session_time if session_time is not None else datetime.now(timezone.utc).isoformat(),
#                 'session_id': session_id if session_id is not None else str(uuid4()),
#                 'user_type': user_type if user_type is not None else {}
#             }
#         )
#         return hash_key

#     def get_item(self, user_id, sort_key=None):
#         response = self._table.get_item(
#             Key={
#                 'user_id': user_id,
#             },
#         )
#         return response

#     def query_item(self, filter_key='user_id', filter_value='alvaro'):
#         filtering_exp = Key('user_id').eq('alvaro')
#         response = self._table.query(KeyConditionExpression=filtering_exp)
#         return response['Items']


# class DynamoDBLogs(ChatBotDB):
#     '''Class for DynamoDB database of logs'''
#     def __init__(self, table_resource):
#         self._table = table_resource

#     def list_all_items(self):
#         response = self._table.scan()
#         return response['Items']

#     def list_items(self, username=DEFAULT_USERNAME):
#         response = self._table.query(
#             KeyConditionExpression=Key('username').eq(username)
#         )
#         return response['Items']

#     def add_item(self, description, metadata=None, sessions=None, username=DEFAULT_USERNAME, session_id=None):
#         session_id = session_id if session_id is not None else str(uuid4())
#         self._table.put_item(
#             Item={
#                 'username': username,
#                 'session_id': session_id,
#                 'description': description,
#                 'metadata': metadata if metadata is not None else {},
#                 'sessions': sessions if sessions is not None else {},
#             }
#         )
#         return session_id

#     def get_item(self, session_id, username=DEFAULT_USERNAME):
#         response = self._table.get_item(
#             Key={
#                 # 'username': username,
#                 'session_id': session_id,
#             },
#         )
#         return response['Item']

#     def delete_item(self, session_id, username=DEFAULT_USERNAME):
#         self._table.delete_item(
#             Key={
#                 # 'username': username,
#                 'session_id': session_id,
#             }
#         )

#     def update_item(self, session_id, description=None,
#                     metadata=None, sessions=None, username=DEFAULT_USERNAME):
#         # We could also use update_item() with an UpdateExpression.
#         item = self.get_item(session_id)
#         if description is not None:
#             item['description'] = description
#         if metadata is not None:
#             item['metadata'] = metadata
#         if sessions is not None:
#             item['sessions'] = sessions
#         self._table.put_item(Item=item)