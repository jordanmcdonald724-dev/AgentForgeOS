/**
 * Live Task Monitor Component
 * 
 * Real-time display of task execution status and agent activity
 * using WebSocket connections for live updates.
 */

import React, { useState, useEffect } from 'react';

// Simple UI components (replace with actual UI library components)
const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`border rounded-lg shadow-sm ${className}`}>{children}</div>
);

const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`p-4 border-b ${className}`}>{children}</div>
);

const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`p-4 ${className}`}>{children}</div>
);

const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>
);

const Badge: React.FC<{ children: React.ReactNode; variant?: string; className?: string }> = ({ 
  children, 
  variant = 'default', 
  className = '' 
}) => {
  const baseClasses = 'px-2 py-1 rounded text-xs font-medium';
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    outline: 'border border-gray-300 text-gray-700',
  };
  return (
    <span className={`${baseClasses} ${variantClasses[variant as keyof typeof variantClasses]} ${className}`}>
      {children}
    </span>
  );
};

const Progress: React.FC<{ value: number; className?: string }> = ({ value, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
    <div 
      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
      style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
    />
  </div>
);
import { useTaskUpdates, useAgentActivity } from '../../hooks/useWebSocket';

interface Task {
  task_id: string;
  status: string;
  assigned_agent: string;
  description?: string;
  progress?: number;
  started_at?: string;
  completed_at?: string;
}

interface AgentActivity {
  agent_name: string;
  activity: string;
  timestamp: string;
  details?: any;
}

export const LiveTaskMonitor: React.FC<{ projectId?: string }> = ({ projectId }) => {
  const { taskUpdates, latestTaskUpdate, status: wsStatus } = useTaskUpdates({ projectId });
  const { agentActivity, latestAgentActivity } = useAgentActivity({ projectId });
  
  const [tasks, setTasks] = useState<Task[]>([]);
  const [agents, setAgents] = useState<Record<string, AgentActivity>>({});

  // Process task updates
  useEffect(() => {
    if (latestTaskUpdate) {
      const taskData = latestTaskUpdate.data;
      
      setTasks(prev => {
        const existingIndex = prev.findIndex(t => t.task_id === taskData.task_id);
        
        if (existingIndex >= 0) {
          // Update existing task
          const updated = [...prev];
          updated[existingIndex] = {
            ...updated[existingIndex],
            ...taskData,
            progress: taskData.progress || updated[existingIndex].progress,
          };
          return updated;
        } else {
          // Add new task
          return [...prev, {
            task_id: taskData.task_id,
            status: taskData.status,
            assigned_agent: taskData.assigned_agent,
            description: taskData.description,
            progress: taskData.progress || 0,
            started_at: taskData.started_at || latestTaskUpdate.timestamp,
          }];
        }
      });
    }
  }, [latestTaskUpdate]);

  // Process agent activity
  useEffect(() => {
    if (latestAgentActivity) {
      const activityData = latestAgentActivity.data;
      
      setAgents(prev => ({
        ...prev,
        [activityData.agent_name]: {
          agent_name: activityData.agent_name,
          activity: activityData.activity,
          timestamp: latestAgentActivity.timestamp,
          details: activityData,
        },
      }));
    }
  }, [latestAgentActivity]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-500';
      case 'running': return 'bg-blue-500';
      case 'failed': return 'bg-red-500';
      case 'pending': return 'bg-gray-500';
      case 'blocked': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    const colorClass = getStatusColor(status);
    return (
      <Badge className={`${colorClass} text-white`}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  const runningTasks = tasks.filter(t => t.status === 'running');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');

  if (!wsStatus.connected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            Live Task Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <div className="mb-2">🔌 Disconnected</div>
            <div className="text-sm">Attempting to reconnect... ({wsStatus.reconnectAttempts})</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            Live Task Monitor
            <Badge variant="outline" className="ml-auto">
              {projectId ? `Project: ${projectId}` : 'Global'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="font-semibold text-lg">{runningTasks.length}</div>
              <div className="text-gray-500">Running</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-lg text-green-600">{completedTasks.length}</div>
              <div className="text-gray-500">Completed</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-lg text-red-600">{failedTasks.length}</div>
              <div className="text-gray-500">Failed</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-lg">{tasks.length}</div>
              <div className="text-gray-500">Total</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Running Tasks */}
      {runningTasks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Running Tasks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {runningTasks.map(task => (
              <div key={task.task_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium">{task.task_id}</div>
                  {getStatusBadge(task.status)}
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  Agent: {task.assigned_agent}
                </div>
                
                {task.description && (
                  <div className="text-sm text-gray-600 mb-2">
                    {task.description}
                  </div>
                )}
                
                {task.progress !== undefined && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>{task.progress}%</span>
                    </div>
                    <Progress value={task.progress} className="h-2" />
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Agent Activity */}
      {Object.keys(agents).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Agent Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.values(agents).slice(-5).reverse().map((activity, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{activity.agent_name}</div>
                  <div className="text-sm text-gray-600">{activity.activity}</div>
                </div>
                <div className="text-xs text-gray-400">
                  {new Date(activity.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Recent Completed Tasks */}
      {completedTasks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recently Completed</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {completedTasks.slice(-5).reverse().map(task => (
              <div key={task.task_id} className="flex items-center gap-3 p-2 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <span className="font-medium">{task.task_id}</span>
                  <span className="text-gray-500 ml-2">({task.assigned_agent})</span>
                </div>
                <div className="text-xs text-gray-400">
                  {task.completed_at ? new Date(task.completed_at).toLocaleTimeString() : 'Just now'}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* No Activity */}
      {tasks.length === 0 && Object.keys(agents).length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <div className="text-gray-500">
              <div className="text-4xl mb-2">🔄</div>
              <div>Waiting for activity...</div>
              <div className="text-sm mt-1">Tasks and agent activity will appear here</div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
