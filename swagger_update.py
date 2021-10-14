import subprocess
import argparse
import boto3

REST_API_ID = 'j0z5xz882m'

def export_api(id=REST_API_ID):
    client = boto3.client('apigateway')
    response = client.get_export(
        restApiId=id,
        stageName='api',
        exportType='swagger'
    )
    json_content = response['body'].read().decode('utf-8')
    return json_content

def sync_swagger_s3():
    cmd = 'aws s3 sync docs/swagger_dist s3://cb-highered-brain-swagger'
    subprocess.run(cmd.split())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rest-api-id', default=REST_API_ID)
    args = parser.parse_args()
    json_content = export_api(id=args.rest_api_id)
    with open('docs/swagger_dist/docs/api-cb-highered-brain.json', 'w') as file:
        file.write(json_content)
    sync_swagger_s3()

if __name__ == '__main__':
    main()