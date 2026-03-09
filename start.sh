#!/bin/bash
# Start nginx in the background
nginx -g "daemon off;" &

# Try to import the app first to catch import errors
cd /app
python -c "from app.main import app; print('Import OK')" 2>&1

# Start uvicorn in the foreground
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info 2>&1
