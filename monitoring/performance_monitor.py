"""
Performance Monitoring and Metrics System

Comprehensive performance monitoring for AgentForgeOS V2,
tracking system metrics, agent performance, and resource usage.
"""

from __future__ import annotations

import asyncio
import json
import psutil
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class SystemMetric:
    """System performance metric"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int


@dataclass
class AgentMetric:
    """Agent performance metric"""
    timestamp: str
    agent_name: str
    task_id: str
    execution_time: float
    success: bool
    error_count: int
    memory_usage_mb: float
    tokens_used: int
    cost_usd: float


@dataclass
class TaskMetric:
    """Task execution metric"""
    timestamp: str
    task_id: str
    task_type: str
    status: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: float
    agents_involved: List[str]
    artifacts_created: int
    errors: List[str]


@dataclass
class PerformanceAlert:
    """Performance alert"""
    timestamp: str
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    metric_name: str
    current_value: float
    threshold: float
    context: Dict[str, Any]


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for AgentForgeOS.
    
    Monitors:
    - System resources (CPU, memory, disk, network)
    - Agent performance and efficiency
    - Task execution metrics
    - Error rates and patterns
    - Cost tracking
    - Performance alerts
    """
    
    def __init__(self, monitoring_enabled: bool = True):
        self.monitoring_enabled = monitoring_enabled
        
        # Metrics storage
        self.system_metrics: deque[SystemMetric] = deque(maxlen=1000)
        self.agent_metrics: deque[AgentMetric] = deque(maxlen=2000)
        self.task_metrics: deque[TaskMetric] = deque(maxlen=2000)
        self.performance_alerts: deque[PerformanceAlert] = deque(maxlen=500)
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'disk_warning': 90.0,
            'disk_critical': 98.0,
            'task_duration_warning': 300.0,  # 5 minutes
            'task_duration_critical': 900.0,  # 15 minutes
            'error_rate_warning': 0.1,  # 10%
            'error_rate_critical': 0.2,  # 20%
            'agent_response_time_warning': 30.0,  # 30 seconds
            'agent_response_time_critical': 60.0,  # 1 minute
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.last_network_stats = psutil.net_io_counters()
        
        # Performance aggregations
        self.hourly_stats: Dict[str, Any] = {}
        self.daily_stats: Dict[str, Any] = {}
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        logger.info("PerformanceMonitor initialized")
    
    def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start performance monitoring in background thread."""
        if not self.monitoring_enabled:
            logger.info("Performance monitoring is disabled")
            return
        
        if self.monitoring_active:
            logger.warning("Performance monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"Performance monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds: int) -> None:
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metric = self._collect_system_metrics()
                self.system_metrics.append(system_metric)
                
                # Check for performance alerts
                self._check_system_alerts(system_metric)
                
                # Update aggregations
                self._update_aggregations(system_metric)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(interval_seconds)
    
    def _collect_system_metrics(self) -> SystemMetric:
        """Collect current system metrics."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # Network metrics
        network = psutil.net_io_counters()
        network_bytes_sent = network.bytes_sent
        network_bytes_recv = network.bytes_recv
        
        # Connection count
        active_connections = len(psutil.net_connections())
        
        return SystemMetric(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            active_connections=active_connections
        )
    
    def _check_system_alerts(self, metric: SystemMetric) -> None:
        """Check for system performance alerts."""
        alerts = []
        
        # CPU alerts
        if metric.cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='cpu_usage',
                severity='critical',
                message=f'CPU usage critically high: {metric.cpu_percent:.1f}%',
                metric_name='cpu_percent',
                current_value=metric.cpu_percent,
                threshold=self.thresholds['cpu_critical'],
                context={'active_connections': metric.active_connections}
            ))
        elif metric.cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='cpu_usage',
                severity='medium',
                message=f'CPU usage high: {metric.cpu_percent:.1f}%',
                metric_name='cpu_percent',
                current_value=metric.cpu_percent,
                threshold=self.thresholds['cpu_warning'],
                context={'active_connections': metric.active_connections}
            ))
        
        # Memory alerts
        if metric.memory_percent >= self.thresholds['memory_critical']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='memory_usage',
                severity='critical',
                message=f'Memory usage critically high: {metric.memory_percent:.1f}%',
                metric_name='memory_percent',
                current_value=metric.memory_percent,
                threshold=self.thresholds['memory_critical'],
                context={'memory_used_mb': metric.memory_used_mb}
            ))
        elif metric.memory_percent >= self.thresholds['memory_warning']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='memory_usage',
                severity='medium',
                message=f'Memory usage high: {metric.memory_percent:.1f}%',
                metric_name='memory_percent',
                current_value=metric.memory_percent,
                threshold=self.thresholds['memory_warning'],
                context={'memory_used_mb': metric.memory_used_mb}
            ))
        
        # Disk alerts
        if metric.disk_usage_percent >= self.thresholds['disk_critical']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='disk_usage',
                severity='critical',
                message=f'Disk usage critically high: {metric.disk_usage_percent:.1f}%',
                metric_name='disk_usage_percent',
                current_value=metric.disk_usage_percent,
                threshold=self.thresholds['disk_critical'],
                context={}
            ))
        elif metric.disk_usage_percent >= self.thresholds['disk_warning']:
            alerts.append(PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='disk_usage',
                severity='medium',
                message=f'Disk usage high: {metric.disk_usage_percent:.1f}%',
                metric_name='disk_usage_percent',
                current_value=metric.disk_usage_percent,
                threshold=self.thresholds['disk_warning'],
                context={}
            ))
        
        # Store and trigger callbacks for alerts
        for alert in alerts:
            self.performance_alerts.append(alert)
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
    
    def record_agent_metric(self, agent_metric: AgentMetric) -> None:
        """Record agent performance metric."""
        self.agent_metrics.append(agent_metric)
        
        # Check for agent performance alerts
        self._check_agent_alerts(agent_metric)
    
    def _check_agent_alerts(self, metric: AgentMetric) -> None:
        """Check for agent performance alerts."""
        if not metric.success:
            return  # Don't alert on failed tasks
        
        # Response time alerts
        if metric.execution_time >= self.thresholds['agent_response_time_critical']:
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='agent_response_time',
                severity='critical',
                message=f'Agent {metric.agent_name} response time critical: {metric.execution_time:.1f}s',
                metric_name='execution_time',
                current_value=metric.execution_time,
                threshold=self.thresholds['agent_response_time_critical'],
                context={
                    'agent_name': metric.agent_name,
                    'task_id': metric.task_id,
                    'tokens_used': metric.tokens_used
                }
            )
            self.performance_alerts.append(alert)
        elif metric.execution_time >= self.thresholds['agent_response_time_warning']:
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='agent_response_time',
                severity='medium',
                message=f'Agent {metric.agent_name} response time high: {metric.execution_time:.1f}s',
                metric_name='execution_time',
                current_value=metric.execution_time,
                threshold=self.thresholds['agent_response_time_warning'],
                context={
                    'agent_name': metric.agent_name,
                    'task_id': metric.task_id,
                    'tokens_used': metric.tokens_used
                }
            )
            self.performance_alerts.append(alert)
    
    def record_task_metric(self, task_metric: TaskMetric) -> None:
        """Record task execution metric."""
        self.task_metrics.append(task_metric)
        
        # Check for task performance alerts
        self._check_task_alerts(task_metric)
    
    def _check_task_alerts(self, metric: TaskMetric) -> None:
        """Check for task performance alerts."""
        # Duration alerts
        if metric.duration_seconds >= self.thresholds['task_duration_critical']:
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='task_duration',
                severity='critical',
                message=f'Task {metric.task_id} duration critical: {metric.duration_seconds:.1f}s',
                metric_name='duration_seconds',
                current_value=metric.duration_seconds,
                threshold=self.thresholds['task_duration_critical'],
                context={
                    'task_id': metric.task_id,
                    'task_type': metric.task_type,
                    'agents_involved': metric.agents_involved
                }
            )
            self.performance_alerts.append(alert)
        elif metric.duration_seconds >= self.thresholds['task_duration_warning']:
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='task_duration',
                severity='medium',
                message=f'Task {metric.task_id} duration high: {metric.duration_seconds:.1f}s',
                metric_name='duration_seconds',
                current_value=metric.duration_seconds,
                threshold=self.thresholds['task_duration_warning'],
                context={
                    'task_id': metric.task_id,
                    'task_type': metric.task_type,
                    'agents_involved': metric.agents_involved
                }
            )
            self.performance_alerts.append(alert)
        
        # Error alerts
        if metric.status == 'failed':
            alert = PerformanceAlert(
                timestamp=metric.timestamp,
                alert_type='task_failure',
                severity='high',
                message=f'Task {metric.task_id} failed',
                metric_name='task_status',
                current_value=1.0,
                threshold=0.0,
                context={
                    'task_id': metric.task_id,
                    'task_type': metric.task_type,
                    'errors': metric.errors
                }
            )
            self.performance_alerts.append(alert)
    
    def _update_aggregations(self, metric: SystemMetric) -> None:
        """Update performance aggregations."""
        current_hour = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:00')
        current_day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Update hourly stats
        if current_hour not in self.hourly_stats:
            self.hourly_stats[current_hour] = {
                'cpu_samples': [],
                'memory_samples': [],
                'disk_samples': [],
                'network_sent': 0,
                'network_recv': 0,
                'connection_samples': []
            }
        
        hour_stats = self.hourly_stats[current_hour]
        hour_stats['cpu_samples'].append(metric.cpu_percent)
        hour_stats['memory_samples'].append(metric.memory_percent)
        hour_stats['disk_samples'].append(metric.disk_usage_percent)
        hour_stats['network_sent'] = metric.network_bytes_sent
        hour_stats['network_recv'] = metric.network_bytes_recv
        hour_stats['connection_samples'].append(metric.active_connections)
        
        # Update daily stats
        if current_day not in self.daily_stats:
            self.daily_stats[current_day] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
                'total_agent_calls': 0,
                'total_execution_time': 0.0,
                'total_tokens_used': 0,
                'total_cost': 0.0
            }
        
        # Clean up old aggregations (keep last 7 days)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        self.daily_stats = {
            day: stats for day, stats in self.daily_stats.items()
            if datetime.strptime(day, '%Y-%m-%d') >= cutoff_date
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        if not self.system_metrics:
            return {'status': 'no_data'}
        
        latest_metric = self.system_metrics[-1]
        
        # Calculate averages over last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_metrics = [
            m for m in self.system_metrics
            if datetime.fromisoformat(m.timestamp) >= one_hour_ago
        ]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = latest_metric.cpu_percent
            avg_memory = latest_metric.memory_percent
            avg_disk = latest_metric.disk_usage_percent
        
        return {
            'status': 'healthy',
            'timestamp': latest_metric.timestamp,
            'current': {
                'cpu_percent': latest_metric.cpu_percent,
                'memory_percent': latest_metric.memory_percent,
                'disk_usage_percent': latest_metric.disk_usage_percent,
                'active_connections': latest_metric.active_connections
            },
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'disk_usage_percent': avg_disk
            },
            'alerts_count': len(self.performance_alerts),
            'monitoring_active': self.monitoring_active
        }
    
    def get_agent_performance(self, agent_name: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get agent performance statistics."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter metrics
        if agent_name:
            filtered_metrics = [
                m for m in self.agent_metrics
                if m.agent_name == agent_name and datetime.fromisoformat(m.timestamp) >= cutoff_time
            ]
        else:
            filtered_metrics = [
                m for m in self.agent_metrics
                if datetime.fromisoformat(m.timestamp) >= cutoff_time
            ]
        
        if not filtered_metrics:
            return {'status': 'no_data'}
        
        # Calculate statistics
        total_calls = len(filtered_metrics)
        successful_calls = sum(1 for m in filtered_metrics if m.success)
        success_rate = successful_calls / total_calls if total_calls > 0 else 0
        
        execution_times = [m.execution_time for m in filtered_metrics if m.success]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        total_tokens = sum(m.tokens_used for m in filtered_metrics)
        total_cost = sum(m.cost_usd for m in filtered_metrics)
        
        # Agent breakdown
        agent_stats = {}
        for metric in filtered_metrics:
            if metric.agent_name not in agent_stats:
                agent_stats[metric.agent_name] = {
                    'calls': 0,
                    'successful': 0,
                    'avg_execution_time': 0,
                    'total_tokens': 0,
                    'total_cost': 0.0
                }
            
            stats = agent_stats[metric.agent_name]
            stats['calls'] += 1
            if metric.success:
                stats['successful'] += 1
                stats['avg_execution_time'] += metric.execution_time
            stats['total_tokens'] += metric.tokens_used
            stats['total_cost'] += metric.cost_usd
        
        # Calculate averages
        for stats in agent_stats.values():
            if stats['successful'] > 0:
                stats['avg_execution_time'] /= stats['successful']
            stats['success_rate'] = stats['successful'] / stats['calls']
        
        return {
            'period_hours': hours,
            'total_calls': total_calls,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'agent_breakdown': agent_stats
        }
    
    def get_task_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get task execution performance."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        filtered_metrics = [
            m for m in self.task_metrics
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not filtered_metrics:
            return {'status': 'no_data'}
        
        # Calculate statistics
        total_tasks = len(filtered_metrics)
        completed_tasks = sum(1 for m in filtered_metrics if m.status == 'completed')
        failed_tasks = sum(1 for m in filtered_metrics if m.status == 'failed')
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        durations = [m.duration_seconds for m in filtered_metrics if m.end_time]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Task type breakdown
        task_types = {}
        for metric in filtered_metrics:
            task_type = metric.task_type
            if task_type not in task_types:
                task_types[task_type] = {
                    'total': 0,
                    'completed': 0,
                    'failed': 0,
                    'avg_duration': 0.0
                }
            
            stats = task_types[task_type]
            stats['total'] += 1
            if metric.status == 'completed':
                stats['completed'] += 1
                stats['avg_duration'] += metric.duration_seconds
            elif metric.status == 'failed':
                stats['failed'] += 1
        
        # Calculate averages
        for stats in task_types.values():
            if stats['completed'] > 0:
                stats['avg_duration'] /= stats['completed']
            stats['completion_rate'] = stats['completed'] / stats['total']
        
        return {
            'period_hours': hours,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'completion_rate': completion_rate,
            'avg_duration_seconds': avg_duration,
            'task_type_breakdown': task_types
        }
    
    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance alerts."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        filtered_alerts = [
            alert for alert in self.performance_alerts
            if datetime.fromisoformat(alert.timestamp) >= cutoff_time
            and (severity is None or alert.severity == severity)
        ]
        
        return [asdict(alert) for alert in filtered_alerts]
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'period_hours': hours,
            'system_status': self.get_system_status(),
            'agent_performance': self.get_agent_performance(hours=hours),
            'task_performance': self.get_task_performance(hours=hours),
            'alerts': self.get_alerts(hours=hours),
            'thresholds': self.thresholds
        }
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, metric_name: str, warning_threshold: float, critical_threshold: float) -> None:
        """Set performance thresholds for a metric."""
        self.thresholds[f'{metric_name}_warning'] = warning_threshold
        self.thresholds[f'{metric_name}_critical'] = critical_threshold
        logger.info(f"Updated thresholds for {metric_name}: warning={warning_threshold}, critical={critical_threshold}")
    
    def export_metrics(self, file_path: str, hours: int = 24) -> None:
        """Export metrics to file."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter metrics
        system_data = [
            asdict(m) for m in self.system_metrics
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        agent_data = [
            asdict(m) for m in self.agent_metrics
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        task_data = [
            asdict(m) for m in self.task_metrics
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        alert_data = [
            asdict(a) for a in self.performance_alerts
            if datetime.fromisoformat(a.timestamp) >= cutoff_time
        ]
        
        export_data = {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'period_hours': hours,
            'system_metrics': system_data,
            'agent_metrics': agent_data,
            'task_metrics': task_data,
            'alerts': alert_data,
            'thresholds': self.thresholds
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {file_path}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
