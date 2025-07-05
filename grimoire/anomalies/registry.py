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
Anomaly Registry System

Central registry for managing anomaly definitions, named sets, and context-aware
anomaly activation rules. Provides the foundation for organizing and deploying
anomalies across the Grimoire agent hierarchy.
"""

from typing import Dict, List, Set, Optional, Callable, Any
from datetime import datetime
import threading
import json

from .base import BaseAnomaly


class AnomalyRegistry:
    """
    Central registry for managing anomaly definitions and detection sets.
    
    The registry serves as the single source of truth for all anomaly definitions,
    organizes them into named sets for easy deployment, and manages context rules
    that determine which anomalies should be active in different situations.
    """
    
    def __init__(self):
        """Initialize the anomaly registry."""
        # Core storage
        self.anomalies: Dict[str, BaseAnomaly] = {}  # anomaly_id -> anomaly
        self.anomaly_sets: Dict[str, List[str]] = {}  # set_name -> [anomaly_ids]
        self.context_rules: List[Callable] = []  # functions for context-based activation
        
        # Indexing for fast lookups
        self.anomalies_by_name: Dict[str, str] = {}  # name -> anomaly_id
        self.anomalies_by_tag: Dict[str, Set[str]] = {}  # tag -> {anomaly_ids}
        self.anomalies_by_severity: Dict[str, Set[str]] = {}  # severity_level -> {anomaly_ids}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Registry metadata
        self.creation_time = datetime.now()
        self.last_modified = datetime.now()
        
        # Initialize severity buckets
        self._initialize_severity_buckets()
    
    def _initialize_severity_buckets(self):
        """Initialize severity level buckets."""
        self.anomalies_by_severity = {
            "low": set(),      # 0.0 - 0.3
            "medium": set(),   # 0.3 - 0.6
            "high": set(),     # 0.6 - 0.9
            "critical": set()  # 0.9 - 1.0
        }
    
    def register_anomaly(self, anomaly: BaseAnomaly) -> str:
        """
        Register an anomaly and return its ID.
        
        Args:
            anomaly: The anomaly instance to register
            
        Returns:
            The anomaly's unique ID
            
        Raises:
            ValueError: If anomaly name is already registered
        """
        with self._lock:
            # Check for name conflicts
            if anomaly.name in self.anomalies_by_name:
                existing_id = self.anomalies_by_name[anomaly.name]
                if existing_id != anomaly.anomaly_id:
                    raise ValueError(f"Anomaly name '{anomaly.name}' is already registered")
            
            # Register the anomaly
            self.anomalies[anomaly.anomaly_id] = anomaly
            self.anomalies_by_name[anomaly.name] = anomaly.anomaly_id
            
            # Update indexes
            self._update_tag_index(anomaly)
            self._update_severity_index(anomaly)
            
            # Update modification time
            self.last_modified = datetime.now()
            
            return anomaly.anomaly_id
    
    def unregister_anomaly(self, anomaly_id: str) -> bool:
        """
        Unregister an anomaly by ID.
        
        Args:
            anomaly_id: ID of anomaly to unregister
            
        Returns:
            True if anomaly was found and removed, False otherwise
        """
        with self._lock:
            if anomaly_id not in self.anomalies:
                return False
            
            anomaly = self.anomalies[anomaly_id]
            
            # Remove from main storage
            del self.anomalies[anomaly_id]
            del self.anomalies_by_name[anomaly.name]
            
            # Remove from indexes
            self._remove_from_tag_index(anomaly)
            self._remove_from_severity_index(anomaly)
            
            # Remove from any sets
            for set_name, anomaly_ids in self.anomaly_sets.items():
                if anomaly_id in anomaly_ids:
                    anomaly_ids.remove(anomaly_id)
            
            # Update modification time
            self.last_modified = datetime.now()
            
            return True
    
    def get_anomaly(self, identifier: str) -> Optional[BaseAnomaly]:
        """
        Get anomaly by ID or name.
        
        Args:
            identifier: Anomaly ID or name
            
        Returns:
            Anomaly instance or None if not found
        """
        with self._lock:
            # Try as ID first
            if identifier in self.anomalies:
                return self.anomalies[identifier]
            
            # Try as name
            if identifier in self.anomalies_by_name:
                anomaly_id = self.anomalies_by_name[identifier]
                return self.anomalies[anomaly_id]
            
            return None
    
    def create_anomaly_set(self, set_name: str, anomaly_identifiers: List[str]) -> bool:
        """
        Create a named set of anomalies.
        
        Args:
            set_name: Name for the anomaly set
            anomaly_identifiers: List of anomaly IDs or names
            
        Returns:
            True if set was created successfully
            
        Raises:
            ValueError: If any anomaly identifier is not found
        """
        with self._lock:
            # Resolve all identifiers to IDs
            anomaly_ids = []
            for identifier in anomaly_identifiers:
                anomaly = self.get_anomaly(identifier)
                if anomaly is None:
                    raise ValueError(f"Anomaly '{identifier}' not found in registry")
                anomaly_ids.append(anomaly.anomaly_id)
            
            # Create the set
            self.anomaly_sets[set_name] = anomaly_ids
            self.last_modified = datetime.now()
            
            return True
    
    def get_anomaly_set(self, set_name: str) -> List[BaseAnomaly]:
        """
        Get list of anomaly objects for a named set.
        
        Args:
            set_name: Name of the anomaly set
            
        Returns:
            List of anomaly instances (empty if set not found)
        """
        with self._lock:
            if set_name not in self.anomaly_sets:
                return []
            
            anomalies = []
            for anomaly_id in self.anomaly_sets[set_name]:
                if anomaly_id in self.anomalies:
                    anomalies.append(self.anomalies[anomaly_id])
            
            return anomalies
    
    def add_to_set(self, set_name: str, anomaly_identifier: str) -> bool:
        """
        Add an anomaly to an existing set.
        
        Args:
            set_name: Name of the set
            anomaly_identifier: Anomaly ID or name to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            if set_name not in self.anomaly_sets:
                return False
            
            anomaly = self.get_anomaly(anomaly_identifier)
            if anomaly is None:
                return False
            
            if anomaly.anomaly_id not in self.anomaly_sets[set_name]:
                self.anomaly_sets[set_name].append(anomaly.anomaly_id)
                self.last_modified = datetime.now()
            
            return True
    
    def remove_from_set(self, set_name: str, anomaly_identifier: str) -> bool:
        """
        Remove an anomaly from a set.
        
        Args:
            set_name: Name of the set
            anomaly_identifier: Anomaly ID or name to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            if set_name not in self.anomaly_sets:
                return False
            
            anomaly = self.get_anomaly(anomaly_identifier)
            if anomaly is None:
                return False
            
            if anomaly.anomaly_id in self.anomaly_sets[set_name]:
                self.anomaly_sets[set_name].remove(anomaly.anomaly_id)
                self.last_modified = datetime.now()
                return True
            
            return False
    
    def get_anomalies_by_tag(self, tag: str) -> List[BaseAnomaly]:
        """
        Get all anomalies with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of anomalies with the specified tag
        """
        with self._lock:
            if tag not in self.anomalies_by_tag:
                return []
            
            anomalies = []
            for anomaly_id in self.anomalies_by_tag[tag]:
                if anomaly_id in self.anomalies:
                    anomalies.append(self.anomalies[anomaly_id])
            
            return anomalies
    
    def get_anomalies_by_severity(self, severity_level: str) -> List[BaseAnomaly]:
        """
        Get all anomalies at a specific severity level.
        
        Args:
            severity_level: One of 'low', 'medium', 'high', 'critical'
            
        Returns:
            List of anomalies at the specified severity level
        """
        with self._lock:
            if severity_level not in self.anomalies_by_severity:
                return []
            
            anomalies = []
            for anomaly_id in self.anomalies_by_severity[severity_level]:
                if anomaly_id in self.anomalies:
                    anomalies.append(self.anomalies[anomaly_id])
            
            return anomalies
    
    def add_context_rule(self, rule_func: Callable[[Dict[str, Any], 'AnomalyRegistry'], List[BaseAnomaly]]):
        """
        Add a function that determines active anomalies based on context.
        
        Args:
            rule_func: Function that takes (context, registry) and returns list of anomalies
        """
        with self._lock:
            self.context_rules.append(rule_func)
            self.last_modified = datetime.now()
    
    def remove_context_rule(self, rule_func: Callable) -> bool:
        """
        Remove a context rule function.
        
        Args:
            rule_func: The rule function to remove
            
        Returns:
            True if rule was found and removed
        """
        with self._lock:
            if rule_func in self.context_rules:
                self.context_rules.remove(rule_func)
                self.last_modified = datetime.now()
                return True
            return False
    
    def get_active_anomalies_for_context(self, context: Dict[str, Any]) -> List[BaseAnomaly]:
        """
        Determine which anomalies should be active based on context.
        
        Args:
            context: Context dictionary with environment/situation information
            
        Returns:
            List of anomalies that should be active for this context
        """
        active_anomalies = []
        
        with self._lock:
            for rule in self.context_rules:
                try:
                    suggested_anomalies = rule(context, self)
                    if suggested_anomalies:
                        active_anomalies.extend(suggested_anomalies)
                except Exception as e:
                    # Log error but don't break the system
                    print(f"Error in context rule: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_anomalies = []
        for anomaly in active_anomalies:
            if anomaly.anomaly_id not in seen:
                seen.add(anomaly.anomaly_id)
                unique_anomalies.append(anomaly)
        
        return unique_anomalies
    
    def _update_tag_index(self, anomaly: BaseAnomaly):
        """Update tag index for an anomaly."""
        for tag in anomaly.tags:
            if tag not in self.anomalies_by_tag:
                self.anomalies_by_tag[tag] = set()
            self.anomalies_by_tag[tag].add(anomaly.anomaly_id)
    
    def _remove_from_tag_index(self, anomaly: BaseAnomaly):
        """Remove anomaly from tag index."""
        for tag in anomaly.tags:
            if tag in self.anomalies_by_tag:
                self.anomalies_by_tag[tag].discard(anomaly.anomaly_id)
                # Clean up empty tag sets
                if not self.anomalies_by_tag[tag]:
                    del self.anomalies_by_tag[tag]
    
    def _update_severity_index(self, anomaly: BaseAnomaly):
        """Update severity index for an anomaly."""
        severity_level = self._get_severity_level(anomaly.severity)
        self.anomalies_by_severity[severity_level].add(anomaly.anomaly_id)
    
    def _remove_from_severity_index(self, anomaly: BaseAnomaly):
        """Remove anomaly from severity index."""
        for severity_set in self.anomalies_by_severity.values():
            severity_set.discard(anomaly.anomaly_id)
    
    def _get_severity_level(self, severity: float) -> str:
        """Convert numeric severity to level string."""
        if severity < 0.3:
            return "low"
        elif severity < 0.6:
            return "medium"
        elif severity < 0.9:
            return "high"
        else:
            return "critical"
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the registry.
        
        Returns:
            Dictionary with registry statistics
        """
        with self._lock:
            return {
                "total_anomalies": len(self.anomalies),
                "anomaly_sets": len(self.anomaly_sets),
                "context_rules": len(self.context_rules),
                "creation_time": self.creation_time.isoformat(),
                "last_modified": self.last_modified.isoformat(),
                "severity_distribution": {
                    level: len(anomaly_ids) 
                    for level, anomaly_ids in self.anomalies_by_severity.items()
                },
                "tag_distribution": {
                    tag: len(anomaly_ids) 
                    for tag, anomaly_ids in self.anomalies_by_tag.items()
                },
                "set_sizes": {
                    set_name: len(anomaly_ids)
                    for set_name, anomaly_ids in self.anomaly_sets.items()
                }
            }
    
    def list_sets(self) -> List[str]:
        """Get list of all anomaly set names."""
        with self._lock:
            return list(self.anomaly_sets.keys())
    
    def list_tags(self) -> List[str]:
        """Get list of all tags used by anomalies."""
        with self._lock:
            return list(self.anomalies_by_tag.keys())
    
    def list_anomalies(self) -> List[str]:
        """Get list of all anomaly names."""
        with self._lock:
            return list(self.anomalies_by_name.keys())
    
    def export_registry(self, include_anomaly_data: bool = False) -> Dict[str, Any]:
        """
        Export registry configuration for backup/transfer.
        
        Args:
            include_anomaly_data: Whether to include full anomaly objects
            
        Returns:
            Exportable registry data
        """
        with self._lock:
            export_data = {
                "metadata": {
                    "creation_time": self.creation_time.isoformat(),
                    "last_modified": self.last_modified.isoformat(),
                    "export_time": datetime.now().isoformat()
                },
                "anomaly_sets": self.anomaly_sets.copy(),
                "statistics": self.get_registry_stats()
            }
            
            if include_anomaly_data:
                export_data["anomalies"] = {
                    anomaly_id: anomaly.get_metadata()
                    for anomaly_id, anomaly in self.anomalies.items()
                }
            
            return export_data
    
    def clear_registry(self):
        """Clear all anomalies and sets (use with caution)."""
        with self._lock:
            self.anomalies.clear()
            self.anomaly_sets.clear()
            self.context_rules.clear()
            self.anomalies_by_name.clear()
            self.anomalies_by_tag.clear()
            self._initialize_severity_buckets()
            self.last_modified = datetime.now()


# Global registry instance
anomaly_registry = AnomalyRegistry()


# Convenience functions for common operations
def register_anomaly(anomaly: BaseAnomaly) -> str:
    """Register an anomaly with the global registry."""
    return anomaly_registry.register_anomaly(anomaly)


def get_anomaly(identifier: str) -> Optional[BaseAnomaly]:
    """Get an anomaly from the global registry."""
    return anomaly_registry.get_anomaly(identifier)


def create_anomaly_set(set_name: str, anomaly_identifiers: List[str]) -> bool:
    """Create an anomaly set in the global registry."""
    return anomaly_registry.create_anomaly_set(set_name, anomaly_identifiers)


def get_anomaly_set(set_name: str) -> List[BaseAnomaly]:
    """Get an anomaly set from the global registry."""
    return anomaly_registry.get_anomaly_set(set_name)


def add_context_rule(rule_func: Callable):
    """Add a context rule to the global registry."""
    anomaly_registry.add_context_rule(rule_func)


# Example context rules for common scenarios
def game_context_rule(context: Dict[str, Any], registry: AnomalyRegistry) -> List[BaseAnomaly]:
    """Context rule for game environments."""
    environment = context.get("environment", "unknown")
    player_count = context.get("player_count", 0)
    
    active_anomalies = []
    
    # Always include critical security anomalies
    active_anomalies.extend(registry.get_anomalies_by_tag("security"))
    
    # Add performance monitoring in production
    if environment == "production":
        active_anomalies.extend(registry.get_anomalies_by_tag("performance"))
    
    # Add anti-cheat measures for multiplayer
    if player_count > 1:
        active_anomalies.extend(registry.get_anomalies_by_tag("anti-cheat"))
    
    return active_anomalies


def business_context_rule(context: Dict[str, Any], registry: AnomalyRegistry) -> List[BaseAnomaly]:
    """Context rule for business applications."""
    business_hours = context.get("business_hours", True)
    transaction_volume = context.get("transaction_volume", "normal")
    
    active_anomalies = []
    
    # Always monitor for fraud
    active_anomalies.extend(registry.get_anomalies_by_tag("fraud"))
    
    # Enhanced monitoring during business hours
    if business_hours:
        active_anomalies.extend(registry.get_anomalies_by_tag("business-critical"))
    
    # Additional monitoring during high volume
    if transaction_volume == "high":
        active_anomalies.extend(registry.get_anomalies_by_tag("volume-sensitive"))
    
    return active_anomalies