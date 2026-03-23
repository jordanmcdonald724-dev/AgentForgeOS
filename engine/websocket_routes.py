"""
WebSocket Routes for FastAPI Integration

Provides WebSocket endpoints for real-time UI updates and integrates
with the WebSocket manager for connection handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter

from engine.websocket_manager import websocket_manager, WebSocketMessage

logger = logging.getLogger(__name__)

# Create WebSocket router
websocket_router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Helper class for managing WebSocket connections in FastAPI."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str) -> bool:
        """Connect a WebSocket client."""
        try:
            await websocket.accept()
            self.active_connections[session_id] = websocket
            return True
        except Exception as e:
            logger.error(f"Failed to connect WebSocket {session_id}: {e}")
            return False
    
    def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal_message(self, message: str, session_id: str) -> bool:
        """Send a message to a specific client."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
                return False
        return False


# Global connection manager
connection_manager = ConnectionManager()


@websocket_router.websocket("/connect/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    project_id: Optional[str] = None
):
    """
    Main WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier
        project_id: Optional project to subscribe to
    """
    # Connect WebSocket
    connected = await connection_manager.connect(websocket, session_id)
    if not connected:
        await websocket.close(code=1000)
        return
    
    # Register with WebSocket manager
    registered = await websocket_manager.register_connection(
        session_id, websocket, project_id
    )
    
    if not registered:
        await websocket.close(code=1000)
        connection_manager.disconnect(session_id)
        return
    
    logger.info(f"WebSocket client connected: {session_id} (project: {project_id})")
    
    try:
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(session_id, message, project_id)
            except json.JSONDecodeError:
                # Send error for invalid JSON
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": "Invalid JSON format"},
                    timestamp="2024-01-01T00:00:00Z"  # Would use real timestamp
                )
                await connection_manager.send_personal_message(
                    json.dumps(error_msg.__dict__, default=str), 
                    session_id
                )
            except Exception as e:
                logger.error(f"Error handling message from {session_id}: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
    finally:
        # Cleanup
        await websocket_manager.unregister_connection(session_id, websocket)
        connection_manager.disconnect(session_id)


@websocket_router.websocket("/project/{project_id}")
async def project_websocket(
    websocket: WebSocket, 
    project_id: str,
    session_id: Optional[str] = None
):
    """
    Project-specific WebSocket endpoint.
    
    Args:
        websocket: WebSocket connection
        project_id: Project identifier
        session_id: Optional session identifier (will generate if not provided)
    """
    # Generate session ID if not provided
    if not session_id:
        import uuid
        session_id = f"project_{project_id}_{uuid.uuid4().hex[:8]}"
    
    # Connect WebSocket
    connected = await connection_manager.connect(websocket, session_id)
    if not connected:
        await websocket.close(code=1000)
        return
    
    # Register with WebSocket manager and subscribe to project
    registered = await websocket_manager.register_connection(
        session_id, websocket, project_id
    )
    
    if not registered:
        await websocket.close(code=1000)
        connection_manager.disconnect(session_id)
        return
    
    logger.info(f"Project WebSocket client connected: {session_id} -> {project_id}")
    
    try:
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_project_websocket_message(session_id, project_id, message)
            except json.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": "Invalid JSON format"},
                    timestamp="2024-01-01T00:00:00Z"
                )
                await connection_manager.send_personal_message(
                    json.dumps(error_msg.__dict__, default=str), 
                    session_id
                )
            except Exception as e:
                logger.error(f"Error handling project message from {session_id}: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"Project WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Project WebSocket error for {session_id}: {e}")
    finally:
        # Cleanup
        await websocket_manager.unregister_connection(session_id, websocket)
        connection_manager.disconnect(session_id)


async def handle_websocket_message(
    session_id: str, 
    message: Dict[str, Any], 
    project_id: Optional[str] = None
) -> None:
    """
    Handle incoming WebSocket messages from clients.
    
    Args:
        session_id: Session identifier
        message: Message data
        project_id: Associated project ID
    """
    message_type = message.get("type")
    
    if message_type == "ping":
        # Handle ping/pong for connection health
        pong_msg = WebSocketMessage(
            type="pong",
            data={"timestamp": "2024-01-01T00:00:00Z"},
            timestamp="2024-01-01T00:00:00Z",
            session_id=session_id
        )
        await websocket_manager.send_to_session(session_id, pong_msg)
    
    elif message_type == "subscribe_project":
        # Handle project subscription
        new_project_id = message.get("project_id")
        if new_project_id:
            success = await websocket_manager.subscribe_to_project(session_id, new_project_id)
            if success:
                logger.info(f"Session {session_id} subscribed to project {new_project_id}")
            else:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": f"Failed to subscribe to project {new_project_id}"},
                    timestamp="2024-01-01T00:00:00Z"
                )
                await websocket_manager.send_to_session(session_id, error_msg)
    
    elif message_type == "get_status":
        # Handle status request
        stats = websocket_manager.get_connection_stats()
        status_msg = WebSocketMessage(
            type="status_response",
            data=stats,
            timestamp="2024-01-01T00:00:00Z"
        )
        await websocket_manager.send_to_session(session_id, status_msg)
    
    elif message_type == "request_project_status":
        # Handle project status request
        if project_id:
            # This would integrate with orchestration engine to get real project status
            project_status = {
                "project_id": project_id,
                "status": "active",
                "tasks": [],
                "agents": [],
                "last_update": "2024-01-01T00:00:00Z"
            }
            
            status_msg = WebSocketMessage(
                type="project_status_response",
                data=project_status,
                timestamp="2024-01-01T00:00:00Z",
                project_id=project_id
            )
            await websocket_manager.send_to_session(session_id, status_msg)
    
    else:
        # Handle unknown message types
        error_msg = WebSocketMessage(
            type="error",
            data={"error": f"Unknown message type: {message_type}"},
            timestamp="2024-01-01T00:00:00Z"
        )
        await websocket_manager.send_to_session(session_id, error_msg)


async def handle_project_websocket_message(
    session_id: str, 
    project_id: str, 
    message: Dict[str, Any]
) -> None:
    """
    Handle project-specific WebSocket messages.
    
    Args:
        session_id: Session identifier
        project_id: Project identifier
        message: Message data
    """
    message_type = message.get("type")
    
    if message_type == "ping":
        # Handle ping/pong
        pong_msg = WebSocketMessage(
            type="pong",
            data={"timestamp": "2024-01-01T00:00:00Z"},
            timestamp="2024-01-01T00:00:00Z",
            session_id=session_id,
            project_id=project_id
        )
        await websocket_manager.send_to_session(session_id, pong_msg)
    
    elif message_type == "request_tasks":
        # Handle task list request
        # This would integrate with orchestration engine
        tasks_msg = WebSocketMessage(
            type="tasks_response",
            data={
                "project_id": project_id,
                "tasks": [],
                "total": 0
            },
            timestamp="2024-01-01T00:00:00Z",
            project_id=project_id
        )
        await websocket_manager.send_to_session(session_id, tasks_msg)
    
    elif message_type == "request_agents":
        # Handle agent status request
        agents_msg = WebSocketMessage(
            type="agents_response",
            data={
                "project_id": project_id,
                "agents": [],
                "active_count": 0
            },
            timestamp="2024-01-01T00:00:00Z",
            project_id=project_id
        )
        await websocket_manager.send_to_session(session_id, agents_msg)
    
    else:
        # Handle unknown message types
        error_msg = WebSocketMessage(
            type="error",
            data={"error": f"Unknown project message type: {message_type}"},
            timestamp="2024-01-01T00:00:00Z",
            project_id=project_id
        )
        await websocket_manager.send_to_session(session_id, error_msg)


# Helper functions for broadcasting from other parts of the system

async def broadcast_task_update(task_id: str, status: str, data: Dict[str, Any], project_id: Optional[str] = None):
    """Broadcast task update via WebSocket."""
    await websocket_manager.broadcast_task_update(task_id, status, data, project_id)


async def broadcast_agent_activity(agent_name: str, activity: str, data: Dict[str, Any], project_id: Optional[str] = None):
    """Broadcast agent activity via WebSocket."""
    await websocket_manager.broadcast_agent_activity(agent_name, activity, data, project_id)


async def broadcast_build_progress(project_id: str, stage: str, progress: float, message: str):
    """Broadcast build progress via WebSocket."""
    await websocket_manager.broadcast_build_progress(project_id, stage, progress, message)


async def broadcast_system_event(event_type: str, data: Dict[str, Any], severity: str = "info"):
    """Broadcast system event via WebSocket."""
    await websocket_manager.broadcast_system_event(event_type, data, severity)


async def broadcast_error(error: str, context: Dict[str, Any], project_id: Optional[str] = None):
    """Broadcast error via WebSocket."""
    await websocket_manager.broadcast_error(error, context, project_id)


# Cleanup task for stale connections
async def cleanup_websocket_connections():
    """Background task to cleanup stale WebSocket connections."""
    while True:
        try:
            await websocket_manager.cleanup_stale_connections()
            await asyncio.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Error in WebSocket cleanup task: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error
