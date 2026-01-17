#!/bin/bash
set -e

echo "Starting Golf Weather API..."

# Run database migrations if alembic is configured
if [ -f "alembic.ini" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Migration skipped (database may not be configured)"
fi

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
