#!/usr/bin/env python3
"""
Grimoire Familiar Debugging Tools

This module provides debugging and monitoring tools for the familiar messaging
system, including message tracing, performance monitoring, and error analysis.
"""

import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
from datetime import datetime

from .messaging import FamiliarMessage, MessageType, MessagePriority, MessageRouter


@dataclass
class MessageTrace:
    """Trace information for a message's journey through the system."""
    message_id: str
    start_time: float
    end_time: Optional[float] = None
    sender_name: str = ""
    recipient_name: str = ""
    message_type: str = ""
    route_path: List[str] = field(default_factory=list)
    delivery_status: str = "PENDING"  # PENDING, DELIVERED, FAILED, EXPIRED
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    def mark_delivered(self):
        """Mark the message as successfully delivered."""
        self.end_time = time.time()
        self.delivery_status = "DELIVERED"
        self.processing_time = self.end_time - self.start_time
    
    def mark_failed(self, error: str):
        """Mark the message as failed with error information."""
        self.end_time = time.time()
        self.delivery_status = "FAILED"
        self.error_message = error
        self.processing_time = self.end_time - self.start_time
    
    def mark_expired(self):
        """Mark the message as expired."""
        self.end_time = time.time()
        self.delivery_status = "EXPIRED"
        self.processing_time = self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "sender_name": self.sender_name,
            "recipient_name": self.recipient_name,
            "message_type": self.message_type,
            "route_path": self.route_path,
            "delivery_status": self.delivery_status,
            "error_message": self.error_message,
            "processing_time": self.processing_time
        }


class MessageTracer:
    """
    Traces message flow through the familiar system for debugging.
    
    Provides detailed logging of message routing, delivery times,
    and error conditions for system debugging and optimization.
    """
    
    def __init__(self, max_traces: int = 10000):
        self.max_traces = max_traces
        self.traces: Dict[str, MessageTrace] = {}
        self.trace_history: deque = deque(maxlen=max_traces)
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_messages": 0,
            "delivered_messages": 0,
            "failed_messages": 0,
            "expired_messages": 0,
            "average_processing_time": 0.0,
            "max_processing_time": 0.0,
            "min_processing_time": float('inf')
        }
        
        # Performance tracking
        self.performance_buckets = defaultdict(list)  # message_type -> [processing_times]
        self.route_performance = defaultdict(list)    # route_path -> [processing_times]
    
    def start_trace(self, message: FamiliarMessage) -> None:
        """Start tracing a message."""
        with self.lock:
            trace = MessageTrace(
                message_id=message.message_id,
                start_time=time.time(),
                sender_name=message.sender_name,
                recipient_name=message.recipient_name,
                message_type=message.message_type.name,
                route_path=message.route_history.copy()
            )
            
            self.traces[message.message_id] = trace
            self.stats["total_messages"] += 1
    
    def update_trace(self, message: FamiliarMessage) -> None:
        """Update trace with routing information."""
        with self.lock:
            if message.message_id in self.traces:
                trace = self.traces[message.message_id]
                trace.route_path = message.route_history.copy()
    
    def end_trace(self, message_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """End tracing for a message."""
        with self.lock:
            if message_id not in self.traces:
                return
            
            trace = self.traces[message_id]
            
            if success:
                trace.mark_delivered()
                self.stats["delivered_messages"] += 1
            elif error and "expired" in error.lower():
                trace.mark_expired()
                self.stats["expired_messages"] += 1
            else:
                trace.mark_failed(error or "Unknown error")
                self.stats["failed_messages"] += 1
            
            # Update performance statistics
            if trace.processing_time is not None:
                self._update_performance_stats(trace)
            
            # Move to history
            self.trace_history.append(trace)
            del self.traces[message_id]
    
    def _update_performance_stats(self, trace: MessageTrace) -> None:
        """Update performance statistics with completed trace."""
        processing_time = trace.processing_time
        
        # Update overall stats
        total_delivered = self.stats["delivered_messages"]
        if total_delivered > 0:
            current_avg = self.stats["average_processing_time"]
            self.stats["average_processing_time"] = (
                (current_avg * (total_delivered - 1) + processing_time) / total_delivered
            )
        
        self.stats["max_processing_time"] = max(self.stats["max_processing_time"], processing_time or 0.0)
        self.stats["min_processing_time"] = min(self.stats["min_processing_time"], processing_time or 0.0)
        
        # Update type-specific performance
        self.performance_buckets[trace.message_type].append(processing_time)
        
        # Update route-specific performance
        route_key = " -> ".join(trace.route_path)
        self.route_performance[route_key].append(processing_time)
    
    def get_trace(self, message_id: str) -> Optional[MessageTrace]:
        """Get trace information for a specific message."""
        with self.lock:
            return self.traces.get(message_id) or next(
                (trace for trace in self.trace_history if trace.message_id == message_id), None
            )
    
    def get_active_traces(self) -> List[MessageTrace]:
        """Get all currently active traces."""
        with self.lock:
            return list(self.traces.values())
    
    def get_trace_history(self, limit: int = 100) -> List[MessageTrace]:
        """Get recent trace history."""
        with self.lock:
            return list(self.trace_history)[-limit:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        with self.lock:
            report = {
                "overall_stats": self.stats.copy(),
                "message_type_performance": {},
                "route_performance": {},
                "slow_messages": [],
                "failed_messages": []
            }
            
            # Message type performance
            for msg_type, times in self.performance_buckets.items():
                if times:
                    report["message_type_performance"][msg_type] = {
                        "count": len(times),
                        "average_time": sum(times) / len(times),
                        "max_time": max(times),
                        "min_time": min(times)
                    }
            
            # Route performance
            for route, times in self.route_performance.items():
                if times:
                    report["route_performance"][route] = {
                        "count": len(times),
                        "average_time": sum(times) / len(times),
                        "max_time": max(times),
                        "min_time": min(times)
                    }
            
            # Slow messages (top 10)
            slow_threshold = self.stats["average_processing_time"] * 2
            slow_messages = [
                trace for trace in self.trace_history
                if trace.processing_time and trace.processing_time > slow_threshold
            ]
            slow_messages.sort(key=lambda t: t.processing_time or 0, reverse=True)
            report["slow_messages"] = [trace.to_dict() for trace in slow_messages[:10]]
            
            # Failed messages
            failed_messages = [
                trace for trace in self.trace_history
                if trace.delivery_status == "FAILED"
            ]
            report["failed_messages"] = [trace.to_dict() for trace in failed_messages[-10:]]
            
            return report
    
    def clear_history(self) -> None:
        """Clear trace history."""
        with self.lock:
            self.trace_history.clear()
            self.performance_buckets.clear()
            self.route_performance.clear()
    
    def export_traces(self, filename: str) -> None:
        """Export trace history to JSON file."""
        with self.lock:
            traces_data = [trace.to_dict() for trace in self.trace_history]
            
        with open(filename, 'w') as f:
            json.dump({
                "export_time": datetime.now().isoformat(),
                "stats": self.stats,
                "traces": traces_data
            }, f, indent=2)


class MessageMonitor:
    """
    Real-time monitoring of familiar message system.
    
    Provides live statistics, alerts, and health monitoring
    for the message routing system.
    """
    
    def __init__(self, tracer: MessageTracer):
        self.tracer = tracer
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "max_processing_time": 5.0,     # seconds
            "max_queue_size": 1000,         # messages
            "max_failure_rate": 0.1,        # 10% failure rate
            "max_expired_rate": 0.05        # 5% expiration rate
        }
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = 30.0  # seconds
    
    def start_monitoring(self) -> None:
        """Start real-time monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._check_system_health()
                time.sleep(self.check_interval)
            except Exception as e:
                self._add_alert("MONITOR_ERROR", f"Monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def _check_system_health(self) -> None:
        """Check system health and generate alerts."""
        stats = self.tracer.stats
        
        # Check processing time
        if stats["max_processing_time"] > self.thresholds["max_processing_time"]:
            self._add_alert("SLOW_PROCESSING", 
                          f"Max processing time {stats['max_processing_time']:.2f}s exceeds threshold")
        
        # Check failure rate
        total_messages = stats["total_messages"]
        if total_messages > 0:
            failure_rate = stats["failed_messages"] / total_messages
            if failure_rate > self.thresholds["max_failure_rate"]:
                self._add_alert("HIGH_FAILURE_RATE", 
                              f"Failure rate {failure_rate:.2%} exceeds threshold")
            
            # Check expiration rate
            expiry_rate = stats["expired_messages"] / total_messages
            if expiry_rate > self.thresholds["max_expired_rate"]:
                self._add_alert("HIGH_EXPIRY_RATE", 
                              f"Expiry rate {expiry_rate:.2%} exceeds threshold")
    
    def _add_alert(self, alert_type: str, message: str) -> None:
        """Add a new alert."""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
    
    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return self.alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
    
    def set_threshold(self, threshold_name: str, value: float) -> None:
        """Set monitoring threshold."""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get live system statistics."""
        return {
            "tracer_stats": self.tracer.stats,
            "active_traces": len(self.tracer.get_active_traces()),
            "recent_alerts": len([a for a in self.alerts if time.time() - a["timestamp"] < 300]),
            "monitoring_active": self.monitoring_active,
            "thresholds": self.thresholds
        }


class DebugMessageRouter(MessageRouter):
    """
    Enhanced MessageRouter with integrated debugging capabilities.
    
    Extends the base MessageRouter with automatic tracing,
    monitoring, and debugging features.
    """
    
    def __init__(self, name: str = "DebugMessageRouter"):
        super().__init__(name)
        self.tracer = MessageTracer()
        self.monitor = MessageMonitor(self.tracer)
        self.debug_enabled = True
        
        # Start monitoring by default
        self.monitor.start_monitoring()
    
    def route_message(self, message: FamiliarMessage) -> bool:
        """Route message with debugging support."""
        if self.debug_enabled:
            self.tracer.start_trace(message)
        
        try:
            result = super().route_message(message)
            
            if self.debug_enabled:
                if result:
                    self.tracer.end_trace(message.message_id, success=True)
                else:
                    self.tracer.end_trace(message.message_id, success=False, error="Routing failed")
            
            return result
            
        except Exception as e:
            if self.debug_enabled:
                self.tracer.end_trace(message.message_id, success=False, error=str(e))
            raise
    
    def _deliver_message(self, message: FamiliarMessage, destination: str) -> bool:
        """Deliver message with trace updates."""
        if self.debug_enabled:
            self.tracer.update_trace(message)
        
        return super()._deliver_message(message, destination)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get comprehensive debugging information."""
        return {
            "router_stats": self.get_statistics(),
            "tracer_performance": self.tracer.get_performance_report(),
            "monitor_alerts": self.monitor.get_alerts(),
            "live_stats": self.monitor.get_live_stats()
        }
    
    def enable_debug(self) -> None:
        """Enable debugging features."""
        self.debug_enabled = True
        self.monitor.start_monitoring()
    
    def disable_debug(self) -> None:
        """Disable debugging features."""
        self.debug_enabled = False
        self.monitor.stop_monitoring()
    
    def export_debug_data(self, filename: str) -> None:
        """Export all debugging data to file."""
        debug_data = self.get_debug_info()
        
        with open(filename, 'w') as f:
            json.dump(debug_data, f, indent=2, default=str)
    
    def __del__(self):
        """Cleanup when router is destroyed."""
        if hasattr(self, 'monitor'):
            self.monitor.stop_monitoring()


# Convenience functions for debugging
def create_debug_router(name: str = "DebugRouter") -> DebugMessageRouter:
    """Create a debug-enabled message router."""
    return DebugMessageRouter(name)


def analyze_message_flow(traces: List[MessageTrace]) -> Dict[str, Any]:
    """Analyze message flow patterns from traces."""
    analysis = {
        "total_messages": len(traces),
        "delivery_success_rate": 0.0,
        "average_hops": 0.0,
        "common_routes": defaultdict(int),
        "bottlenecks": [],
        "error_patterns": defaultdict(int)
    }
    
    if not traces:
        return analysis
    
    # Calculate success rate
    delivered = sum(1 for t in traces if t.delivery_status == "DELIVERED")
    analysis["delivery_success_rate"] = delivered / len(traces)
    
    # Calculate average hops
    total_hops = sum(len(t.route_path) for t in traces)
    analysis["average_hops"] = total_hops / len(traces)
    
    # Find common routes
    for trace in traces:
        route = " -> ".join(trace.route_path)
        analysis["common_routes"][route] += 1
    
    # Find bottlenecks (routes with high processing times)
    route_times = defaultdict(list)
    for trace in traces:
        if trace.processing_time:
            route = " -> ".join(trace.route_path)
            route_times[route].append(trace.processing_time)
    
    for route, times in route_times.items():
        if len(times) > 1:
            avg_time = sum(times) / len(times)
            analysis["bottlenecks"].append({
                "route": route,
                "average_time": avg_time,
                "message_count": len(times)
            })
    
    # Sort bottlenecks by average time
    analysis["bottlenecks"].sort(key=lambda x: x["average_time"], reverse=True)
    
    # Find error patterns
    for trace in traces:
        if trace.delivery_status == "FAILED" and trace.error_message:
            analysis["error_patterns"][trace.error_message] += 1
    
    return analysis