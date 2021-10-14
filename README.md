# Chatbot - Higher Ed - Brain

## REST API

API documentation is available in [Swagger UI](https://swagger.io/tools/swagger-ui/) in the following URL: http://cb-highered-brain-swagger.s3-website-us-east-1.amazonaws.com/
The static website serving the UI is hosted on the `cb-highered-brain-swagger` S3 Bucket.
The automatically-generated JSON file with Swagger/OpenAPI models for the API that feed the UI are in [`docs/swagger_dist/docs/api-cb-highered-brain.json`](docs/swagger_dist/docs/api-cb-highered-brain.json).
A helper script located in [`swagger_update.py`](swagger_update.py) is run periodically to export the JSON file from API Gateway and upload it into the corresponding S3 Bucket.

## DynamoDB

Data generated in the chatbot is stored in two [DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) noSQL databases:
- `*-sessions-*`
  - Partition key: `session_id` (String)
  - Sort key: NA
  - GSI: 
    - Name: `user_id-index`
    - Partition key: `user_id`
    - Sort key: NA
- `*-users-*`
  - Partition key: `log_id` (String)
  - Sort key: NA
  - GSI: NA

#### Note on efficient partitioning of user-sessions

User-Session data is stored in `*-sessions-*`, where `session_id` is the partition key, and `user_id` is only an attribute. We avoid using `user_id` as a partition key (with `session_id` as a sort key) because DynamoDB scales efficiently by assigning a table's partition to different nodes, and we expect the generic "public user" to experience a high number of concurrent operations. Tables partitioned by session sidestep this issue. See [here](https://aws.amazon.com/blogs/database/choosing-the-right-dynamodb-partition-key/) for more information.

Because accessing the sessions of a given user is important, we implement a [Global Secondary Index (GSI)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html) on the `user_id` attribute. The endpoint methods associated to this GSI are of the form `/user/`.

### Table generation

The two DynamoDB tables described above are generated using the program defined in [`createtable.py`](createtable.py).
Run the program using the following syntax:
```sh
python createtable.py [-s [stage]] [-t [table]]
```
Options and defaults are:
- `-s, --stage=dev`
- `-t, --table-type=logs`

Table types are either `sessions` or `logs`. Individual table specs (i.e. naming, environment variables, primary keys, GSI) are all specified in the script itself.