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
Pre-built Anomaly Libraries

This module provides pre-built anomaly libraries for common game and business
scenarios, ready to be deployed in production environments.
"""

from typing import Dict, Any, List
from .base import BaseAnomaly, CompositeAnomaly, AdaptiveAnomaly
from .registry import anomaly_registry


# =============================================================================
# GAME ANOMALY LIBRARY
# =============================================================================

class HealthCriticalAnomaly(BaseAnomaly):
    """Detects critically low health conditions."""
    
    def __init__(self, threshold: float = 0.1):
        super().__init__(
            name="health_critical",
            severity=0.9,
            description=f"Health below {threshold * 100}% threshold"
        )
        self.threshold = threshold
        self.add_tag("health")
        self.add_tag("critical")
        self.add_tag("game")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        health = entity_state.get("health", 100)
        max_health = entity_state.get("max_health", 100)
        
        if max_health <= 0:
            return False
        
        health_ratio = health / max_health
        return health_ratio <= self.threshold


class ResourceDepletionAnomaly(BaseAnomaly):
    """Detects resource depletion scenarios."""
    
    def __init__(self, resource_type: str = "mana", threshold: float = 0.05):
        super().__init__(
            name=f"{resource_type}_depletion",
            severity=0.7,
            description=f"{resource_type} below {threshold * 100}% threshold"
        )
        self.resource_type = resource_type
        self.threshold = threshold
        self.add_tag("resource")
        self.add_tag("depletion")
        self.add_tag("game")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        current = entity_state.get(self.resource_type, 100)
        maximum = entity_state.get(f"max_{self.resource_type}", 100)
        
        if maximum <= 0:
            return False
        
        resource_ratio = current / maximum
        return resource_ratio <= self.threshold


class CombatOverwhelmAnomaly(BaseAnomaly):
    """Detects when entity is overwhelmed in combat."""
    
    def __init__(self, enemy_ratio_threshold: float = 3.0):
        super().__init__(
            name="combat_overwhelm",
            severity=0.8,
            description=f"Facing {enemy_ratio_threshold}x more enemies than allies"
        )
        self.enemy_ratio_threshold = enemy_ratio_threshold
        self.add_tag("combat")
        self.add_tag("tactical")
        self.add_tag("game")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        enemies_nearby = world_state.get("enemies_nearby", 0)
        allies_nearby = world_state.get("allies_nearby", 1)  # Include self
        
        if allies_nearby == 0:
            return enemies_nearby > 0
        
        enemy_ratio = enemies_nearby / allies_nearby
        return enemy_ratio >= self.enemy_ratio_threshold


class PerformanceDegradationAnomaly(AdaptiveAnomaly):
    """Detects performance degradation in game systems."""
    
    def __init__(self):
        super().__init__(
            name="performance_degradation",
            properties=["fps", "frame_time", "memory_usage"],
            threshold_multiplier=2.5,
            min_samples=20,
            severity=0.6,
            description="Performance metrics deviating from baseline"
        )
        self.add_tag("performance")
        self.add_tag("system")
        self.add_tag("game")


class PlayerBehaviorAnomaly(AdaptiveAnomaly):
    """Detects unusual player behavior patterns."""
    
    def __init__(self):
        super().__init__(
            name="player_behavior",
            properties=["actions_per_minute", "movement_speed", "decision_time"],
            threshold_multiplier=3.0,
            min_samples=50,
            severity=0.5,
            description="Player behavior deviating from normal patterns"
        )
        self.add_tag("player")
        self.add_tag("behavior")
        self.add_tag("game")


class CoordinatedAttackAnomaly(CompositeAnomaly):
    """Detects coordinated attacks requiring multiple conditions."""
    
    def __init__(self):
        # Create sub-anomalies
        health_anomaly = HealthCriticalAnomaly(threshold=0.3)
        combat_anomaly = CombatOverwhelmAnomaly(enemy_ratio_threshold=2.0)
        resource_anomaly = ResourceDepletionAnomaly("mana", threshold=0.2)
        
        super().__init__(
            name="coordinated_attack",
            sub_anomalies=[health_anomaly, combat_anomaly, resource_anomaly],
            threshold=2,  # At least 2 of 3 conditions
            severity=0.95,
            description="Coordinated attack detected - multiple threat indicators"
        )
        self.add_tag("combat")
        self.add_tag("coordinated")
        self.add_tag("critical")
        self.add_tag("game")


# =============================================================================
# BUSINESS ANOMALY LIBRARY
# =============================================================================

class TransactionVolumeAnomaly(AdaptiveAnomaly):
    """Detects unusual transaction volume patterns."""
    
    def __init__(self):
        super().__init__(
            name="transaction_volume",
            properties=["transaction_count", "transaction_value", "unique_users"],
            threshold_multiplier=2.0,
            min_samples=100,
            severity=0.7,
            description="Transaction volume deviating from normal patterns"
        )
        self.add_tag("transaction")
        self.add_tag("volume")
        self.add_tag("business")


class UserBehaviorAnomaly(AdaptiveAnomaly):
    """Detects unusual user behavior in business applications."""
    
    def __init__(self):
        super().__init__(
            name="user_behavior",
            properties=["session_duration", "page_views", "click_rate"],
            threshold_multiplier=2.5,
            min_samples=30,
            severity=0.6,
            description="User behavior patterns deviating from baseline"
        )
        self.add_tag("user")
        self.add_tag("behavior")
        self.add_tag("business")


class SystemLoadAnomaly(BaseAnomaly):
    """Detects system overload conditions."""
    
    def __init__(self, cpu_threshold: float = 0.9, memory_threshold: float = 0.85):
        super().__init__(
            name="system_load",
            severity=0.8,
            description=f"System load above thresholds (CPU: {cpu_threshold * 100}%, Memory: {memory_threshold * 100}%)"
        )
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.add_tag("system")
        self.add_tag("load")
        self.add_tag("business")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        cpu_usage = world_state.get("cpu_usage", 0.0)
        memory_usage = world_state.get("memory_usage", 0.0)
        
        return cpu_usage >= self.cpu_threshold or memory_usage >= self.memory_threshold


class SecurityBreachAnomaly(BaseAnomaly):
    """Detects potential security breaches."""
    
    def __init__(self, failed_attempts_threshold: int = 5):
        super().__init__(
            name="security_breach",
            severity=0.95,
            description=f"Security breach indicators detected (failed attempts: {failed_attempts_threshold})"
        )
        self.failed_attempts_threshold = failed_attempts_threshold
        self.add_tag("security")
        self.add_tag("breach")
        self.add_tag("critical")
        self.add_tag("business")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        failed_logins = entity_state.get("failed_login_attempts", 0)
        suspicious_ips = world_state.get("suspicious_ip_count", 0)
        
        return failed_logins >= self.failed_attempts_threshold or suspicious_ips > 0


class DataQualityAnomaly(BaseAnomaly):
    """Detects data quality issues."""
    
    def __init__(self, null_threshold: float = 0.1, duplicate_threshold: float = 0.05):
        super().__init__(
            name="data_quality",
            severity=0.6,
            description=f"Data quality issues detected (null: {null_threshold * 100}%, duplicates: {duplicate_threshold * 100}%)"
        )
        self.null_threshold = null_threshold
        self.duplicate_threshold = duplicate_threshold
        self.add_tag("data")
        self.add_tag("quality")
        self.add_tag("business")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        null_ratio = entity_state.get("null_value_ratio", 0.0)
        duplicate_ratio = entity_state.get("duplicate_ratio", 0.0)
        
        return null_ratio >= self.null_threshold or duplicate_ratio >= self.duplicate_threshold


class ComplianceViolationAnomaly(CompositeAnomaly):
    """Detects compliance violations requiring multiple checks."""
    
    def __init__(self):
        # Create sub-anomalies for compliance checks
        class DataRetentionAnomaly(BaseAnomaly):
            def __init__(self):
                super().__init__(
                    name="data_retention_violation",
                    severity=0.8,
                    description="Data retention policy violation"
                )
                self.add_tag("compliance")
                self.add_tag("retention")
            
            def detect(self, entity_state, world_state):
                retention_days = entity_state.get("data_retention_days", 0)
                max_retention = world_state.get("max_retention_days", 365)
                return retention_days > max_retention
        
        class AccessControlAnomaly(BaseAnomaly):
            def __init__(self):
                super().__init__(
                    name="access_control_violation",
                    severity=0.9,
                    description="Access control policy violation"
                )
                self.add_tag("compliance")
                self.add_tag("access")
            
            def detect(self, entity_state, world_state):
                unauthorized_access = entity_state.get("unauthorized_access_attempts", 0)
                return unauthorized_access > 0
        
        data_retention_anomaly = DataRetentionAnomaly()
        access_control_anomaly = AccessControlAnomaly()
        
        super().__init__(
            name="compliance_violation",
            sub_anomalies=[data_retention_anomaly, access_control_anomaly],
            threshold=1,  # Any violation is critical
            severity=0.9,
            description="Compliance violation detected"
        )
        self.add_tag("compliance")
        self.add_tag("violation")
        self.add_tag("critical")
        self.add_tag("business")


# =============================================================================
# LIBRARY INITIALIZATION AND MANAGEMENT
# =============================================================================

def initialize_game_anomaly_library():
    """Initialize and register all game anomalies."""
    anomalies = [
        HealthCriticalAnomaly(),
        ResourceDepletionAnomaly("mana"),
        ResourceDepletionAnomaly("stamina"),
        CombatOverwhelmAnomaly(),
        PerformanceDegradationAnomaly(),
        PlayerBehaviorAnomaly(),
        CoordinatedAttackAnomaly()
    ]
    
    # Register all anomalies
    for anomaly in anomalies:
        anomaly_registry.register_anomaly(anomaly)
    
    # Create predefined sets
    anomaly_registry.create_anomaly_set("critical_anomalies", [
        "health_critical", "coordinated_attack"
    ])
    
    anomaly_registry.create_anomaly_set("combat_anomalies", [
        "health_critical", "combat_overwhelm", "mana_depletion", "coordinated_attack"
    ])
    
    anomaly_registry.create_anomaly_set("performance_anomalies", [
        "performance_degradation"
    ])
    
    anomaly_registry.create_anomaly_set("exploration_anomalies", [
        "health_critical", "stamina_depletion", "performance_degradation"
    ])
    
    anomaly_registry.create_anomaly_set("development_anomalies", [
        "performance_degradation", "player_behavior"
    ])
    
    return anomalies


def initialize_business_anomaly_library():
    """Initialize and register all business anomalies."""
    anomalies = [
        TransactionVolumeAnomaly(),
        UserBehaviorAnomaly(),
        SystemLoadAnomaly(),
        SecurityBreachAnomaly(),
        DataQualityAnomaly(),
        ComplianceViolationAnomaly()
    ]
    
    # Register all anomalies
    for anomaly in anomalies:
        anomaly_registry.register_anomaly(anomaly)
    
    # Create predefined sets
    anomaly_registry.create_anomaly_set("security_anomalies", [
        "security_breach", "compliance_violation"
    ])
    
    anomaly_registry.create_anomaly_set("operational_anomalies", [
        "system_load", "data_quality", "transaction_volume"
    ])
    
    anomaly_registry.create_anomaly_set("audit_anomalies", [
        "compliance_violation", "data_quality", "security_breach"
    ])
    
    anomaly_registry.create_anomaly_set("compliance_anomalies", [
        "compliance_violation", "data_quality"
    ])
    
    anomaly_registry.create_anomaly_set("financial_anomalies", [
        "transaction_volume", "user_behavior"
    ])
    
    anomaly_registry.create_anomaly_set("resource_anomalies", [
        "system_load", "transaction_volume"
    ])
    
    return anomalies


def initialize_all_anomaly_libraries():
    """Initialize both game and business anomaly libraries."""
    game_anomalies = initialize_game_anomaly_library()
    business_anomalies = initialize_business_anomaly_library()
    
    # Create universal sets
    anomaly_registry.create_anomaly_set("basic_anomalies", [
        "health_critical", "system_load", "data_quality"
    ])
    
    anomaly_registry.create_anomaly_set("night_anomalies", [
        "security_breach", "compliance_violation", "system_load"
    ])
    
    anomaly_registry.create_anomaly_set("day_anomalies", [
        "transaction_volume", "user_behavior", "performance_degradation"
    ])
    
    return game_anomalies + business_anomalies


def get_anomaly_library_stats():
    """Get statistics about loaded anomaly libraries."""
    stats = anomaly_registry.get_registry_stats()
    
    # Count by library type
    game_count = 0
    business_count = 0
    
    for anomaly_name in anomaly_registry.list_anomalies():
        anomaly = anomaly_registry.get_anomaly(anomaly_name)
        if anomaly and hasattr(anomaly, 'tags'):
            if "game" in anomaly.tags:
                game_count += 1
            if "business" in anomaly.tags:
                business_count += 1
    
    stats["libraries"] = {
        "game_anomalies": game_count,
        "business_anomalies": business_count,
        "total_libraries": 2
    }
    
    return stats


# Pre-built anomaly library exports
__all__ = [
    # Game anomalies
    "HealthCriticalAnomaly",
    "ResourceDepletionAnomaly", 
    "CombatOverwhelmAnomaly",
    "PerformanceDegradationAnomaly",
    "PlayerBehaviorAnomaly",
    "CoordinatedAttackAnomaly",
    
    # Business anomalies
    "TransactionVolumeAnomaly",
    "UserBehaviorAnomaly",
    "SystemLoadAnomaly",
    "SecurityBreachAnomaly",
    "DataQualityAnomaly",
    "ComplianceViolationAnomaly",
    
    # Library functions
    "initialize_game_anomaly_library",
    "initialize_business_anomaly_library",
    "initialize_all_anomaly_libraries",
    "get_anomaly_library_stats"
]