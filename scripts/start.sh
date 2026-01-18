#!/bin/bash

echo "Starting Golf Weather API..."

# Run database migrations if alembic is configured (with timeout)
if [ -f "alembic.ini" ]; then
    echo "Running database migrations..."
    timeout 30 alembic upgrade head || echo "Migration skipped or timed out"
fi

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
