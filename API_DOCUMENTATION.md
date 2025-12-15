# API Documentation

Complete reference for all API endpoints.

## Base URL
```
http://localhost:5000/api
```

## Authentication

API keys configured in `.env` file. No authentication headers required for local deployment.

## Endpoints

### Health Check

**GET** `/health`

Check service availability.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "fibo": "available",
    "comfyui": "available",
    "nuke": "available",
    "agents": "available"
  }
}
