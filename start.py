#!/usr/bin/env python3
"""Startup script for combined nginx + SMO backend on Cloud Run.

Runs nginx in the background, SMO backend in the foreground
so Cloud Run captures its logs.
"""
import subprocess
import sys
import os

# Start nginx in background
subprocess.Popen(["nginx", "-g", "daemon off;"], stdout=sys.stdout, stderr=sys.stderr)

# Start SMO backend in the foreground (port 8000) — replaces this process
os.chdir("/app/smo")
os.execvp("uvicorn", [
    "uvicorn", "app.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--log-level", "info",
])
