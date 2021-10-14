# Chatbot - Higher Ed - Brain

## REST API

Automatically generated [Swagger](https://swagger.io/) 2.0 models for the API are in [docs/swagger.json](docs/swagger.json)

The REST API supports the following resources:
- GET - `/logs/`: get a list of all interactions
- POST - `/logs/`: create a new interaction
- GET - `/logs/{log_id}`: get a specific interaction
- DELETE - `/logs/{log_id}`: delete a specific interaction 
- PUT - `/logs/{log_id}`: update a specific interaction
- GET - `/sessions`: get a list of all sessions
- POST - `/sessions`: create a new session
- GET - `/logs/{session_id}`: get a specific session
- DELETE - `/logs/{session_id}`: delete a specific session 
- PUT - `/logs/{session_id}`: update a specific session

### API Documentation

An OpenAPI file with API documentation is in [`docs/latestswagger.json](docs/latestswagger.json).
```sh
aws apigateway get-export --parameters extensions='apigateway' --rest-api-id j0z5xz882m --stage-name api --export-type swagger latestswagger.json
```

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