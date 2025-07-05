# Grimoire Programming Language
# Copyright (C) 2025 Sean Miner
#
# This file is part of Grimoire.
#
# Grimoire is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Grimoire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Anomaly Detection Mixins

Provides mixins for automatic anomaly detection during entity processing.
These mixins can be added to familiars to enable proactive anomaly monitoring.
"""

from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
import threading
import time

from .base import BaseAnomaly, AnomalyReport
from .registry import anomaly_registry


class AnomalyDetectorMixin:
    """
    Mixin that provides automatic anomaly detection capabilities to familiars.
    
    This mixin should be added to familiar classes to enable proactive
    anomaly monitoring during normal entity processing operations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Anomaly detection state
        self.assigned_anomalies: List[BaseAnomaly] = []
        self.anomaly_watch_list: Set[str] = set()  # anomaly IDs to monitor
        self.detection_cache: Dict[str, Dict[str, Any]] = {}  # anomaly_id -> cached data
        self.last_scan_time: float = 0.0
        self.scan_interval: float = 1.0  # seconds between scans
        self.detection_enabled: bool = True
        
        # Performance optimization
        self.batch_size: int = 10  # Process anomalies in batches
        self.cache_ttl: float = 5.0  # Cache results for 5 seconds
        
        # Detection statistics
        self.detection_stats = {
            "total_scans": 0,
            "total_detections": 0,
            "anomalies_detected": {},
            "scan_times": [],
            "last_detection": None
        }
        
        # Thread safety
        self._anomaly_lock = threading.RLock()
        
        # Initialize anomaly output socket for reporting
        if hasattr(self, 'add_socket'):
            self.add_socket("anomaly_output", data_type="anomaly_report", direction="output")
    
    def add_anomaly_watch(self, anomaly: BaseAnomaly) -> None:
        """
        Add an anomaly to the watch list for automatic detection.
        
        Args:
            anomaly: The anomaly to monitor
        """
        with self._anomaly_lock:
            if anomaly not in self.assigned_anomalies:
                self.assigned_anomalies.append(anomaly)
                self.anomaly_watch_list.add(anomaly.anomaly_id)
                
                # Initialize cache entry
                self.detection_cache[anomaly.anomaly_id] = {
                    "last_check": 0.0,
                    "last_result": False,
                    "check_count": 0
                }
                
                # Log activity if available
                if hasattr(self, 'log_activity'):
                    self.log_activity("anomaly", f"Added anomaly watch: {anomaly.name}", 
                                    {"anomaly_id": anomaly.anomaly_id, "severity": anomaly.severity})
    
    def remove_anomaly_watch(self, anomaly_id: str) -> bool:
        """
        Remove an anomaly from the watch list.
        
        Args:
            anomaly_id: ID of the anomaly to remove
            
        Returns:
            True if anomaly was removed, False if not found
        """
        with self._anomaly_lock:
            if anomaly_id in self.anomaly_watch_list:
                self.anomaly_watch_list.remove(anomaly_id)
                
                # Remove from assigned anomalies
                self.assigned_anomalies = [a for a in self.assigned_anomalies if a.anomaly_id != anomaly_id]
                
                # Clear cache
                if anomaly_id in self.detection_cache:
                    del self.detection_cache[anomaly_id]
                
                if hasattr(self, 'log_activity'):
                    self.log_activity("anomaly", f"Removed anomaly watch: {anomaly_id}", {})
                
                return True
            return False
    
    def scan_for_anomalies(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> List[AnomalyReport]:
        """
        Scan for anomalies in the given entity and world state.
        
        Args:
            entity_state: Current state of the entity being monitored
            world_state: Current world state context
            
        Returns:
            List of anomaly reports for detected anomalies
        """
        if not self.detection_enabled:
            return []
        
        current_time = time.time()
        
        # Check if enough time has passed since last scan
        if current_time - self.last_scan_time < self.scan_interval:
            return []
        
        with self._anomaly_lock:
            self.last_scan_time = current_time
            self.detection_stats["total_scans"] += 1
            
            detected_reports = []
            scan_start = time.time()
            
            # Process anomalies in batches for performance
            for i in range(0, len(self.assigned_anomalies), self.batch_size):
                batch = self.assigned_anomalies[i:i + self.batch_size]
                
                for anomaly in batch:
                    try:
                        # Check cache first
                        cache_entry = self.detection_cache.get(anomaly.anomaly_id, {})
                        last_check = cache_entry.get("last_check", 0.0)
                        
                        # Use cached result if within TTL
                        if current_time - last_check < self.cache_ttl:
                            if cache_entry.get("last_result", False):
                                # Create report from cached detection
                                report = self._create_anomaly_report(anomaly, entity_state, world_state)
                                detected_reports.append(report)
                            continue
                        
                        # Perform actual detection
                        is_detected = anomaly.detect(entity_state, world_state)
                        
                        # Update cache
                        self.detection_cache[anomaly.anomaly_id] = {
                            "last_check": current_time,
                            "last_result": is_detected,
                            "check_count": cache_entry.get("check_count", 0) + 1
                        }
                        
                        if is_detected:
                            report = self._create_anomaly_report(anomaly, entity_state, world_state)
                            detected_reports.append(report)
                            
                            # Update statistics
                            self.detection_stats["total_detections"] += 1
                            anomaly_name = anomaly.name
                            self.detection_stats["anomalies_detected"][anomaly_name] = \
                                self.detection_stats["anomalies_detected"].get(anomaly_name, 0) + 1
                            self.detection_stats["last_detection"] = current_time
                            
                            # Log detection
                            if hasattr(self, 'log_activity'):
                                self.log_activity("anomaly", f"Anomaly detected: {anomaly.name}", 
                                                {"severity": anomaly.severity, "entity_state": entity_state})
                    
                    except Exception as e:
                        # Log error but don't break the scan
                        if hasattr(self, 'log_activity'):
                            self.log_activity("anomaly", f"Error detecting anomaly {anomaly.name}: {str(e)}", 
                                            {"error": str(e)})
            
            # Record scan time
            scan_duration = time.time() - scan_start
            self.detection_stats["scan_times"].append(scan_duration)
            
            # Keep only last 100 scan times for performance
            if len(self.detection_stats["scan_times"]) > 100:
                self.detection_stats["scan_times"] = self.detection_stats["scan_times"][-100:]
            
            # Send reports through socket if available
            if detected_reports and hasattr(self, 'send_to_socket'):
                for report in detected_reports:
                    self.send_to_socket("anomaly_output", report)
            
            return detected_reports
    
    def _create_anomaly_report(self, anomaly: BaseAnomaly, entity_state: Dict[str, Any], 
                              world_state: Dict[str, Any]) -> AnomalyReport:
        """Create an anomaly report for a detected anomaly."""
        return AnomalyReport(
            anomaly_id=anomaly.anomaly_id,
            anomaly_name=anomaly.name,
            severity=anomaly.severity,
            detection_time=time.time(),
            entity_state=entity_state.copy(),
            world_state=world_state.copy(),
            detector_name=getattr(self, 'name', 'unknown'),
            escalation_needed=anomaly.should_escalate(),
            metadata=anomaly.get_metadata()
        )
    
    def auto_scan_during_update(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> None:
        """
        Automatically scan for anomalies during the familiar's autonomous update.
        
        This method should be called from the familiar's autonomous_update method
        to enable automatic anomaly detection during normal processing.
        
        Args:
            entity_state: Current state of the entity being managed
            world_state: Current world state context
        """
        if not self.assigned_anomalies:
            return
        
        detected_reports = self.scan_for_anomalies(entity_state, world_state)
        
        # Handle escalations
        for report in detected_reports:
            if report.escalation_needed:
                self.escalate_anomaly_report(report)
    
    def escalate_anomaly_report(self, report: AnomalyReport) -> None:
        """
        Escalate an anomaly report to higher-level agents.
        
        Args:
            report: The anomaly report to escalate
        """
        escalation_data = {
            "type": "anomaly_escalation",
            "report": report,
            "escalated_by": getattr(self, 'name', 'unknown'),
            "escalation_time": time.time(),
            "familiar_type": getattr(self, 'familiar_type', 'unknown')
        }
        
        # Send to escalation socket if available
        if hasattr(self, 'send_to_socket'):
            try:
                self.send_to_socket("escalation_output", escalation_data)
            except Exception:
                # Fallback: try generic anomaly output
                try:
                    self.send_to_socket("anomaly_output", escalation_data)
                except Exception:
                    pass
        
        # Log escalation
        if hasattr(self, 'log_activity'):
            self.log_activity("anomaly", f"Escalated anomaly: {report.anomaly_name}", 
                            {"severity": report.severity, "escalation_time": escalation_data["escalation_time"]})
        
        # Report to spirit if available
        if hasattr(self, 'spirit_ref') and self.spirit_ref:
            try:
                self.spirit_ref.handle_anomaly_escalation(report)
            except AttributeError:
                pass  # Spirit doesn't have anomaly handling
    
    def set_detection_interval(self, interval: float) -> None:
        """
        Set the interval between anomaly scans.
        
        Args:
            interval: Time in seconds between scans
        """
        with self._anomaly_lock:
            self.scan_interval = max(0.1, interval)  # Minimum 100ms
    
    def enable_detection(self) -> None:
        """Enable automatic anomaly detection."""
        with self._anomaly_lock:
            self.detection_enabled = True
            if hasattr(self, 'log_activity'):
                self.log_activity("anomaly", "Anomaly detection enabled", {})
    
    def disable_detection(self) -> None:
        """Disable automatic anomaly detection."""
        with self._anomaly_lock:
            self.detection_enabled = False
            if hasattr(self, 'log_activity'):
                self.log_activity("anomaly", "Anomaly detection disabled", {})
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about anomaly detection performance.
        
        Returns:
            Dictionary with detection statistics
        """
        with self._anomaly_lock:
            stats = self.detection_stats.copy()
            
            # Calculate average scan time
            if stats["scan_times"]:
                stats["avg_scan_time"] = sum(stats["scan_times"]) / len(stats["scan_times"])
                stats["max_scan_time"] = max(stats["scan_times"])
                stats["min_scan_time"] = min(stats["scan_times"])
            else:
                stats["avg_scan_time"] = 0.0
                stats["max_scan_time"] = 0.0
                stats["min_scan_time"] = 0.0
            
            # Add configuration info
            stats["config"] = {
                "detection_enabled": self.detection_enabled,
                "scan_interval": self.scan_interval,
                "batch_size": self.batch_size,
                "cache_ttl": self.cache_ttl,
                "watched_anomalies": len(self.assigned_anomalies)
            }
            
            return stats
    
    def clear_detection_cache(self) -> None:
        """Clear the anomaly detection cache."""
        with self._anomaly_lock:
            self.detection_cache.clear()
            if hasattr(self, 'log_activity'):
                self.log_activity("anomaly", "Detection cache cleared", {})
    
    def optimize_detection_performance(self) -> None:
        """
        Optimize detection performance based on recent scan times.
        
        This method automatically adjusts batch size and cache TTL based on
        recent performance metrics.
        """
        with self._anomaly_lock:
            if len(self.detection_stats["scan_times"]) < 10:
                return  # Not enough data
            
            avg_scan_time = sum(self.detection_stats["scan_times"][-10:]) / 10
            
            # Adjust batch size based on scan time
            if avg_scan_time > 0.1:  # 100ms
                # Scans are taking too long, reduce batch size
                self.batch_size = max(1, self.batch_size - 1)
            elif avg_scan_time < 0.01:  # 10ms
                # Scans are fast, increase batch size
                self.batch_size = min(50, self.batch_size + 1)
            
            # Adjust cache TTL based on detection frequency
            if self.detection_stats["total_detections"] > 0:
                detection_rate = self.detection_stats["total_detections"] / self.detection_stats["total_scans"]
                if detection_rate > 0.1:  # High detection rate
                    self.cache_ttl = max(1.0, self.cache_ttl - 0.5)
                elif detection_rate < 0.01:  # Low detection rate
                    self.cache_ttl = min(10.0, self.cache_ttl + 0.5)


class ContextAwareAnomalyMixin:
    """
    Mixin that provides context-aware anomaly management.
    
    This mixin automatically activates/deactivates anomalies based on
    current context such as game mode, time, system load, etc.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Context management
        self.current_context: Dict[str, Any] = {}
        self.context_rules: List[Callable] = []
        self.active_anomaly_sets: Set[str] = set()
        
        # Context update tracking
        self.last_context_update: float = 0.0
        self.context_update_interval: float = 5.0  # seconds
        
        # Thread safety
        self._context_lock = threading.RLock()
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """
        Update the current context and refresh active anomalies.
        
        Args:
            new_context: New context information
        """
        with self._context_lock:
            self.current_context.update(new_context)
            self.last_context_update = time.time()
            
            # Refresh active anomalies based on new context
            self._refresh_active_anomalies()
            
            if hasattr(self, 'log_activity'):
                self.log_activity("context", "Context updated", {"context": new_context})
    
    def add_context_rule(self, rule_func: Callable[[Dict[str, Any]], List[str]]) -> None:
        """
        Add a context rule that determines which anomaly sets should be active.
        
        Args:
            rule_func: Function that takes context and returns list of anomaly set names
        """
        with self._context_lock:
            self.context_rules.append(rule_func)
    
    def _refresh_active_anomalies(self) -> None:
        """Refresh active anomalies based on current context."""
        if not hasattr(self, 'assigned_anomalies'):
            return
        
        # Determine which anomaly sets should be active
        should_be_active = set()
        
        for rule in self.context_rules:
            try:
                active_sets = rule(self.current_context)
                should_be_active.update(active_sets)
            except Exception as e:
                if hasattr(self, 'log_activity'):
                    self.log_activity("context", f"Error in context rule: {str(e)}", {"error": str(e)})
        
        # Activate/deactivate anomaly sets as needed
        for set_name in should_be_active:
            if set_name not in self.active_anomaly_sets:
                self._activate_anomaly_set(set_name)
        
        for set_name in list(self.active_anomaly_sets):
            if set_name not in should_be_active:
                self._deactivate_anomaly_set(set_name)
    
    def _activate_anomaly_set(self, set_name: str) -> None:
        """Activate an anomaly set."""
        anomalies = anomaly_registry.get_anomaly_set(set_name)
        
        for anomaly in anomalies:
            if hasattr(self, 'add_anomaly_watch'):
                self.add_anomaly_watch(anomaly)
        
        self.active_anomaly_sets.add(set_name)
        
        if hasattr(self, 'log_activity'):
            self.log_activity("context", f"Activated anomaly set: {set_name}", 
                            {"anomaly_count": len(anomalies)})
    
    def _deactivate_anomaly_set(self, set_name: str) -> None:
        """Deactivate an anomaly set."""
        anomalies = anomaly_registry.get_anomaly_set(set_name)
        
        for anomaly in anomalies:
            if hasattr(self, 'remove_anomaly_watch'):
                self.remove_anomaly_watch(anomaly.anomaly_id)
        
        self.active_anomaly_sets.discard(set_name)
        
        if hasattr(self, 'log_activity'):
            self.log_activity("context", f"Deactivated anomaly set: {set_name}", 
                            {"anomaly_count": len(anomalies)})
    
    def auto_update_context(self) -> None:
        """
        Automatically update context during familiar updates.
        
        This method should be called from the familiar's autonomous_update method.
        """
        current_time = time.time()
        
        if current_time - self.last_context_update < self.context_update_interval:
            return
        
        # Gather context information
        context_updates = {}
        
        # Time-based context
        context_updates["current_time"] = current_time
        context_updates["hour_of_day"] = int((current_time % 86400) / 3600)
        
        # System load context (simplified)
        if hasattr(self, 'detection_stats'):
            recent_scans = self.detection_stats.get("scan_times", [])
            if recent_scans:
                context_updates["system_load"] = "high" if sum(recent_scans[-5:]) / 5 > 0.05 else "normal"
        
        # Game state context
        if hasattr(self, 'charge') and self.charge:
            if hasattr(self.charge, 'properties'):
                context_updates["entity_health"] = self.charge.properties.get("health", 100)
                context_updates["entity_active"] = self.charge.properties.get("active", True)
        
        self.update_context(context_updates)


# Pre-built context rules for common scenarios
def game_mode_context_rule(context: Dict[str, Any]) -> List[str]:
    """Context rule for game mode-based anomaly activation."""
    mode = context.get("game_mode", "unknown")
    
    if mode == "combat":
        return ["combat_anomalies", "critical_anomalies"]
    elif mode == "exploration":
        return ["exploration_anomalies", "performance_anomalies"]
    elif mode == "development":
        return ["development_anomalies"]
    else:
        return ["basic_anomalies"]


def time_based_context_rule(context: Dict[str, Any]) -> List[str]:
    """Context rule for time-based anomaly activation."""
    hour = context.get("hour_of_day", 12)
    
    if 22 <= hour or hour <= 6:  # Night time
        return ["night_anomalies", "security_anomalies"]
    else:  # Day time
        return ["day_anomalies", "performance_anomalies"]


def load_based_context_rule(context: Dict[str, Any]) -> List[str]:
    """Context rule for system load-based anomaly activation."""
    load = context.get("system_load", "normal")
    
    if load == "high":
        return ["critical_anomalies"]  # Only critical anomalies during high load
    else:
        return ["basic_anomalies", "performance_anomalies"]


def business_period_context_rule(context: Dict[str, Any]) -> List[str]:
    """Context rule for business period-based anomaly activation."""
    period = context.get("business_period", "normal")
    
    if period in ["month_end", "quarter_end", "year_end"]:
        return ["audit_anomalies", "compliance_anomalies", "critical_anomalies"]
    elif period == "budget_review":
        return ["financial_anomalies", "resource_anomalies"]
    else:
        return ["basic_anomalies", "operational_anomalies"]