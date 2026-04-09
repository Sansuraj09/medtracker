#!/bin/bash

echo "Initializing database..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"

echo "Starting Gunicorn..."
exec python -m gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
