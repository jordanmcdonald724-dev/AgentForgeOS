"""
Monitoring API Routes

Provides REST API endpoints for performance monitoring,
metrics collection, and system health status.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from monitoring.performance_monitor import performance_monitor, PerformanceAlert


# Create router
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# Request/Response Models
class SystemStatusResponse(BaseModel):
    """System status response model"""
    status: str
    timestamp: str
    current: Dict[str, Any]
    averages: Dict[str, Any]
    alerts_count: int
    monitoring_active: bool


class AgentPerformanceResponse(BaseModel):
    """Agent performance response model"""
    period_hours: int
    total_calls: int
    success_rate: float
    avg_execution_time: float
    total_tokens: int
    total_cost: float
    agent_breakdown: Dict[str, Any]


class TaskPerformanceResponse(BaseModel):
    """Task performance response model"""
    period_hours: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    completion_rate: float
    avg_duration_seconds: float
    task_type_breakdown: Dict[str, Any]


class AlertResponse(BaseModel):
    """Alert response model"""
    timestamp: str
    alert_type: str
    severity: str
    message: str
    metric_name: str
    current_value: float
    threshold: float
    context: Dict[str, Any]


class PerformanceReportResponse(BaseModel):
    """Performance report response model"""
    generated_at: str
    period_hours: int
    system_status: Dict[str, Any]
    agent_performance: Dict[str, Any]
    task_performance: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    thresholds: Dict[str, float]


class ThresholdUpdateRequest(BaseModel):
    """Threshold update request model"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float


@monitoring_router.get("/system/status")
async def get_system_status() -> SystemStatusResponse:
    """Get current system status and performance metrics."""
    try:
        status_data = performance_monitor.get_system_status()
        return SystemStatusResponse(**status_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/system/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check endpoint."""
    try:
        status = performance_monitor.get_system_status()
        
        # Determine overall health
        if status.get('status') == 'no_data':
            health_status = 'unknown'
            health_code = 503
        elif status.get('alerts_count', 0) > 10:
            health_status = 'degraded'
            health_code = 200
        elif status.get('current', {}).get('cpu_percent', 0) > 95:
            health_status = 'critical'
            health_code = 503
        elif status.get('current', {}).get('memory_percent', 0) > 95:
            health_status = 'critical'
            health_code = 503
        else:
            health_status = 'healthy'
            health_code = 200
        
        return {
            'status': health_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'monitoring_active': performance_monitor.monitoring_active,
            'details': status
        }
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }


@monitoring_router.get("/agents/performance")
async def get_agent_performance(
    agent_name: Optional[str] = Query(None, description="Specific agent name"),
    hours: int = Query(24, ge=1, le=168, description="Period in hours (1-168)")
) -> AgentPerformanceResponse:
    """Get agent performance statistics."""
    try:
        performance_data = performance_monitor.get_agent_performance(agent_name, hours)
        return AgentPerformanceResponse(**performance_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/tasks/performance")
async def get_task_performance(
    hours: int = Query(24, ge=1, le=168, description="Period in hours (1-168)")
) -> TaskPerformanceResponse:
    """Get task execution performance."""
    try:
        performance_data = performance_monitor.get_task_performance(hours)
        return TaskPerformanceResponse(**performance_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    hours: int = Query(24, ge=1, le=168, description="Period in hours (1-168)")
) -> List[AlertResponse]:
    """Get performance alerts."""
    try:
        alerts_data = performance_monitor.get_alerts(severity, hours)
        return [AlertResponse(**alert) for alert in alerts_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/report")
async def get_performance_report(
    hours: int = Query(24, ge=1, le=168, description="Period in hours (1-168)")
) -> PerformanceReportResponse:
    """Generate comprehensive performance report."""
    try:
        report_data = performance_monitor.get_performance_report(hours)
        return PerformanceReportResponse(**report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.post("/thresholds")
async def update_thresholds(request: ThresholdUpdateRequest) -> Dict[str, Any]:
    """Update performance thresholds."""
    try:
        performance_monitor.set_threshold(
            request.metric_name,
            request.warning_threshold,
            request.critical_threshold
        )
        
        return {
            "success": True,
            "message": f"Thresholds updated for {request.metric_name}",
            "warning_threshold": request.warning_threshold,
            "critical_threshold": request.critical_threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/thresholds")
async def get_thresholds() -> Dict[str, float]:
    """Get current performance thresholds."""
    try:
        return performance_monitor.thresholds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.post("/start")
async def start_monitoring(
    interval_seconds: int = Query(30, ge=10, le=300, description="Monitoring interval in seconds")
) -> Dict[str, Any]:
    """Start performance monitoring."""
    try:
        if performance_monitor.monitoring_active:
            return {
                "success": False,
                "message": "Monitoring is already active"
            }
        
        performance_monitor.start_monitoring(interval_seconds)
        
        return {
            "success": True,
            "message": f"Monitoring started with {interval_seconds}s interval",
            "interval_seconds": interval_seconds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.post("/stop")
async def stop_monitoring() -> Dict[str, Any]:
    """Stop performance monitoring."""
    try:
        if not performance_monitor.monitoring_active:
            return {
                "success": False,
                "message": "Monitoring is not active"
            }
        
        performance_monitor.stop_monitoring()
        
        return {
            "success": True,
            "message": "Monitoring stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/metrics/export")
async def export_metrics(
    hours: int = Query(24, ge=1, le=168, description="Period in hours (1-168)")
) -> Dict[str, Any]:
    """Export metrics data for download."""
    try:
        # Generate export data
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        system_data = [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "disk_usage_percent": m.disk_usage_percent,
                "active_connections": m.active_connections
            }
            for m in performance_monitor.system_metrics
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "period_hours": hours,
            "system_metrics": system_data,
            "total_metrics": len(system_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/dashboard")
async def get_dashboard_data() -> Dict[str, Any]:
    """Get consolidated dashboard data."""
    try:
        # Get recent metrics
        system_status = performance_monitor.get_system_status()
        agent_perf = performance_monitor.get_agent_performance(hours=1)
        task_perf = performance_monitor.get_task_performance(hours=1)
        recent_alerts = performance_monitor.get_alerts(hours=1)
        
        # Calculate summary metrics
        total_alerts = len(recent_alerts)
        critical_alerts = len([a for a in recent_alerts if a.get('severity') == 'critical'])
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "status": system_status.get('status', 'unknown'),
                "cpu_percent": system_status.get('current', {}).get('cpu_percent', 0),
                "memory_percent": system_status.get('current', {}).get('memory_percent', 0),
                "disk_usage_percent": system_status.get('current', {}).get('disk_usage_percent', 0),
                "active_connections": system_status.get('current', {}).get('active_connections', 0)
            },
            "agents": {
                "total_calls": agent_perf.get('total_calls', 0),
                "success_rate": agent_perf.get('success_rate', 0),
                "avg_execution_time": agent_perf.get('avg_execution_time', 0)
            },
            "tasks": {
                "total_tasks": task_perf.get('total_tasks', 0),
                "completion_rate": task_perf.get('completion_rate', 0),
                "avg_duration": task_perf.get('avg_duration_seconds', 0)
            },
            "alerts": {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "recent_alerts": recent_alerts[:5]  # Last 5 alerts
            },
            "monitoring": {
                "active": performance_monitor.monitoring_active,
                "metrics_count": len(performance_monitor.system_metrics)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent metric recording endpoint (for internal use)
@monitoring_router.post("/metrics/agent")
async def record_agent_metric(
    agent_name: str,
    task_id: str,
    execution_time: float,
    success: bool,
    tokens_used: int = 0,
    cost_usd: float = 0.0,
    memory_usage_mb: float = 0.0,
    error_count: int = 0
) -> Dict[str, Any]:
    """Record agent performance metric."""
    try:
        from monitoring.performance_monitor import AgentMetric
        
        metric = AgentMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            task_id=task_id,
            execution_time=execution_time,
            success=success,
            error_count=error_count,
            memory_usage_mb=memory_usage_mb,
            tokens_used=tokens_used,
            cost_usd=cost_usd
        )
        
        performance_monitor.record_agent_metric(metric)
        
        return {
            "success": True,
            "message": f"Agent metric recorded for {agent_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Task metric recording endpoint (for internal use)
@monitoring_router.post("/metrics/task")
async def record_task_metric(
    task_id: str,
    task_type: str,
    status: str,
    start_time: str,
    end_time: Optional[str] = None,
    agents_involved: list[str] = [],
    artifacts_created: int = 0,
    errors: list[str] = []
) -> Dict[str, Any]:
    """Record task execution metric."""
    try:
        from monitoring.performance_monitor import TaskMetric
        
        # Calculate duration
        duration_seconds = 0
        if end_time and start_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration_seconds = (end_dt - start_dt).total_seconds()
        
        metric = TaskMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            task_type=task_type,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            agents_involved=agents_involved,
            artifacts_created=artifacts_created,
            errors=errors
        )
        
        performance_monitor.record_task_metric(metric)
        
        return {
            "success": True,
            "message": f"Task metric recorded for {task_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
