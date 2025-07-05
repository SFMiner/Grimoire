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
Enhanced Familiar Classes with Anomaly Detection

This module provides enhanced familiar classes that integrate automatic anomaly
detection capabilities for proactive monitoring during entity processing.
"""

from typing import Dict, Any, Optional, List
import time

from ..interpreter import GrimoireFamiliar
from ..anomalies.mixins import AnomalyDetectorMixin, ContextAwareAnomalyMixin
from ..anomalies.libraries import initialize_game_anomaly_library, initialize_business_anomaly_library
from ..familiars.entity_familiar import EntityFamiliar
from ..familiars.ai_familiar import AIFamiliar


class AnomalyDetectorFamiliar(AnomalyDetectorMixin, ContextAwareAnomalyMixin, GrimoireFamiliar):
    """
    Enhanced familiar with automatic anomaly detection capabilities.
    
    This familiar automatically scans for anomalies during processing and
    can escalate reports through the socket system to spirits and archons.
    """
    
    def __init__(self, name: str, familiar_type: str = "AnomalyDetector", **kwargs):
        super().__init__(name, familiar_type, {}, **kwargs)
        
        # Initialize anomaly-specific sockets
        self.add_socket("escalation_output", data_type="escalation_report", direction="output")
        self.add_socket("context_input", data_type="context_update", direction="input")
        
        # Set up context rules
        from ..anomalies.mixins import game_mode_context_rule, time_based_context_rule
        self.add_context_rule(game_mode_context_rule)
        self.add_context_rule(time_based_context_rule)
        
        # Initialize with basic anomaly library
        if not hasattr(self, '_anomaly_library_initialized'):
            initialize_game_anomaly_library()
            self._anomaly_library_initialized = True
    
    def autonomous_update(self):
        """Enhanced autonomous update with anomaly detection."""
        # Standard familiar update
        super().autonomous_update()
        
        # Auto-update context based on current state
        self.auto_update_context()
        
        # Check for context updates from socket
        context_update = self.receive_from_socket("context_input")
        if context_update:
            self.update_context(context_update)
        
        # Perform anomaly scanning if we have a charge
        if self.charge and hasattr(self.charge, 'properties'):
            entity_state = self.charge.properties.copy()
            world_state = self._gather_world_state()
            
            # Automatic anomaly scanning
            self.auto_scan_during_update(entity_state, world_state)
    
    def _gather_world_state(self) -> Dict[str, Any]:
        """Gather world state information for anomaly detection."""
        world_state = {
            "current_time": time.time(),
            "system_load": "normal",  # Simplified
            "game_mode": "normal",
        }
        
        # Add performance metrics if available
        if hasattr(self, 'detection_stats'):
            recent_scans = self.detection_stats.get("scan_times", [])
            if recent_scans:
                avg_scan_time = sum(recent_scans[-5:]) / len(recent_scans[-5:])
                world_state["avg_scan_time"] = avg_scan_time
                world_state["system_load"] = "high" if avg_scan_time > 0.05 else "normal"
        
        return world_state
    
    def handle_anomaly_escalation(self, report):
        """Handle escalation from other familiars."""
        if hasattr(self, 'spirit_ref') and self.spirit_ref:
            # Forward to spirit
            try:
                self.spirit_ref.handle_anomaly_escalation(report)
            except AttributeError:
                # Spirit doesn't have anomaly handling, log it
                self.log_activity("anomaly", "Spirit cannot handle escalation", 
                                {"report": report.anomaly_name})


class MonitoringFamiliar(AnomalyDetectorFamiliar, EntityFamiliar):
    """
    Specialized familiar for monitoring entities with anomaly detection.
    
    Combines entity management with proactive anomaly monitoring.
    """
    
    def __init__(self, name: str, entity_type: str = "Generic", **kwargs):
        super().__init__(name, "MonitoringFamiliar", **kwargs)
        self.entity_type = entity_type
        
        # Set up monitoring-specific configuration
        self.set_detection_interval(0.5)  # Check every 500ms
        
        # Initialize appropriate anomaly library based on entity type
        if entity_type.lower() in ["player", "npc", "monster"]:
            initialize_game_anomaly_library()
        else:
            initialize_business_anomaly_library()
    
    def autonomous_update(self):
        """Enhanced monitoring with entity-specific anomaly detection."""
        super().autonomous_update()
        
        # Optimize detection performance based on load
        self.optimize_detection_performance()


class GameEntityFamiliar(AnomalyDetectorFamiliar, EntityFamiliar):
    """
    Game entity familiar with automatic anomaly detection.
    
    Specialized for game entities like players, NPCs, and monsters.
    """
    
    def __init__(self, name: str, entity_data: Dict[str, Any], **kwargs):
        super().__init__(name, "GameEntityFamiliar", **kwargs)
        
        # Initialize with game-specific anomaly library
        initialize_game_anomaly_library()
        
        # Set up entity-specific anomaly watches
        self._setup_game_anomaly_watches(entity_data)
        
        # Configure context for game mode
        self.update_context({
            "game_mode": "normal",
            "entity_type": entity_data.get("type", "generic")
        })
    
    def _setup_game_anomaly_watches(self, entity_data: Dict[str, Any]):
        """Set up anomaly watches based on entity type."""
        from ..anomalies.registry import anomaly_registry
        
        entity_type = entity_data.get("type", "generic").lower()
        
        if entity_type == "player":
            # Add player-specific anomalies
            health_anomaly = anomaly_registry.get_anomaly("health_critical")
            if health_anomaly:
                self.add_anomaly_watch(health_anomaly)
            
            behavior_anomaly = anomaly_registry.get_anomaly("player_behavior")
            if behavior_anomaly:
                self.add_anomaly_watch(behavior_anomaly)
        
        elif entity_type in ["npc", "monster"]:
            # Add combat-related anomalies
            combat_anomaly = anomaly_registry.get_anomaly("combat_overwhelm")
            if combat_anomaly:
                self.add_anomaly_watch(combat_anomaly)
        
        # Add performance anomaly for all game entities
        perf_anomaly = anomaly_registry.get_anomaly("performance_degradation")
        if perf_anomaly:
            self.add_anomaly_watch(perf_anomaly)


class BusinessEntityFamiliar(AnomalyDetectorFamiliar, EntityFamiliar):
    """
    Business entity familiar with automatic anomaly detection.
    
    Specialized for business entities like users, transactions, and systems.
    """
    
    def __init__(self, name: str, entity_data: Dict[str, Any], **kwargs):
        super().__init__(name, "BusinessEntityFamiliar", **kwargs)
        
        # Initialize with business-specific anomaly library
        initialize_business_anomaly_library()
        
        # Set up entity-specific anomaly watches
        self._setup_business_anomaly_watches(entity_data)
        
        # Configure context for business mode
        self.update_context({
            "business_mode": "normal",
            "entity_type": entity_data.get("type", "generic")
        })
    
    def _setup_business_anomaly_watches(self, entity_data: Dict[str, Any]):
        """Set up anomaly watches based on business entity type."""
        from ..anomalies.registry import anomaly_registry
        
        entity_type = entity_data.get("type", "generic").lower()
        
        if entity_type == "user":
            # Add user behavior anomaly
            behavior_anomaly = anomaly_registry.get_anomaly("user_behavior")
            if behavior_anomaly:
                self.add_anomaly_watch(behavior_anomaly)
        
        elif entity_type == "transaction":
            # Add transaction volume anomaly
            volume_anomaly = anomaly_registry.get_anomaly("transaction_volume")
            if volume_anomaly:
                self.add_anomaly_watch(volume_anomaly)
        
        elif entity_type == "system":
            # Add system load anomaly
            load_anomaly = anomaly_registry.get_anomaly("system_load")
            if load_anomaly:
                self.add_anomaly_watch(load_anomaly)
        
        # Add security anomaly for all business entities
        security_anomaly = anomaly_registry.get_anomaly("security_breach")
        if security_anomaly:
            self.add_anomaly_watch(security_anomaly)


class AIFamiliarWithAnomalyDetection(AnomalyDetectorFamiliar, AIFamiliar):
    """
    AI familiar enhanced with anomaly detection capabilities.
    
    Combines AI decision-making with proactive anomaly monitoring.
    """
    
    def __init__(self, name: str, ai_type: str = "decision_maker", **kwargs):
        super().__init__(name, f"AI_{ai_type}", **kwargs)
        
        # Initialize both libraries for comprehensive coverage
        initialize_game_anomaly_library()
        initialize_business_anomaly_library()
        
        # Set up AI-specific anomaly detection
        self.set_detection_interval(1.0)  # Check every second for AI
        
        # Add context rule for AI load
        def ai_load_context_rule(context):
            ai_load = context.get("ai_decision_time", 0.0)
            if ai_load > 0.1:  # 100ms decision time
                return ["performance_anomalies", "critical_anomalies"]
            return ["basic_anomalies"]
        
        self.add_context_rule(ai_load_context_rule)
    
    def autonomous_update(self):
        """Enhanced AI update with anomaly detection."""
        start_time = time.time()
        
        # Standard AI update
        super().autonomous_update()
        
        # Track AI decision time for context
        decision_time = time.time() - start_time
        self.update_context({"ai_decision_time": decision_time})


# =============================================================================
# SPIRIT CLASSES WITH ANOMALY HANDLING
# =============================================================================

class AnomalyHandlingSpirit:
    """
    Mixin for spirits to handle anomaly escalations from familiars.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Anomaly handling state
        self.anomaly_reports: List[Any] = []
        self.escalation_threshold = 3  # Escalate to archon after 3 reports
        
        # Add anomaly input socket
        if hasattr(self, 'add_socket'):
            self.add_socket("anomaly_input", data_type="anomaly_report", direction="input")
            self.add_socket("archon_escalation", data_type="escalation_report", direction="output")
    
    def handle_anomaly_escalation(self, report):
        """Handle anomaly escalation from familiar."""
        self.anomaly_reports.append(report)
        
        # Log the escalation
        if hasattr(self, 'log_activity'):
            self.log_activity("anomaly", f"Received escalation: {report.anomaly_name}",
                            {"severity": report.severity, "detector": report.detector_name})
        
        # Check if we should escalate to archon
        if len(self.anomaly_reports) >= self.escalation_threshold:
            self.escalate_to_archon()
    
    def escalate_to_archon(self):
        """Escalate accumulated anomaly reports to archon."""
        if not self.anomaly_reports:
            return
        
        escalation_data = {
            "type": "spirit_escalation",
            "spirit_name": getattr(self, 'name', 'unknown'),
            "report_count": len(self.anomaly_reports),
            "reports": self.anomaly_reports,
            "escalation_time": time.time()
        }
        
        # Send to archon through socket
        if hasattr(self, 'send_to_socket'):
            try:
                self.send_to_socket("archon_escalation", escalation_data)
            except Exception as e:
                if hasattr(self, 'log_activity'):
                    self.log_activity("anomaly", f"Failed to escalate to archon: {str(e)}", {})
        
        # Clear reports after escalation
        self.anomaly_reports.clear()
        
        if hasattr(self, 'log_activity'):
            self.log_activity("anomaly", "Escalated to archon", {"report_count": escalation_data["report_count"]})


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_monitoring_familiar(name: str, entity_type: str = "Generic", 
                              entity_data: Optional[Dict[str, Any]] = None) -> MonitoringFamiliar:
    """
    Factory function to create a monitoring familiar with appropriate anomaly detection.
    
    Args:
        name: Name for the familiar
        entity_type: Type of entity to monitor
        entity_data: Optional entity data for configuration
        
    Returns:
        Configured monitoring familiar
    """
    entity_data = entity_data or {}
    familiar = MonitoringFamiliar(name, entity_type)
    
    # Configure based on entity type
    if entity_type.lower() in ["player", "npc", "monster"]:
        familiar.update_context({"game_mode": "normal", "entity_type": entity_type})
    else:
        familiar.update_context({"business_mode": "normal", "entity_type": entity_type})
    
    return familiar


def create_game_entity_familiar(name: str, entity_data: Dict[str, Any]) -> GameEntityFamiliar:
    """
    Factory function to create a game entity familiar with anomaly detection.
    
    Args:
        name: Name for the familiar
        entity_data: Entity data including type and properties
        
    Returns:
        Configured game entity familiar
    """
    return GameEntityFamiliar(name, entity_data)


def create_business_entity_familiar(name: str, entity_data: Dict[str, Any]) -> BusinessEntityFamiliar:
    """
    Factory function to create a business entity familiar with anomaly detection.
    
    Args:
        name: Name for the familiar
        entity_data: Entity data including type and properties
        
    Returns:
        Configured business entity familiar
    """
    return BusinessEntityFamiliar(name, entity_data)


def create_ai_familiar_with_anomaly_detection(name: str, ai_type: str = "decision_maker") -> AIFamiliarWithAnomalyDetection:
    """
    Factory function to create an AI familiar with anomaly detection.
    
    Args:
        name: Name for the familiar
        ai_type: Type of AI familiar
        
    Returns:
        Configured AI familiar with anomaly detection
    """
    return AIFamiliarWithAnomalyDetection(name, ai_type)


# Export all enhanced familiar classes
__all__ = [
    "AnomalyDetectorFamiliar",
    "MonitoringFamiliar",
    "GameEntityFamiliar",
    "BusinessEntityFamiliar",
    "AIFamiliarWithAnomalyDetection",
    "AnomalyHandlingSpirit",
    "create_monitoring_familiar",
    "create_game_entity_familiar",
    "create_business_entity_familiar",
    "create_ai_familiar_with_anomaly_detection"
]