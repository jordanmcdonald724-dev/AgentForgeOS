/**
 * WebSocket Hook for Real-Time UI Updates
 * 
 * Provides React hook for connecting to AgentForgeOS WebSocket
 * and receiving real-time updates for tasks, agents, and system events.
 */

import { useState, useEffect, useRef, useCallback } from 'react';

const createSessionId = (): string => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
};

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  session_id?: string;
  project_id?: string;
}

export interface WebSocketStatus {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  reconnectAttempts: number;
}

export interface UseWebSocketOptions {
  projectId?: string;
  sessionId?: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

const DEFAULT_OPTIONS: Partial<UseWebSocketOptions> = {
  autoReconnect: true,
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
};

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const [status, setStatus] = useState<WebSocketStatus>({
    connected: false,
    connecting: false,
    error: null,
    reconnectAttempts: 0,
  });

  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);

  const finalOptions = { ...DEFAULT_OPTIONS, ...options };
  const {
    projectId,
    sessionId: userSessionId,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts,
  } = finalOptions;

  // Generate or use provided session ID
  const sessionId = userSessionId || useRef<string>(createSessionId()).current;

  // WebSocket URL
  const wsUrl = projectId
    ? `ws://localhost:8000/api/ws/project/${projectId}?session_id=${sessionId}`
    : `ws://localhost:8000/api/ws/connect/${sessionId}${projectId ? `?project_id=${projectId}` : ''}`;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus(prev => ({ ...prev, connecting: true, error: null }));

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected:', sessionId);
        setStatus({
          connected: true,
          connecting: false,
          error: null,
          reconnectAttempts: 0,
        });

        // Send queued messages
        while (messageQueueRef.current.length > 0) {
          const message = messageQueueRef.current.shift();
          if (message) {
            ws.send(JSON.stringify(message));
          }
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setMessages(prev => [...prev, message]);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        wsRef.current = null;

        setStatus(prev => ({
          ...prev,
          connected: false,
          connecting: false,
        }));

        // Auto-reconnect if enabled and not a normal closure
        if (
          autoReconnect &&
          event.code !== 1000 &&
          status.reconnectAttempts < (maxReconnectAttempts || 5)
        ) {
          const timeout = setTimeout(() => {
            setStatus(prev => ({
              ...prev,
              reconnectAttempts: prev.reconnectAttempts + 1,
            }));
            connect();
          }, reconnectInterval);

          reconnectTimeoutRef.current = timeout;
        } else if (status.reconnectAttempts >= (maxReconnectAttempts || 5)) {
          setStatus(prev => ({
            ...prev,
            error: 'Max reconnection attempts reached',
          }));
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStatus(prev => ({
          ...prev,
          error: 'WebSocket connection error',
          connecting: false,
        }));
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setStatus(prev => ({
        ...prev,
        connecting: false,
        error: 'Failed to create WebSocket connection',
      }));
    }
  }, [wsUrl, sessionId, autoReconnect, reconnectInterval, maxReconnectAttempts, status.reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Disconnected by user');
      wsRef.current = null;
    }

    setStatus({
      connected: false,
      connecting: false,
      error: null,
      reconnectAttempts: 0,
    });
  }, []);

  const sendMessage = useCallback((message: any) => {
    const wsMessage: WebSocketMessage = {
      type: message.type || 'message',
      data: message.data || message,
      timestamp: new Date().toISOString(),
      session_id: sessionId,
      project_id: projectId,
    };

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(wsMessage));
    } else {
      // Queue message for when connection is established
      messageQueueRef.current.push(wsMessage);
    }
  }, [sessionId, projectId]);

  // Specific message senders
  const sendPing = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  const subscribeToProject = useCallback((newProjectId: string) => {
    sendMessage({
      type: 'subscribe_project',
      data: { project_id: newProjectId },
    });
  }, [sendMessage]);

  const getStatus = useCallback(() => {
    sendMessage({ type: 'get_status' });
  }, [sendMessage]);

  const getProjectStatus = useCallback(() => {
    if (projectId) {
      sendMessage({ type: 'request_project_status' });
    }
  }, [sendMessage, projectId]);

  // Message filters
  const getMessagesByType = useCallback((type: string) => {
    return messages.filter(msg => msg.type === type);
  }, [messages]);

  const getLastMessageByType = useCallback((type: string) => {
    const typeMessages = getMessagesByType(type);
    return typeMessages[typeMessages.length - 1] || null;
  }, [getMessagesByType]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Periodic ping to keep connection alive
  useEffect(() => {
    if (status.connected) {
      const pingInterval = setInterval(sendPing, 30000); // Ping every 30 seconds
      return () => clearInterval(pingInterval);
    }
  }, [status.connected, sendPing]);

  return {
    // Connection
    sessionId,
    status,
    connect,
    disconnect,
    
    // Messages
    messages,
    sendMessage,
    clearMessages,
    getMessagesByType,
    getLastMessageByType,
    
    // Specific actions
    sendPing,
    subscribeToProject,
    getStatus,
    getProjectStatus,
  };
};

// Specific hooks for different message types
export const useTaskUpdates = (options: UseWebSocketOptions = {}) => {
  const ws = useWebSocket(options);
  const taskMessages = ws.getMessagesByType('task_update');
  
  return {
    ...ws,
    taskUpdates: taskMessages,
    latestTaskUpdate: ws.getLastMessageByType('task_update'),
  };
};

export const useAgentActivity = (options: UseWebSocketOptions = {}) => {
  const ws = useWebSocket(options);
  const activityMessages = ws.getMessagesByType('agent_activity');
  
  return {
    ...ws,
    agentActivity: activityMessages,
    latestAgentActivity: ws.getLastMessageByType('agent_activity'),
  };
};

export const useBuildProgress = (options: UseWebSocketOptions = {}) => {
  const ws = useWebSocket(options);
  const progressMessages = ws.getMessagesByType('build_progress');
  
  return {
    ...ws,
    buildProgress: progressMessages,
    latestBuildProgress: ws.getLastMessageByType('build_progress'),
  };
};

export const useSystemEvents = (options: UseWebSocketOptions = {}) => {
  const ws = useWebSocket(options);
  const eventMessages = ws.getMessagesByType('system_event');
  const errorMessages = ws.getMessagesByType('error');
  
  return {
    ...ws,
    systemEvents: eventMessages,
    errors: errorMessages,
    latestSystemEvent: ws.getLastMessageByType('system_event'),
    latestError: ws.getLastMessageByType('error'),
  };
};
