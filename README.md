# Chatbot - Higher Ed - Brain

## REST API

Automatically generated Swagger 2.0 models for the API are in [docs/swagger.json](docs/swagger.json)

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

## DynamoDB

Data generated in the chatbot is stored in two [DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) noSQL databases:
- `icfesbot-sessions-2021`
  - Partition key: `session_id` (String)
  - Sort key: NA
  - GSI: 
    - Name: `user_id-index`
    - Partition key: `user_id`
    - Sort key: NA
- `icfesbot-users-2021`
  - Partition key: `log_id` (String)
  - Sort key: NA
  - GSI: NA