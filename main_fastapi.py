"""
TTKi FastAPI Application with DDD Architecture
Enterprise-grade foundation for multi-agent system
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import DDD layers
from src.domain.services.agent_orchestrator import AgentOrchestrator
from src.application.services.ttki_application_service import TTKiApplicationService
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging.logger import setup_logging

# Import legacy support for gradual migration
from flask import Flask
from flask_socketio import SocketIO
import threading

logger = logging.getLogger(__name__)

# Pydantic models for API
class TaskRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}
    priority: str = "medium"

class TaskResponse(BaseModel):
    success: bool
    result: Any = None
    error: str = None
    duration: float = 0.0
    agent_type: str = None
    execution_plan: Dict[str, Any] = None

# Global application service
app_service: TTKiApplicationService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global app_service
    
    # Startup
    logger.info("🚀 Starting TTKi FastAPI application...")
    
    # Initialize DDD services
    settings = get_settings()
    agent_orchestrator = AgentOrchestrator()
    app_service = TTKiApplicationService(agent_orchestrator)
    
    # Initialize agent system
    await app_service.initialize()
    
    logger.info("✅ TTKi application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TTKi application...")
    if app_service:
        await app_service.shutdown()
    logger.info("✅ TTKi application shutdown complete")

# Create FastAPI app with DDD architecture
app = FastAPI(
    title="TTKi AI Terminal",
    description="Enterprise-grade AI terminal with multi-agent system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected via WebSocket")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main TTKi interface"""
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/v1/execute", response_model=TaskResponse)
async def execute_task(
    request: TaskRequest,
    app_service_dep: TTKiApplicationService = Depends(lambda: app_service)
):
    """Execute task through DDD application service"""
    try:
        result = await app_service_dep.execute_task(
            task=request.task,
            context=request.context,
            priority=request.priority
        )
        
        return TaskResponse(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error"),
            duration=result.get("duration", 0.0),
            agent_type=result.get("agent_type"),
            execution_plan=result.get("execution_plan")
        )
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/status")
async def get_system_status(
    app_service_dep: TTKiApplicationService = Depends(lambda: app_service)
):
    """Get system status"""
    try:
        return await app_service_dep.get_system_status()
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Process through application service
            if app_service:
                result = await app_service.execute_task(data)
                await manager.send_personal_message(
                    f"Result: {result}",
                    client_id
                )
            else:
                await manager.send_personal_message(
                    "Error: Application service not available",
                    client_id
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        manager.disconnect(client_id)

# Legacy Flask support for gradual migration
flask_app = None
socketio = None

def run_legacy_flask():
    """Run legacy Flask app in separate thread"""
    global flask_app, socketio
    
    try:
        # Import legacy app
        from app import app as legacy_app, socketio as legacy_socketio
        flask_app = legacy_app
        socketio = legacy_socketio
        
        logger.info("🔄 Starting legacy Flask support on port 5001")
        socketio.run(flask_app, host='0.0.0.0', port=5001, debug=False)
        
    except ImportError:
        logger.warning("Legacy Flask app not available")
    except Exception as e:
        logger.error(f"Error starting legacy Flask: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    # Start legacy Flask in background for gradual migration
    if get_settings().enable_legacy_support:
        threading.Thread(target=run_legacy_flask, daemon=True).start()

# Main application runner
if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    # Get settings
    settings = get_settings()
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        "main_fastapi:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
