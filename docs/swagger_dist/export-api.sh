#! /bin/bash
export AWS_PAGER="" # trick from https://stackoverflow.com/questions/60122188/how-to-turn-off-the-pager-for-aws-cli-return-value
mkdir docs | true
aws apigateway get-export --rest-api-id j0z5xz882m --stage-name "api" --export-type swagger docs/api-cb-highered-brain.json

