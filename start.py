#!/usr/bin/env python3
"""Startup script for combined nginx + uvicorn container on Cloud Run.

Runs nginx in the background and uvicorn in the foreground so that
Cloud Run captures uvicorn's stdout/stderr in its logging.
"""
import subprocess
import sys
import os

# Start nginx in background
subprocess.Popen(["nginx", "-g", "daemon off;"], stdout=sys.stdout, stderr=sys.stderr)

# Start uvicorn in the foreground (replaces this process)
os.execvp("uvicorn", [
    "uvicorn", "app.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--log-level", "info",
])
