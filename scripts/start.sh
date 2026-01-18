#!/bin/bash

echo "Starting Golf Weather API..."

# Skip alembic migrations - database is managed manually
# The leads table and other schema changes are applied via Railway console
echo "Skipping alembic migrations (database managed manually)"

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
