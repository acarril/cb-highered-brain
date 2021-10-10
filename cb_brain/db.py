from uuid import uuid4

from boto3.dynamodb.conditions import Key

DEFAULT_USERNAME = 'default'

class ChatBotDB(object):
    def list_items(self):
        pass

    def add_item(self, description, metadata=None, sessions=None):
        pass

    def get_item(self, user_id):
        pass

    def delete_item(self, user_id):
        pass

    def update_item(self, user_id,description=None,
                    metadata=None, sessions=None):
        pass


# class InMemoryLogsDB(ChatBotDB):
#     '''Class for in-memory databse of logs (for testing)'''
#     def __init__(self, state=None):
#         if state is None:
#             state = {}
#         self._state = state

#     def list_all_items(self):
#         all_items = []
#         for username in self._state:
#             all_items.extend(self.list_items(username))
#         return all_items

#     def list_items(self, username=DEFAULT_USERNAME):
#         return self._state.get(username, {}).values()

#     def add_item(self, description, metadata=None, sessions=None, username=DEFAULT_USERNAME):
#         if username not in self._state:
#             self._state[username] = {}
#         user_id = str(uuid4())
#         self._state[username][user_id] = {
#             'user_id': user_id,
#             'description': description,
#             'metadata': metadata if metadata is not None else {},
#             'username': username,
#             'sessions': sessions if sessions is not None else {}
#         }
#         return user_id

#     def get_item(self, user_id, username=DEFAULT_USERNAME):
#         return self._state[username][user_id]

#     def delete_item(self, user_id, username=DEFAULT_USERNAME):
#         del self._state[username][user_id]

#     def update_item(self, user_id, description=None,
#                     metadata=None, sessions=None, username=DEFAULT_USERNAME):
#         item = self._state[username][user_id]
#         if description is not None:
#             item['description'] = description
#         if metadata is not None:
#             item['metadata'] = metadata
#         if sessions is not None:
#             item['sessions'] = sessions


class DynamoDBLogs(ChatBotDB):
    '''Class for DynamoDB database of logs'''
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, username=DEFAULT_USERNAME):
        response = self._table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']

    def add_item(self, description, metadata=None, sessions=None, username=DEFAULT_USERNAME, session_id=None):
        session_id = session_id if session_id is not None else str(uuid4())
        self._table.put_item(
            Item={
                'username': username,
                'session_id': session_id,
                'description': description,
                'metadata': metadata if metadata is not None else {},
                'sessions': sessions if sessions is not None else {},
            }
        )
        return session_id

    def get_item(self, session_id, username=DEFAULT_USERNAME):
        response = self._table.get_item(
            Key={
                # 'username': username,
                'session_id': session_id,
            },
        )
        return response['Item']

    def delete_item(self, session_id, username=DEFAULT_USERNAME):
        self._table.delete_item(
            Key={
                # 'username': username,
                'session_id': session_id,
            }
        )

    def update_item(self, session_id, description=None,
                    metadata=None, sessions=None, username=DEFAULT_USERNAME):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(session_id)
        if description is not None:
            item['description'] = description
        if metadata is not None:
            item['metadata'] = metadata
        if sessions is not None:
            item['sessions'] = sessions
        self._table.put_item(Item=item)