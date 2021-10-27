import subprocess
import argparse
import copy
import boto3
import json
import pandas as pd
from collections.abc import MutableMapping

REST_API_ID = 'j0z5xz882m'

params = pd.read_csv('s3://cb-colombia/estudiantes_2021.csv', index_col=0, nrows=0).columns.tolist()

def export_api(id=REST_API_ID):
    client = boto3.client('apigateway')
    response = client.get_export(
        restApiId=id,
        stageName='api',
        exportType='swagger'
    )
    body = response['body']
    return body

def sync_swagger_s3():
    cmd = 'aws s3 sync docs/swagger_dist s3://cb-highered-brain-swagger'
    subprocess.run(cmd.split())

def delete_keys_from_dict(dictionary, keys):
    keys_set = set(keys)  # just an optimization for the "if key in keys" lookup
    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            else:
                modified_dict[key] = value
    return modified_dict

def add_query_params(dictionary, path, params, method='get'):
    def add_query_param(param, modified_dict, path=path, method=method):
        modified_dict['paths'][path][method]['parameters'].append(
            {
                "name": param,
                "in": "query",
                "required": False,
                "allowEmptyValue": True,
                "type": "string"
            }
        )
    
    modified_dict = copy.deepcopy(dictionary)
    for param in params:
        add_query_param(param, modified_dict=modified_dict)
    return modified_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rest-api-id', default=REST_API_ID)
    parser.add_argument('--no-options', action='store_true')
    parser.add_argument('--local', action='store_true')
    args = parser.parse_args()
    json_content = json.load(export_api(id=args.rest_api_id))
    if args.no_options:
        json_content = delete_keys_from_dict(json_content, ['options'])
    json_content = add_query_params(json_content, '/students/{web_id}', params=params)
    with open('docs/swagger_dist/docs/api-cb-highered-brain.json', 'w') as file:
        json.dump(json_content, file, indent=2)
    if not args.local:
        sync_swagger_s3()

if __name__ == '__main__':
    main()