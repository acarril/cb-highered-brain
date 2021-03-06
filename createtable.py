import os
import json
import argparse
import boto3

TABLES = {
    'degrees': {
        'prefix': 'icfesbot',
        'suffix': '2021',
        'env_var': 'DEGREES_TABLE_NAME',
        'hash_key': 'degree_id'
    },
    'credits': {
        'prefix': 'icfesbot',
        'suffix': '2021',
        'env_var': 'CREDITS_TABLE_NAME',
        'hash_key': 'id_credito'
    },
    'students': {
        'prefix': 'icfesbot',
        'suffix': '2021',
        'env_var': 'STUDENTS_TABLE_NAME',
        'hash_key': 'web_id'
    },
    'sessions': {
        'prefix': 'icfesbot',
        'suffix': '2021',
        'env_var': 'SESSIONS_TABLE_NAME',
        'hash_key': 'session_id',
        'gsi_partition_key': 'web_id'
    }
}


def create_table(table_name, hash_key, range_key=None, gsi_partition_key=None):
    client = boto3.client('dynamodb')
    key_schema = [
        {
            'AttributeName': hash_key,
            'KeyType': 'HASH',
        }
    ]
    attribute_definitions = [
        {
            'AttributeName': hash_key,
            'AttributeType': 'S',
        }
    ]
    if range_key is not None:
        key_schema.append({'AttributeName': range_key, 'KeyType': 'RANGE'})
        attribute_definitions.append(
            {'AttributeName': range_key, 'AttributeType': 'S'})
    client.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        BillingMode='PAY_PER_REQUEST'
    )
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=table_name, WaiterConfig={'Delay': 1})
    if gsi_partition_key is not None:
        gsi = [
            {
                'Create': {
                    'IndexName': '-'.join([gsi_partition_key, 'index']),
                    'KeySchema': [
                        {
                            'AttributeName': gsi_partition_key,
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
                
            }
        ]
        client.update_table(
            AttributeDefinitions=[
                {
                    'AttributeName': gsi_partition_key,
                    'AttributeType': 'S'
                }
            ],
            TableName=table_name,
            GlobalSecondaryIndexUpdates=gsi
        )
    return table_name


def record_as_env_var(key, value, stage):
    with open(os.path.join('.chalice', 'config.json')) as f:
        data = json.load(f)
        data['stages'].setdefault(stage, {}).setdefault(
            'environment_variables', {}
        )[key] = value
    with open(os.path.join('.chalice', 'config.json'), 'w') as f:
        serialized = json.dumps(data, indent=2, separators=(',', ': '))
        f.write(serialized + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument('-t', '--table-type', default='students',
                        choices=['credits', 'degrees', 'students', 'sessions'],
                        help='Specify which type to create')
    args = parser.parse_args()
    table_config = TABLES[args.table_type]
    table_name = create_table(
        '-'.join([table_config['prefix'], args.table_type, table_config['suffix']]),
        table_config['hash_key'],
        table_config.get('range_key'),
        table_config.get('gsi_partition_key')
    )
    record_as_env_var(table_config['env_var'], table_name, args.stage)


if __name__ == '__main__':
    main()