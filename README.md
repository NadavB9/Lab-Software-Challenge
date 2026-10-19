# A simple fastapi based service manager

## Getting Started
Before Starting, you need [uv](https://docs.astral.sh/uv/getting-started/installation/)

To run with the default settings:
```bash
cp .env.example .env # Copy the default env file
uv run fastapi run # Run FastAPI ( uv will auto-install the dependencies)
```

## Configuration
By default, the server will run with an sqlite db located at `./services.db`, you can change this in the .env file to another database or file.

## Example

```sh
# Create 2 services
curl -X POST http://localhost:8000/services `
  -H "Content-Type: application/json" `
  -d '{
    "services": [
      { "name": "Service A", "host": "127.0.0.1", "port": 8001 },
      { "name": "Service B", "host": "127.0.0.1", "port": 8002 }
    ]
  }'

# Get the services
curl localhost:8000/services

# Delete the service with id 1
curl -X DELETE localhost:8000/services/1

```
