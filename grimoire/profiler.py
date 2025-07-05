#!/usr/bin/env python3
"""
Grimoire Performance Profiler

This module provides comprehensive profiling tools for AI familiars,
familiar operations, socket communications, and overall system performance.
"""

import time
import threading
import gc
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
import functools
import inspect

# Optional psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. System monitoring will be limited.")


@dataclass
class ProfileSample:
    """A single performance measurement sample."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_before: Optional[int] = None
    memory_after: Optional[int] = None
    memory_delta: Optional[int] = None
    cpu_percent: Optional[float] = None
    thread_id: int = field(default_factory=lambda: threading.get_ident())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, memory_after: Optional[int] = None, cpu_percent: Optional[float] = None):
        """Complete the profiling sample."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        if memory_after is not None and self.memory_before is not None:
            self.memory_after = memory_after
            self.memory_delta = memory_after - self.memory_before
        
        if cpu_percent is not None:
            self.cpu_percent = cpu_percent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sample to dictionary."""
        return {
            "name": self.name,
            "duration": self.duration,
            "memory_delta": self.memory_delta,
            "cpu_percent": self.cpu_percent,
            "thread_id": self.thread_id,
            "metadata": self.metadata
        }


class PerformanceProfiler:
    """
    Comprehensive performance profiler for Grimoire systems.
    
    Tracks execution time, memory usage, CPU utilization,
    and provides detailed analysis of system performance.
    """
    
    def __init__(self, max_samples: int = 10000):
        self.max_samples = max_samples
        self.samples: deque = deque(maxlen=max_samples)
        self.active_samples: Dict[str, ProfileSample] = {}
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_samples": 0,
            "average_duration": 0.0,
            "max_duration": 0.0,
            "min_duration": float('inf'),
            "total_memory_allocated": 0,
            "peak_memory_usage": 0,
            "average_cpu_usage": 0.0
        }
        
        # Category-specific tracking
        self.category_stats = defaultdict(lambda: {
            "count": 0,
            "total_duration": 0.0,
            "average_duration": 0.0,
            "max_duration": 0.0,
            "min_duration": float('inf'),
            "total_memory": 0,
            "average_memory": 0.0
        })
        
        # Process monitoring
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        else:
            self.process = None
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def start_sample(self, name: str, category: str = "general", **metadata) -> str:
        """Start a new performance sample."""
        sample_id = f"{name}_{time.time()}_{threading.get_ident()}"
        
        # Get current memory usage
        try:
            memory_before = self.process.memory_info().rss if self.process else None
        except:
            memory_before = None
        
        sample = ProfileSample(
            name=name,
            start_time=time.time(),
            memory_before=memory_before,
            metadata={"category": category, **metadata}
        )
        
        with self.lock:
            self.active_samples[sample_id] = sample
        
        return sample_id
    
    def end_sample(self, sample_id: str) -> Optional[ProfileSample]:
        """End a performance sample."""
        with self.lock:
            if sample_id not in self.active_samples:
                return None
            
            sample = self.active_samples.pop(sample_id)
        
        # Get current memory and CPU usage
        try:
            memory_after = self.process.memory_info().rss if self.process else None
            cpu_percent = self.process.cpu_percent() if self.process else None
        except:
            memory_after = None
            cpu_percent = None
        
        sample.complete(memory_after, cpu_percent)
        
        with self.lock:
            self.samples.append(sample)
            self._update_stats(sample)
        
        return sample
    
    def _update_stats(self, sample: ProfileSample) -> None:
        """Update statistics with new sample."""
        self.stats["total_samples"] += 1
        
        if sample.duration is not None:
            # Update overall duration stats
            total_samples = self.stats["total_samples"]
            current_avg = self.stats["average_duration"]
            self.stats["average_duration"] = (
                (current_avg * (total_samples - 1) + sample.duration) / total_samples
            )
            
            self.stats["max_duration"] = max(self.stats["max_duration"], sample.duration)
            self.stats["min_duration"] = min(self.stats["min_duration"], sample.duration)
            
            # Update category stats
            category = sample.metadata.get("category", "general")
            cat_stats = self.category_stats[category]
            cat_stats["count"] += 1
            cat_stats["total_duration"] += sample.duration
            cat_stats["average_duration"] = cat_stats["total_duration"] / cat_stats["count"]
            cat_stats["max_duration"] = max(cat_stats["max_duration"], sample.duration)
            cat_stats["min_duration"] = min(cat_stats["min_duration"], sample.duration)
        
        if sample.memory_delta is not None:
            if sample.memory_delta > 0:
                self.stats["total_memory_allocated"] += sample.memory_delta
            
            if sample.memory_after is not None:
                self.stats["peak_memory_usage"] = max(
                    self.stats["peak_memory_usage"], sample.memory_after
                )
            
            # Update category memory stats
            category = sample.metadata.get("category", "general")
            cat_stats = self.category_stats[category]
            if sample.memory_delta > 0:
                cat_stats["total_memory"] += sample.memory_delta
                cat_stats["average_memory"] = cat_stats["total_memory"] / cat_stats["count"]
        
        if sample.cpu_percent is not None:
            total_samples = self.stats["total_samples"]
            current_avg = self.stats["average_cpu_usage"]
            self.stats["average_cpu_usage"] = (
                (current_avg * (total_samples - 1) + sample.cpu_percent) / total_samples
            )
    
    @contextmanager
    def profile(self, name: str, category: str = "general", **metadata):
        """Context manager for profiling code blocks."""
        sample_id = self.start_sample(name, category, **metadata)
        try:
            yield
        finally:
            self.end_sample(sample_id)
    
    def profile_function(self, category: str = "function"):
        """Decorator for profiling functions."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = f"{func.__module__}.{func.__qualname__}"
                with self.profile(name, category):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_report(self, category: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        with self.lock:
            report = {
                "overall_stats": self.stats.copy(),
                "category_stats": dict(self.category_stats),
                "recent_samples": [],
                "slow_operations": [],
                "memory_intensive": [],
                "system_info": self._get_system_info()
            }
            
            # Filter samples by category if specified
            samples = list(self.samples)
            if category:
                samples = [s for s in samples if s.metadata.get("category") == category]
            
            # Recent samples
            report["recent_samples"] = [s.to_dict() for s in samples[-limit:]]
            
            # Slow operations (top 10)
            slow_ops = sorted(samples, key=lambda s: s.duration or 0, reverse=True)[:10]
            report["slow_operations"] = [s.to_dict() for s in slow_ops]
            
            # Memory intensive operations
            memory_ops = sorted(
                [s for s in samples if s.memory_delta and s.memory_delta > 0],
                key=lambda s: s.memory_delta or 0,
                reverse=True
            )[:10]
            report["memory_intensive"] = [s.to_dict() for s in memory_ops]
            
            return report
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            return {
                "cpu_count": psutil.cpu_count() if PSUTIL_AVAILABLE else "N/A",
                "memory_total": psutil.virtual_memory().total if PSUTIL_AVAILABLE else "N/A",
                "memory_available": psutil.virtual_memory().available if PSUTIL_AVAILABLE else "N/A",
                "memory_percent": psutil.virtual_memory().percent if PSUTIL_AVAILABLE else "N/A",
                "process_memory": self.process.memory_info().rss if self.process and PSUTIL_AVAILABLE else "N/A",
                "process_cpu": self.process.cpu_percent() if self.process and PSUTIL_AVAILABLE else "N/A",
                "thread_count": threading.active_count(),
                "gc_objects": len(gc.get_objects())
            }
        except:
            return {"error": "Could not retrieve system info"}
    
    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start continuous system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float) -> None:
        """Continuous monitoring loop."""
        while self.monitoring_active:
            try:
                with self.profile("system_monitor", "monitoring"):
                    # This will automatically track system resource usage
                    time.sleep(0.1)  # Small delay for measurement
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def clear_samples(self) -> None:
        """Clear all samples and reset statistics."""
        with self.lock:
            self.samples.clear()
            self.active_samples.clear()
            self.stats = {
                "total_samples": 0,
                "average_duration": 0.0,
                "max_duration": 0.0,
                "min_duration": float('inf'),
                "total_memory_allocated": 0,
                "peak_memory_usage": 0,
                "average_cpu_usage": 0.0
            }
            self.category_stats.clear()
    
    def export_report(self, filename: str, category: Optional[str] = None) -> None:
        """Export performance report to file."""
        import json
        
        report = self.get_report(category)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)


class AIFamiliarProfiler:
    """
    Specialized profiler for AI familiar operations.
    
    Tracks AI decision making, goal evaluation, action execution,
    and provides insights into AI performance patterns.
    """
    
    def __init__(self, profiler: PerformanceProfiler):
        self.profiler = profiler
        self.ai_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "decision_count": 0,
            "goal_evaluations": 0,
            "action_executions": 0,
            "total_decision_time": 0.0,
            "average_decision_time": 0.0,
            "goal_satisfaction_history": [],
            "action_success_rate": 0.0,
            "actions_successful": 0,
            "actions_failed": 0
        })
        self.lock = threading.Lock()
    
    def profile_decision(self, ai_name: str):
        """Context manager for profiling AI decision making."""
        return self.profiler.profile(
            f"ai_decision_{ai_name}",
            "ai_decision",
            ai_name=ai_name
        )
    
    def profile_goal_evaluation(self, ai_name: str, goal_name: str):
        """Context manager for profiling goal evaluation."""
        return self.profiler.profile(
            f"goal_eval_{ai_name}_{goal_name}",
            "goal_evaluation",
            ai_name=ai_name,
            goal_name=goal_name
        )
    
    def profile_action_execution(self, ai_name: str, action_name: str):
        """Context manager for profiling action execution."""
        return self.profiler.profile(
            f"action_exec_{ai_name}_{action_name}",
            "action_execution",
            ai_name=ai_name,
            action_name=action_name
        )
    
    def record_decision(self, ai_name: str, duration: float, goals_evaluated: int) -> None:
        """Record AI decision statistics."""
        with self.lock:
            stats = self.ai_stats[ai_name]
            stats["decision_count"] += 1
            stats["goal_evaluations"] += goals_evaluated
            stats["total_decision_time"] += duration
            stats["average_decision_time"] = (
                stats["total_decision_time"] / stats["decision_count"]
            )
    
    def record_action_result(self, ai_name: str, action_name: str, success: bool) -> None:
        """Record action execution result."""
        with self.lock:
            stats = self.ai_stats[ai_name]
            stats["action_executions"] += 1
            
            if success:
                stats["actions_successful"] += 1
            else:
                stats["actions_failed"] += 1
            
            total_actions = stats["actions_successful"] + stats["actions_failed"]
            stats["action_success_rate"] = stats["actions_successful"] / total_actions
    
    def record_goal_satisfaction(self, ai_name: str, goal_satisfactions: Dict[str, float]) -> None:
        """Record goal satisfaction levels."""
        with self.lock:
            stats = self.ai_stats[ai_name]
            stats["goal_satisfaction_history"].append({
                "timestamp": time.time(),
                "satisfactions": goal_satisfactions.copy()
            })
            
            # Keep only recent history
            if len(stats["goal_satisfaction_history"]) > 100:
                stats["goal_satisfaction_history"] = stats["goal_satisfaction_history"][-50:]
    
    def get_ai_report(self, ai_name: Optional[str] = None) -> Dict[str, Any]:
        """Get AI performance report."""
        with self.lock:
            if ai_name:
                return {ai_name: dict(self.ai_stats[ai_name])}
            else:
                return {name: dict(stats) for name, stats in self.ai_stats.items()}
    
    def get_performance_insights(self, ai_name: str) -> Dict[str, Any]:
        """Get performance insights for specific AI."""
        with self.lock:
            if ai_name not in self.ai_stats:
                return {"error": f"No data for AI '{ai_name}'"}
            
            stats = self.ai_stats[ai_name]
            insights = {
                "efficiency": {
                    "decisions_per_second": 0.0,
                    "goals_per_decision": 0.0,
                    "decision_overhead": "normal"
                },
                "effectiveness": {
                    "action_success_rate": stats["action_success_rate"],
                    "goal_achievement_trend": "stable"
                },
                "recommendations": []
            }
            
            # Calculate efficiency metrics
            if stats["decision_count"] > 0:
                insights["efficiency"]["goals_per_decision"] = (
                    stats["goal_evaluations"] / stats["decision_count"]
                )
                
                if stats["total_decision_time"] > 0:
                    insights["efficiency"]["decisions_per_second"] = (
                        stats["decision_count"] / stats["total_decision_time"]
                    )
            
            # Analyze decision overhead
            avg_time = stats["average_decision_time"]
            if avg_time > 1.0:
                insights["efficiency"]["decision_overhead"] = "high"
                insights["recommendations"].append("Consider optimizing goal evaluation")
            elif avg_time > 0.5:
                insights["efficiency"]["decision_overhead"] = "moderate"
            
            # Analyze goal satisfaction trends
            history = stats["goal_satisfaction_history"]
            if len(history) >= 3:
                recent = history[-3:]
                # Simple trend analysis
                trend_sum = 0
                for i in range(1, len(recent)):
                    prev_avg = sum(recent[i-1]["satisfactions"].values()) / len(recent[i-1]["satisfactions"])
                    curr_avg = sum(recent[i]["satisfactions"].values()) / len(recent[i]["satisfactions"])
                    trend_sum += curr_avg - prev_avg
                
                if trend_sum > 0.1:
                    insights["effectiveness"]["goal_achievement_trend"] = "improving"
                elif trend_sum < -0.1:
                    insights["effectiveness"]["goal_achievement_trend"] = "declining"
                    insights["recommendations"].append("Review goal priorities and action effectiveness")
            
            # Performance recommendations
            if stats["action_success_rate"] < 0.7:
                insights["recommendations"].append("Review action preconditions and effects")
            
            if insights["efficiency"]["goals_per_decision"] > 10:
                insights["recommendations"].append("Consider reducing number of goals or adding goal filtering")
            
            return insights


# Global profiler instance
_global_profiler = PerformanceProfiler()
_ai_profiler = AIFamiliarProfiler(_global_profiler)


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return _global_profiler


def get_ai_profiler() -> AIFamiliarProfiler:
    """Get the AI profiler instance."""
    return _ai_profiler


def profile(name: str, category: str = "general", **metadata):
    """Convenience function for profiling code blocks."""
    return _global_profiler.profile(name, category, **metadata)


def profile_function(category: str = "function"):
    """Convenience decorator for profiling functions."""
    return _global_profiler.profile_function(category)


def start_system_monitoring(interval: float = 1.0) -> None:
    """Start global system monitoring."""
    _global_profiler.start_monitoring(interval)


def stop_system_monitoring() -> None:
    """Stop global system monitoring."""
    _global_profiler.stop_monitoring()


def get_performance_report(category: Optional[str] = None) -> Dict[str, Any]:
    """Get global performance report."""
    return _global_profiler.get_report(category)


def clear_profiling_data() -> None:
    """Clear all profiling data."""
    _global_profiler.clear_samples()