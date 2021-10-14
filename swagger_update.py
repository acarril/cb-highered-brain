import subprocess
import argparse
import boto3
import json
from collections.abc import MutableMapping

REST_API_ID = 'j0z5xz882m'

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rest-api-id', default=REST_API_ID)
    parser.add_argument('--no-options', action='store_true')
    args = parser.parse_args()
    json_content = json.load(export_api(id=args.rest_api_id))
    if args.no_options:
        json_content = delete_keys_from_dict(json_content, ['options'])
    with open('docs/swagger_dist/docs/api-cb-highered-brain.json', 'w') as file:
        json.dump(json_content, file, indent=2)
    sync_swagger_s3()

if __name__ == '__main__':
    main()