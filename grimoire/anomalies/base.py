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
Core Anomaly Detection Classes

This module implements the foundational anomaly detection architecture including
BaseAnomaly, CompositeAnomaly, and AdaptiveAnomaly classes.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import time
import threading


class BaseAnomaly(ABC):
    """
    Base class for all anomaly detection artifacts.
    
    Anomalies are programmable detection patterns that can be assigned to
    familiars for proactive monitoring during normal entity processing.
    """
    
    def __init__(self, name: str, severity: float = 0.5, description: str = ""):
        """
        Initialize base anomaly.
        
        Args:
            name: Unique identifier for this anomaly type
            severity: Severity level (0.0 = info, 1.0 = critical)
            description: Human-readable description of what this anomaly detects
        """
        self.anomaly_id = str(uuid.uuid4())
        self.name = name
        self.severity = max(0.0, min(1.0, severity))  # Clamp to [0.0, 1.0]
        self.description = description
        self.detection_count = 0
        self.last_detection = None
        self.creation_time = datetime.now()
        self.enabled = True
        self.tags = set()  # For categorization and filtering
        
        # Thread safety for detection counting
        self._lock = threading.Lock()
    
    @abstractmethod
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """
        Check if anomaly condition is met for given entity and world state.
        
        Args:
            entity_state: Dictionary of entity properties and current state
            world_state: Dictionary of global world/system state
            
        Returns:
            True if anomaly condition is detected, False otherwise
            
        Note:
            This method must be implemented by all subclasses.
            Should be fast and stateless for optimal performance.
        """
        pass
    
    def report_detection(self, entity: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log detection occurrence and create standardized report.
        
        Args:
            entity: The entity where anomaly was detected
            context: Additional context information about the detection
            
        Returns:
            Standardized anomaly report dictionary
        """
        with self._lock:
            self.detection_count += 1
            self.last_detection = datetime.now()
        
        # Extract entity identifier
        entity_id = getattr(entity, 'name', None) or getattr(entity, 'id', str(entity))
        
        report = {
            "anomaly_id": self.anomaly_id,
            "anomaly_name": self.name,
            "anomaly_type": self.__class__.__name__,
            "severity": self.severity,
            "entity_id": entity_id,
            "context": context,
            "timestamp": self.last_detection.isoformat(),
            "detection_count": self.detection_count,
            "tags": list(self.tags)
        }
        
        return report
    
    def should_escalate(self) -> bool:
        """
        Determine if this anomaly should be escalated to higher-level agents.
        
        Returns:
            True if anomaly should be escalated based on severity or frequency
        """
        # Escalate critical anomalies immediately
        if self.severity >= 0.8:
            return True
        
        # Escalate if we've seen this anomaly too frequently
        if self.detection_count > 10:
            return True
        
        # Escalate medium-severity anomalies after multiple detections
        if self.severity >= 0.6 and self.detection_count > 5:
            return True
        
        return False
    
    def add_tag(self, tag: str):
        """Add a tag for categorization."""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag."""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if anomaly has specific tag."""
        return tag in self.tags
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return comprehensive anomaly metadata for debugging/monitoring.
        
        Returns:
            Dictionary containing all anomaly metadata
        """
        with self._lock:
            return {
                "id": self.anomaly_id,
                "name": self.name,
                "type": self.__class__.__name__,
                "severity": self.severity,
                "description": self.description,
                "detection_count": self.detection_count,
                "last_detection": self.last_detection.isoformat() if self.last_detection else None,
                "creation_time": self.creation_time.isoformat(),
                "enabled": self.enabled,
                "tags": list(self.tags)
            }
    
    def reset_statistics(self):
        """Reset detection statistics (useful for testing)."""
        with self._lock:
            self.detection_count = 0
            self.last_detection = None
    
    def __str__(self) -> str:
        return f"Anomaly({self.name}, severity={self.severity}, detections={self.detection_count})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', severity={self.severity})"


class CompositeAnomaly(BaseAnomaly):
    """
    Anomaly that requires multiple sub-anomalies to trigger.
    
    Useful for detecting complex patterns that require multiple conditions
    to be met simultaneously (e.g., coordinated attacks, system failures).
    """
    
    def __init__(self, name: str, sub_anomalies: List[BaseAnomaly], 
                 threshold: Optional[int] = None, severity: float = 0.8,
                 description: str = ""):
        """
        Initialize composite anomaly.
        
        Args:
            name: Name for this composite anomaly
            sub_anomalies: List of anomalies that comprise this composite
            threshold: Number of sub-anomalies that must trigger (default: all)
            severity: Severity level for this composite anomaly
            description: Description of what this composite detects
        """
        super().__init__(name, severity, description)
        self.sub_anomalies = sub_anomalies.copy()
        self.threshold = threshold if threshold is not None else len(sub_anomalies)
        self.last_triggered_anomalies = []  # Track which sub-anomalies triggered
        
        # Validate threshold
        if self.threshold <= 0 or self.threshold > len(self.sub_anomalies):
            raise ValueError(f"Threshold {self.threshold} must be between 1 and {len(self.sub_anomalies)}")
        
        # Add composite tag
        self.add_tag("composite")
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """
        Check if enough sub-anomalies trigger to meet threshold.
        
        Args:
            entity_state: Entity state dictionary
            world_state: World state dictionary
            
        Returns:
            True if threshold number of sub-anomalies are detected
        """
        triggered_anomalies = []
        triggered_count = 0
        
        for anomaly in self.sub_anomalies:
            if not anomaly.enabled:
                continue
                
            try:
                if anomaly.detect(entity_state, world_state):
                    triggered_anomalies.append(anomaly)
                    triggered_count += 1
                    
                    # Early exit if we've met threshold
                    if triggered_count >= self.threshold:
                        break
                        
            except Exception as e:
                # Log sub-anomaly error but continue checking others
                print(f"Error in sub-anomaly {anomaly.name}: {e}")
        
        # Store which anomalies triggered for reporting
        self.last_triggered_anomalies = triggered_anomalies
        
        return triggered_count >= self.threshold
    
    def report_detection(self, entity: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced report including which sub-anomalies triggered.
        
        Args:
            entity: Entity where anomaly was detected
            context: Additional context
            
        Returns:
            Enhanced report with sub-anomaly details
        """
        base_report = super().report_detection(entity, context)
        
        # Add composite-specific information
        base_report.update({
            "composite_type": "threshold_based",
            "threshold": self.threshold,
            "total_sub_anomalies": len(self.sub_anomalies),
            "triggered_sub_anomalies": [
                {
                    "name": anomaly.name,
                    "severity": anomaly.severity,
                    "type": anomaly.__class__.__name__
                }
                for anomaly in self.last_triggered_anomalies
            ],
            "triggered_count": len(self.last_triggered_anomalies)
        })
        
        return base_report
    
    def add_sub_anomaly(self, anomaly: BaseAnomaly):
        """Add a new sub-anomaly to the composite."""
        if anomaly not in self.sub_anomalies:
            self.sub_anomalies.append(anomaly)
    
    def remove_sub_anomaly(self, anomaly: BaseAnomaly):
        """Remove a sub-anomaly from the composite."""
        if anomaly in self.sub_anomalies:
            self.sub_anomalies.remove(anomaly)
            # Adjust threshold if necessary
            if self.threshold > len(self.sub_anomalies):
                self.threshold = len(self.sub_anomalies)
    
    def set_threshold(self, new_threshold: int):
        """Update the threshold for triggering."""
        if 1 <= new_threshold <= len(self.sub_anomalies):
            self.threshold = new_threshold
        else:
            raise ValueError(f"Threshold must be between 1 and {len(self.sub_anomalies)}")


class AdaptiveAnomaly(BaseAnomaly):
    """
    Anomaly that learns from baseline data and adapts detection thresholds.
    
    This anomaly type automatically builds statistical baselines for specified
    properties and detects when values deviate significantly from normal patterns.
    """
    
    def __init__(self, name: str, properties: List[str], 
                 threshold_multiplier: float = 2.0, min_samples: int = 10,
                 severity: float = 0.6, description: str = ""):
        """
        Initialize adaptive anomaly.
        
        Args:
            name: Name for this adaptive anomaly
            properties: List of entity properties to monitor
            threshold_multiplier: Standard deviations from mean to trigger (default: 2.0)
            min_samples: Minimum samples needed before detection activates
            severity: Severity level
            description: Description of what this detects
        """
        super().__init__(name, severity, description)
        self.properties = properties.copy()
        self.threshold_multiplier = threshold_multiplier
        self.min_samples = min_samples
        self.baselines = {}  # property -> statistical baseline data
        self.learning_enabled = True
        self.sample_count = 0
        
        # Initialize baseline storage for each property
        for prop in self.properties:
            self.baselines[prop] = {
                'sum': 0.0,
                'sum_sq': 0.0,
                'count': 0,
                'mean': 0.0,
                'std_dev': 0.0,
                'min_val': float('inf'),
                'max_val': float('-inf')
            }
        
        # Add adaptive tag
        self.add_tag("adaptive")
        self.add_tag("learning")
    
    def learn_from_sample(self, entity_state: Dict[str, Any]):
        """
        Update baseline statistics with new sample data.
        
        Args:
            entity_state: Entity state to learn from
        """
        if not self.learning_enabled:
            return
        
        learned_any = False
        
        for prop in self.properties:
            if prop in entity_state:
                value = entity_state[prop]
                if isinstance(value, (int, float)):
                    self._update_baseline(prop, float(value))
                    learned_any = True
        
        if learned_any:
            self.sample_count += 1
    
    def _update_baseline(self, property_name: str, value: float):
        """
        Update running statistics for a property baseline.
        
        Args:
            property_name: Name of the property
            value: New value to incorporate into baseline
        """
        baseline = self.baselines[property_name]
        
        # Update running statistics
        baseline['sum'] += value
        baseline['sum_sq'] += value * value
        baseline['count'] += 1
        baseline['min_val'] = min(baseline['min_val'], value)
        baseline['max_val'] = max(baseline['max_val'], value)
        
        # Recalculate mean and standard deviation
        baseline['mean'] = baseline['sum'] / baseline['count']
        
        if baseline['count'] > 1:
            # Calculate variance using the computational formula
            variance = (baseline['sum_sq'] / baseline['count']) - (baseline['mean'] ** 2)
            baseline['std_dev'] = max(0.0, variance) ** 0.5  # Ensure non-negative
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """
        Detect anomalies by comparing current values to learned baselines.
        
        Args:
            entity_state: Current entity state
            world_state: Current world state
            
        Returns:
            True if any monitored property deviates significantly from baseline
        """
        # First, update baselines if learning is enabled
        if self.learning_enabled:
            self.learn_from_sample(entity_state)
        
        # Don't detect until we have sufficient samples
        if self.sample_count < self.min_samples:
            return False
        
        # Check each monitored property for anomalies
        for prop in self.properties:
            if prop in entity_state and prop in self.baselines:
                value = entity_state[prop]
                
                if isinstance(value, (int, float)):
                    if self._is_anomalous_value(prop, float(value)):
                        return True
        
        return False
    
    def _is_anomalous_value(self, property_name: str, value: float) -> bool:
        """
        Check if a value is anomalous for a given property.
        
        Args:
            property_name: Name of the property
            value: Value to check
            
        Returns:
            True if value is anomalous
        """
        baseline = self.baselines[property_name]
        
        # Need sufficient data and non-zero standard deviation
        if baseline['count'] < self.min_samples or baseline['std_dev'] <= 0:
            return False
        
        # Calculate z-score (number of standard deviations from mean)
        z_score = abs(value - baseline['mean']) / baseline['std_dev']
        
        return z_score > self.threshold_multiplier
    
    def get_baseline_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get current baseline statistics for all monitored properties.
        
        Returns:
            Dictionary mapping property names to their baseline statistics
        """
        return {
            prop: {
                'mean': baseline['mean'],
                'std_dev': baseline['std_dev'],
                'min': baseline['min_val'],
                'max': baseline['max_val'],
                'sample_count': baseline['count']
            }
            for prop, baseline in self.baselines.items()
        }
    
    def set_threshold_multiplier(self, multiplier: float):
        """Update the threshold multiplier for detection sensitivity."""
        if multiplier > 0:
            self.threshold_multiplier = multiplier
        else:
            raise ValueError("Threshold multiplier must be positive")
    
    def enable_learning(self):
        """Enable baseline learning from new samples."""
        self.learning_enabled = True
        self.remove_tag("learning_disabled")
        self.add_tag("learning")
    
    def disable_learning(self):
        """Disable baseline learning (use current baselines only)."""
        self.learning_enabled = False
        self.remove_tag("learning")
        self.add_tag("learning_disabled")
    
    def reset_baselines(self):
        """Reset all baseline statistics (useful for retraining)."""
        for prop in self.properties:
            self.baselines[prop] = {
                'sum': 0.0,
                'sum_sq': 0.0,
                'count': 0,
                'mean': 0.0,
                'std_dev': 0.0,
                'min_val': float('inf'),
                'max_val': float('-inf')
            }
        self.sample_count = 0
    
    def report_detection(self, entity: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced report including baseline statistics and deviation details.
        
        Args:
            entity: Entity where anomaly was detected
            context: Additional context
            
        Returns:
            Enhanced report with adaptive-specific details
        """
        base_report = super().report_detection(entity, context)
        
        # Add adaptive-specific information
        base_report.update({
            "adaptive_type": "statistical_baseline",
            "threshold_multiplier": self.threshold_multiplier,
            "sample_count": self.sample_count,
            "learning_enabled": self.learning_enabled,
            "baseline_stats": self.get_baseline_stats(),
            "monitored_properties": self.properties
        })
        
        return base_report