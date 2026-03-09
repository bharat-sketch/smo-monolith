# Stage 1: Build React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY fe-react-smo/package.json fe-react-smo/package-lock.json* ./
RUN npm ci
COPY fe-react-smo/ .
ARG REACT_APP_BACKEND_URL=/api/v1
ARG REACT_APP_AUTH_SECRET=dummy-secret-key
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV REACT_APP_AUTH_SECRET=${REACT_APP_AUTH_SECRET}
RUN npm run build

# Stage 2: Python backend + nginx
FROM python:3.11-slim

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Install SMO backend dependencies
WORKDIR /app/smo
COPY be-fastapi-smo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install auto-matching-service dependencies (shares most deps, only adds new ones)
WORKDIR /app/auto-matching
COPY auto-matching-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SMO backend code
WORKDIR /app/smo
COPY be-fastapi-smo/ .

# Copy auto-matching-service code
WORKDIR /app/auto-matching
COPY auto-matching-service/ .

# Copy frontend build to nginx
COPY --from=frontend-builder /app/build /var/www/html

# Nginx config: serve static files + proxy /api to uvicorn
COPY nginx.conf /etc/nginx/sites-available/default

# Startup script: nginx + both uvicorn processes
COPY start.py /app/start.py

EXPOSE 8080
CMD ["python", "/app/start.py"]
