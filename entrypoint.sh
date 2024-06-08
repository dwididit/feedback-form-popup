#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000
