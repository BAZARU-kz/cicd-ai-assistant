#!/usr/bin/env sh

# Load environment variables from Vault
python load_env.py

# Run migrations if triggered
if [ "$MIGRATIONS_TRIGGER" = "TRUE" ]
then
    echo "Running database migrations..."
    alembic revision --autogenerate -m "migration message" &&
    alembic upgrade head
fi

# Start the FastAPI application (production mode without reload)
uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8000 --workers 4