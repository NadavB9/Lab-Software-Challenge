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
