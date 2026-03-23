"""
WebSocket Manager for Real-Time UI Updates

Provides live streaming of task execution, agent activity, and system status
to the frontend for real-time monitoring and interaction.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class WebSocketMessage:
    """Standard WebSocket message format"""
    type: str
    data: Dict[str, Any]
    timestamp: str
    session_id: Optional[str] = None
    project_id: Optional[str] = None


class WebSocketManager:
    """
    Manages WebSocket connections and real-time message broadcasting.
    
    Provides live updates for:
    - Task execution status
    - Agent activity
    - Build progress
    - System events
    - Error notifications
    """
    
    def __init__(self):
        # Active connections by session
        self.connections: Dict[str, Set] = {}
        
        # Project-specific subscriptions
        self.project_subscriptions: Dict[str, Set[str]] = {}
        
        # Message queues for each connection
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        logger.info("WebSocketManager initialized")

    async def register_connection(self, session_id: str, websocket, project_id: Optional[str] = None) -> bool:
        """
        Register a new WebSocket connection.
        
        Args:
            session_id: Unique session identifier
            websocket: WebSocket connection object
            project_id: Optional project to subscribe to
            
        Returns:
            True if registration successful
        """
        try:
            # Initialize connection tracking
            if session_id not in self.connections:
                self.connections[session_id] = set()
            
            self.connections[session_id].add(websocket)
            self.message_queues[session_id] = asyncio.Queue()
            
            # Store connection metadata
            self.connection_metadata[session_id] = {
                'connected_at': datetime.now(timezone.utc).isoformat(),
                'project_id': project_id,
                'last_activity': datetime.now(timezone.utc).isoformat(),
                'message_count': 0
            }
            
            # Subscribe to project if specified
            if project_id:
                await self.subscribe_to_project(session_id, project_id)
            
            # Send welcome message
            welcome_msg = WebSocketMessage(
                type="connection_established",
                data={
                    "session_id": session_id,
                    "project_id": project_id,
                    "server_time": datetime.now(timezone.utc).isoformat()
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                session_id=session_id
            )
            
            await self.send_to_session(session_id, welcome_msg)
            
            logger.info(f"WebSocket connection registered: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register WebSocket connection {session_id}: {e}")
            return False

    async def unregister_connection(self, session_id: str, websocket) -> None:
        """Unregister a WebSocket connection."""
        try:
            # Remove from connections
            if session_id in self.connections:
                self.connections[session_id].discard(websocket)
                if not self.connections[session_id]:
                    del self.connections[session_id]
            
            # Remove from project subscriptions
            if session_id in self.connection_metadata:
                project_id = self.connection_metadata[session_id].get('project_id')
                if project_id and project_id in self.project_subscriptions:
                    self.project_subscriptions[project_id].discard(session_id)
                    if not self.project_subscriptions[project_id]:
                        del self.project_subscriptions[project_id]
            
            # Clean up queues and metadata
            self.message_queues.pop(session_id, None)
            self.connection_metadata.pop(session_id, None)
            self.rate_limits.pop(session_id, None)
            
            logger.info(f"WebSocket connection unregistered: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to unregister WebSocket connection {session_id}: {e}")

    async def subscribe_to_project(self, session_id: str, project_id: str) -> bool:
        """
        Subscribe a session to project-specific updates.
        
        Args:
            session_id: Session identifier
            project_id: Project to subscribe to
            
        Returns:
            True if subscription successful
        """
        try:
            if project_id not in self.project_subscriptions:
                self.project_subscriptions[project_id] = set()
            
            self.project_subscriptions[project_id].add(session_id)
            
            # Update connection metadata
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]['project_id'] = project_id
                self.connection_metadata[session_id]['last_activity'] = datetime.now(timezone.utc).isoformat()
            
            # Send subscription confirmation
            confirmation_msg = WebSocketMessage(
                type="subscription_confirmed",
                data={
                    "project_id": project_id,
                    "subscription_type": "project"
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                session_id=session_id,
                project_id=project_id
            )
            
            await self.send_to_session(session_id, confirmation_msg)
            
            logger.info(f"Session {session_id} subscribed to project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe {session_id} to project {project_id}: {e}")
            return False

    async def broadcast_task_update(self, task_id: str, status: str, data: Dict[str, Any], project_id: Optional[str] = None) -> None:
        """
        Broadcast task update to relevant subscribers.
        
        Args:
            task_id: Task identifier
            status: Task status
            data: Additional task data
            project_id: Optional project filter
        """
        message = WebSocketMessage(
            type="task_update",
            data={
                "task_id": task_id,
                "status": status,
                **data
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            project_id=project_id
        )
        
        if project_id:
            await self.broadcast_to_project(project_id, message)
        else:
            await self.broadcast_to_all(message)

    async def broadcast_agent_activity(self, agent_name: str, activity: str, data: Dict[str, Any], project_id: Optional[str] = None) -> None:
        """
        Broadcast agent activity to relevant subscribers.
        
        Args:
            agent_name: Name of the agent
            activity: Activity description
            data: Additional activity data
            project_id: Optional project filter
        """
        message = WebSocketMessage(
            type="agent_activity",
            data={
                "agent_name": agent_name,
                "activity": activity,
                **data
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            project_id=project_id
        )
        
        if project_id:
            await self.broadcast_to_project(project_id, message)
        else:
            await self.broadcast_to_all(message)

    async def broadcast_build_progress(self, project_id: str, stage: str, progress: float, message: str) -> None:
        """
        Broadcast build progress updates.
        
        Args:
            project_id: Project identifier
            stage: Current build stage
            progress: Progress percentage (0-100)
            message: Progress message
        """
        progress_msg = WebSocketMessage(
            type="build_progress",
            data={
                "stage": stage,
                "progress": progress,
                "message": message,
                "project_id": project_id
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            project_id=project_id
        )
        
        await self.broadcast_to_project(project_id, progress_msg)

    async def broadcast_system_event(self, event_type: str, data: Dict[str, Any], severity: str = "info") -> None:
        """
        Broadcast system-wide events.
        
        Args:
            event_type: Type of system event
            data: Event data
            severity: Event severity (info, warning, error)
        """
        message = WebSocketMessage(
            type="system_event",
            data={
                "event_type": event_type,
                "severity": severity,
                **data
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        await self.broadcast_to_all(message)

    async def broadcast_error(self, error: str, context: Dict[str, Any], project_id: Optional[str] = None) -> None:
        """
        Broadcast error notifications.
        
        Args:
            error: Error message
            context: Error context data
            project_id: Optional project filter
        """
        error_msg = WebSocketMessage(
            type="error",
            data={
                "error": error,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            project_id=project_id
        )
        
        if project_id:
            await self.broadcast_to_project(project_id, error_msg)
        else:
            await self.broadcast_to_all(error_msg)

    async def send_to_session(self, session_id: str, message: WebSocketMessage) -> bool:
        """
        Send message to a specific session.
        
        Args:
            session_id: Target session
            message: Message to send
            
        Returns:
            True if message sent successfully
        """
        try:
            if session_id not in self.connections:
                return False
            
            # Check rate limiting
            if not self._check_rate_limit(session_id):
                logger.warning(f"Rate limit exceeded for session {session_id}")
                return False
            
            # Convert message to JSON
            message_json = json.dumps(asdict(message), default=str)
            
            # Send to all websockets in the session
            disconnected = set()
            for websocket in self.connections[session_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket in session {session_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                await self.unregister_connection(session_id, ws)
            
            # Update activity tracking
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]['last_activity'] = datetime.now(timezone.utc).isoformat()
                self.connection_metadata[session_id]['message_count'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to session {session_id}: {e}")
            return False

    async def broadcast_to_project(self, project_id: str, message: WebSocketMessage) -> None:
        """Broadcast message to all sessions subscribed to a project."""
        if project_id not in self.project_subscriptions:
            return
        
        # Send to all subscribed sessions
        for session_id in self.project_subscriptions[project_id]:
            await self.send_to_session(session_id, message)

    async def broadcast_to_all(self, message: WebSocketMessage) -> None:
        """Broadcast message to all active connections."""
        for session_id in list(self.connections.keys()):
            await self.send_to_session(session_id, message)

    def _check_rate_limit(self, session_id: str) -> bool:
        """
        Check if session exceeds rate limits.
        
        Args:
            session_id: Session to check
            
        Returns:
            True if within rate limits
        """
        try:
            now = datetime.now(timezone.utc)
            
            if session_id not in self.rate_limits:
                self.rate_limits[session_id] = {
                    'messages': [],
                    'last_reset': now
                }
            
            rate_data = self.rate_limits[session_id]
            
            # Reset counter if more than 1 minute has passed
            if (now - rate_data['last_reset']).total_seconds() > 60:
                rate_data['messages'] = []
                rate_data['last_reset'] = now
            
            # Add current message
            rate_data['messages'].append(now)
            
            # Check if exceeded limit (100 messages per minute)
            if len(rate_data['messages']) > 100:
                return False
            
            return True
            
        except Exception:
            # If rate limiting fails, allow the message
            return True

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_connections = sum(len(conns) for conns in self.connections.values())
        total_sessions = len(self.connections)
        total_subscriptions = len(self.project_subscriptions)
        
        return {
            "total_connections": total_connections,
            "total_sessions": total_sessions,
            "project_subscriptions": total_subscriptions,
            "active_projects": list(self.project_subscriptions.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def cleanup_stale_connections(self) -> None:
        """Clean up stale connections."""
        try:
            now = datetime.now(timezone.utc)
            stale_sessions = []
            
            for session_id, metadata in self.connection_metadata.items():
                last_activity = datetime.fromisoformat(metadata['last_activity'])
                if (now - last_activity).total_seconds() > 3600:  # 1 hour timeout
                    stale_sessions.append(session_id)
            
            for session_id in stale_sessions:
                if session_id in self.connections:
                    for websocket in list(self.connections[session_id]):
                        await self.unregister_connection(session_id, websocket)
            
            if stale_sessions:
                logger.info(f"Cleaned up {len(stale_sessions)} stale connections")
                
        except Exception as e:
            logger.error(f"Failed to cleanup stale connections: {e}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
