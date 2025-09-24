#!/usr/bin/env python3
"""
Minimal HTTP server for CI/CD testing
"""

import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

app = FastAPI(
    title="Minimal HTTP Server",
    description="A minimal HTTP server for CI/CD testing",
    version="1.0.0"
)

@app.get("/")
async def hello() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        'message': 'Hello from minimal HTTP server!',
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy'
    }

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint for load balancers"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }

@app.get("/info")
async def info() -> Dict[str, Any]:
    """System information endpoint"""
    return {
        'app': 'minimal-http-server',
        'version': '1.0.0',
        'python_version': sys.version,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)