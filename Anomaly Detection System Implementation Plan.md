# Anomaly Detection System Implementation Plan

## Overview

### Original concept:

To go along with the agent system: Anomaly artifact, which can be defined in arbitrary terms, and the set an archon or spirit (which can in turn give it to a familiar as a pact goal) to look out for and report such things. In a game, we might define an anomaly as a creature with negative health (something that should be dead and freed from the queue; whenever the agent encounters something with this condition, it reports it. In an application dealing with finances, one anomaly might be defined as a customer with a negative balance, or and investment that has never increased in value; instead of having to do regular searches for such anomalies, they are reported whenever they are encountered.

This plan implements a comprehensive anomaly detection system that integrates with Grimoire's existing agent infrastructure. The system transforms expensive periodic searches into efficient, agent-driven detection through programmable Anomaly artifacts.


## Conceptual Notes:

## Anomaly Artifact Architecture

### **Core Anomaly Artifact

```grimoire
artifact BaseAnomaly:
    bind name = $SCROLL(unnamed_anomaly)
    bind severity = 0.5  # 0.0 = info, 1.0 = critical
    bind description = $SCROLL(No description provided)
    bind detection_count = 0
    bind last_detection = null
    
    # Abstract detection method - must be overridden
    ritual detect(entity_state, world_state):
        # Override in specific anomaly types
        return false
    
    # Logging and reporting
    ritual report_detection(entity, context):
        self.detection_count = self.detection_count added to 1
        self.last_detection = get_current_time upon
        
        bind report = {
            anomaly_type: self.name,
            severity: self.severity,
            entity: entity.name,
            context: context,
            timestamp: self.last_detection
        }
        
        return report
    
    # Threshold checking for escalation
    ritual should_escalate():
        return self.severity > 0.8 or self.detection_count > 10
```

### **Game-Specific Anomalies**

```grimoire
# Dead entity still active
artifact UndeadAnomaly extends BaseAnomaly:
    bind name = $SCROLL(undead_entity)
    bind severity = 0.9
    bind description = $SCROLL(Entity with negative health still active)
    
    ritual detect(entity_state, world_state):
        bind health = entity_state.get_property($SCROLL(health))
        bind is_active = entity_state.get_property($SCROLL(active))
        
        if health <= 0 and is_active:
            return true
        return false

# Resource leak detection
artifact ResourceLeakAnomaly extends BaseAnomaly:
    bind name = $SCROLL(resource_leak)
    bind severity = 0.7
    bind description = $SCROLL(Entity consuming resources without producing value)
    
    ritual detect(entity_state, world_state):
        bind resource_consumption = entity_state.get_property($SCROLL(resource_usage))
        bind value_produced = entity_state.get_property($SCROLL(value_generated))
        bind uptime = entity_state.get_property($SCROLL(active_time))
        
        # Flag entities consuming resources for extended time without output
        if resource_consumption > 0 and value_produced == 0 and uptime > 300:
            return true
        return false

# Player behavior anomalies
artifact SuspiciousPlayerAnomaly extends BaseAnomaly:
    bind name = $SCROLL(suspicious_player_behavior)
    bind severity = 0.6
    bind description = $SCROLL(Player actions suggest cheating or exploits)
    
    ritual detect(entity_state, world_state):
        bind actions_per_second = entity_state.get_property($SCROLL(action_rate))
        bind impossible_movements = entity_state.get_property($SCROLL(teleport_count))
        bind resource_gain_rate = entity_state.get_property($SCROLL(resource_acceleration))
        
        # Multiple suspicious indicators
        if actions_per_second > 20 or impossible_movements > 0 or resource_gain_rate > 1000:
            return true
        return false
```

### **Business Application Anomalies**

```grimoire
# Financial anomalies
artifact NegativeBalanceAnomaly extends BaseAnomaly:
    bind name = $SCROLL(negative_customer_balance)
    bind severity = 0.8
    bind description = $SCROLL(Customer account with negative balance)
    
    ritual detect(entity_state, world_state):
        bind account_balance = entity_state.get_property($SCROLL(balance))
        bind account_type = entity_state.get_property($SCROLL(account_type))
        
        # Different rules for different account types
        if account_type == $SCROLL(checking) and account_balance < -100:
            return true
        elif account_type == $SCROLL(credit) and account_balance < -10000:
            return true
        return false

# Investment performance anomalies
artifact StagnantInvestmentAnomaly extends BaseAnomaly:
    bind name = $SCROLL(stagnant_investment)
    bind severity = 0.6
    bind description = $SCROLL(Investment with no growth over extended period)
    
    ritual detect(entity_state, world_state):
        bind initial_value = entity_state.get_property($SCROLL(initial_investment))
        bind current_value = entity_state.get_property($SCROLL(current_value))
        bind days_held = entity_state.get_property($SCROLL(days_since_purchase))
        
        # Flag investments that haven't grown in 90+ days
        if days_held > 90 and current_value <= initial_value:
            return true
        return false

# Data integrity anomalies
artifact DataIntegrityAnomaly extends BaseAnomaly:
    bind name = $SCROLL(data_corruption)
    bind severity = 1.0
    bind description = $SCROLL(Entity data violates business rules)
    
    ritual detect(entity_state, world_state):
        bind customer_age = entity_state.get_property($SCROLL(age))
        bind account_creation = entity_state.get_property($SCROLL(created_date))
        bind ssn = entity_state.get_property($SCROLL(ssn))
        
        # Multiple data validation rules
        if customer_age < 0 or customer_age > 150:
            return true
        if account_creation > get_current_time upon:
            return true
        if ssn and not validate_ssn(ssn):
            return true
        return false
```

## Agent Integration

### **Anomaly Detection Pacts**

```grimoire
# Familiars can be assigned anomaly detection duties
bind security_spirit = create_spirit upon $SCROLL(SecurityOfficer), $SCROLL(Monitoring), $SCROLL(security)

bind watchdog_familiar = create_familiar_with_pact upon security_spirit, $SCROLL(Watchdog), [
    $SCROLL(monitor_entities), 
    $SCROLL(detect_anomalies), 
    $SCROLL(report_violations)
]

# Assign specific anomalies to watch for
watchdog_familiar.add_anomaly_watch(undead_anomaly)
watchdog_familiar.add_anomaly_watch(resource_leak_anomaly)
watchdog_familiar.add_anomaly_watch(suspicious_player_anomaly)
```

### **Proactive Anomaly Detection

```grimoire
# Extend familiar base class for anomaly detection
class AnomalyDetectorMixin:
    def __init__(self):
        self.watched_anomalies = []
        self.detection_log = []
        
    def add_anomaly_watch(self, anomaly_artifact):
        self.watched_anomalies.append(anomaly_artifact)
        
    def scan_for_anomalies(self, entity, world_state):
        """Check entity against all watched anomalies"""
        detected_anomalies = []
        
        for anomaly in self.watched_anomalies:
            if anomaly.detect(entity, world_state):
                report = anomaly.report_detection(entity, world_state)
                detected_anomalies.append(report)
                self.detection_log.append(report)
                
                # Send via socket if available
                if self.has_socket("anomaly_output"):
                    self.send_to_socket("anomaly_output", report)
                    
                # Escalate critical anomalies
                if anomaly.should_escalate():
                    self.escalate_anomaly(report)
                    
        return detected_anomalies
        
    def escalate_anomaly(self, report):
        """Send critical anomalies to higher-level agents"""
        if self.has_socket("escalation_output"):
            self.send_to_socket("escalation_output", {
                "type": "critical_anomaly",
                "report": report,
                "escalation_level": "immediate"
            })
```

### **Hierarchical Anomaly Reporting**

```grimoire
# Familiars detect -> Spirits aggregate -> Archons decide

# Familiar level: Direct detection
bind patrol_familiar = create_familiar_with_pact upon security_spirit, $SCROLL(Patrol), [
    $SCROLL(scan_entities), $SCROLL(detect_anomalies)
]

# Spirit level: Anomaly aggregation and analysis
bind security_spirit = create_spirit upon $SCROLL(SecurityChief), $SCROLL(Security), $SCROLL(monitoring)
connect_socket upon patrol_familiar.anomaly_output, security_spirit.anomaly_input

# Archon level: Strategic response to anomaly patterns
bind system_archon = create_archon upon $SCROLL(SystemManager), $SCROLL(Administration)
connect_socket upon security_spirit.pattern_analysis, system_archon.threat_assessment
```

## Advanced Anomaly Features

### **Composite Anomalies

```grimoire
# Anomalies that require multiple conditions
artifact CompositeAttackAnomaly extends BaseAnomaly:
    bind name = $SCROLL(coordinated_attack)
    bind severity = 1.0
    bind sub_anomalies = []
    
    ritual detect(entity_state, world_state):
        bind detected_count = 0
        
        # Check all sub-anomalies
        for sub_anomaly in self.sub_anomalies:
            if sub_anomaly.detect(entity_state, world_state):
                detected_count = detected_count added to 1
                
        # Trigger if multiple anomalies detected simultaneously
        return detected_count >= 3

# Usage
bind attack_detector = conjure CompositeAttackAnomaly upon
attack_detector.sub_anomalies.add(suspicious_player_anomaly)
attack_detector.sub_anomalies.add(resource_leak_anomaly)
attack_detector.sub_anomalies.add(rapid_action_anomaly)
```

### **Learning Anomalies**

```grimoire
# Anomalies that adapt their detection criteria
artifact AdaptiveAnomaly extends BaseAnomaly:
    bind baseline_values = {}
    bind detection_threshold = 2.0  # Standard deviations from normal
    
    ritual learn_baseline(entity_samples):
        # Calculate normal ranges from sample data
        for property_name in entity_samples.get_properties():
            bind values = entity_samples.get_all_values(property_name)
            bind mean = calculate_mean(values)
            bind std_dev = calculate_standard_deviation(values)
            
            self.baseline_values[property_name] = {
                mean: mean,
                std_dev: std_dev
            }
    
    ritual detect(entity_state, world_state):
        for property_name in self.baseline_values:
            bind current_value = entity_state.get_property(property_name)
            bind baseline = self.baseline_values[property_name]
            bind deviation = abs(current_value - baseline.mean) / baseline.std_dev
            
            if deviation > self.detection_threshold:
                return true
        return false
```

## Integration with Existing Systems

### **Socket Integration**

```grimoire
# Anomalies can communicate through the socket system
bind anomaly_aggregator = create_familiar_with_pact upon analysis_spirit, $SCROLL(Aggregator), [$SCROLL(collect_anomalies)]

# Connect multiple detection sources
connect_socket upon game_monitor.anomaly_output, anomaly_aggregator.anomaly_input
connect_socket upon finance_monitor.anomaly_output, anomaly_aggregator.anomaly_input
connect_socket upon player_monitor.anomaly_output, anomaly_aggregator.anomaly_input

# Output aggregated anomaly reports
connect_socket upon anomaly_aggregator.summary_output, system_dashboard.alert_input
```

### **Goal Integration**

```grimoire
# Anomaly detection as AI goals
artifact AnomalyDetectionGoal extends BaseGoalArtifact:
    bind target_anomaly = null
    bind detection_rate_target = 0.95
    
    ritual evaluate_satisfaction(world_state):
        bind total_entities = world_state.get_entity_count()
        bind scanned_entities = world_state.get_scanned_count()
        bind scan_rate = scanned_entities divided by total_entities
        
        return scan_rate

# AI agents can have goals to maintain anomaly detection coverage
bind security_ai = create_ai_familiar upon $SCROLL(SecurityAI)
bind detection_goal = conjure AnomalyDetectionGoal upon $SCROLL(maintain_coverage), 0.8
security_ai.add_goal(detection_goal)
```

This Anomaly system transforms agents from passive executors into proactive guardians that continuously monitor for problems and report them automatically. It's like giving every agent a "sixth sense" for detecting things that shouldn't be there - perfectly magical and highly practical!

## Phase 1: Core Anomaly Framework (Week 1-2)

### **1.1 Base Anomaly Artifact System**

**Goal**: Implement the foundational anomaly detection architecture

**Files to Create**:

- `grimoire/anomalies/base.py` - Core anomaly classes
- `grimoire/anomalies/registry.py` - Anomaly management system
- `grimoire/anomalies/detection.py` - Detection engine integration

**Implementation**:

```python
# grimoire/anomalies/base.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class BaseAnomaly(ABC):
    """Base class for all anomaly detection artifacts"""
    def __init__(self, name: str, severity: float = 0.5, description: str = ""):
        self.anomaly_id = str(uuid.uuid4())
        self.name = name
        self.severity = severity  # 0.0 = info, 1.0 = critical
        self.description = description
        self.detection_count = 0
        self.last_detection = None
        self.creation_time = datetime.now()
        self.enabled = True
        
    @abstractmethod
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """Check if anomaly condition is met. Must be implemented by subclasses."""
        pass
    
    def report_detection(self, entity: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log detection and create report"""
        self.detection_count += 1
        self.last_detection = datetime.now()
        
        report = {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.name,
            "severity": self.severity,
            "entity_id": getattr(entity, 'name', str(entity)),
            "context": context,
            "timestamp": self.last_detection.isoformat(),
            "detection_count": self.detection_count
        }
        
        return report
    
    def should_escalate(self) -> bool:
        """Determine if anomaly should be escalated to higher-level agents"""
        return self.severity > 0.8 or self.detection_count > 10
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return anomaly metadata for debugging/monitoring"""
        return {
            "id": self.anomaly_id,
            "name": self.name,
            "severity": self.severity,
            "description": self.description,
            "detection_count": self.detection_count,
            "last_detection": self.last_detection.isoformat() if self.last_detection else None,
            "enabled": self.enabled
        }

class CompositeAnomaly(BaseAnomaly):
    """Anomaly that requires multiple sub-anomalies to trigger"""
    def __init__(self, name: str, sub_anomalies: List[BaseAnomaly], 
                 threshold: int = None, severity: float = 0.8):
        super().__init__(name, severity)
        self.sub_anomalies = sub_anomalies
        self.threshold = threshold or len(sub_anomalies)  # Default: all must trigger
        
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        triggered_count = 0
        for anomaly in self.sub_anomalies:
            if anomaly.enabled and anomaly.detect(entity_state, world_state):
                triggered_count += 1
                
        return triggered_count >= self.threshold

class AdaptiveAnomaly(BaseAnomaly):
    """Anomaly that learns from baseline data and adapts thresholds"""
    def __init__(self, name: str, properties: List[str], threshold_multiplier: float = 2.0):
        super().__init__(name, 0.6)
        self.properties = properties
        self.threshold_multiplier = threshold_multiplier
        self.baselines = {}  # property -> {mean, std_dev, sample_count}
        self.learning_enabled = True
        
    def learn_from_sample(self, entity_state: Dict[str, Any]):
        """Update baseline statistics with new sample"""
        if not self.learning_enabled:
            return
            
        for prop in self.properties:
            if prop in entity_state:
                value = entity_state[prop]
                if isinstance(value, (int, float)):
                    self._update_baseline(prop, value)
    
    def _update_baseline(self, property_name: str, value: float):
        """Update running statistics for property baseline"""
        if property_name not in self.baselines:
            self.baselines[property_name] = {
                'sum': 0, 'sum_sq': 0, 'count': 0, 'mean': 0, 'std_dev': 0
            }
        
        baseline = self.baselines[property_name]
        baseline['sum'] += value
        baseline['sum_sq'] += value * value
        baseline['count'] += 1
        
        # Update mean and std dev
        baseline['mean'] = baseline['sum'] / baseline['count']
        if baseline['count'] > 1:
            variance = (baseline['sum_sq'] / baseline['count']) - (baseline['mean'] ** 2)
            baseline['std_dev'] = variance ** 0.5
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        # First, update baselines if learning is enabled
        if self.learning_enabled:
            self.learn_from_sample(entity_state)
        
        # Check for anomalies
        for prop in self.properties:
            if prop in entity_state and prop in self.baselines:
                value = entity_state[prop]
                baseline = self.baselines[prop]
                
                if baseline['count'] > 10 and baseline['std_dev'] > 0:  # Need sufficient data
                    deviation = abs(value - baseline['mean']) / baseline['std_dev']
                    if deviation > self.threshold_multiplier:
                        return True
        return False
```

**1.2 Anomaly Registry System**

```python
# grimoire/anomalies/registry.py
from typing import Dict, List, Set, Optional, Callable
from .base import BaseAnomaly

class AnomalyRegistry:
    """Central registry for managing anomaly definitions and detection sets"""
    
    def __init__(self):
        self.anomalies: Dict[str, BaseAnomaly] = {}
        self.anomaly_sets: Dict[str, List[str]] = {}  # named sets of anomaly IDs
        self.context_rules: List[Callable] = []  # functions that determine active anomalies
        
    def register_anomaly(self, anomaly: BaseAnomaly) -> str:
        """Register an anomaly and return its ID"""
        self.anomalies[anomaly.anomaly_id] = anomaly
        return anomaly.anomaly_id
    
    def create_anomaly_set(self, set_name: str, anomaly_ids: List[str]):
        """Create a named set of anomalies"""
        # Validate all anomaly IDs exist
        for anomaly_id in anomaly_ids:
            if anomaly_id not in self.anomalies:
                raise ValueError(f"Anomaly {anomaly_id} not found in registry")
        
        self.anomaly_sets[set_name] = anomaly_ids
    
    def get_anomaly_set(self, set_name: str) -> List[BaseAnomaly]:
        """Get list of anomaly objects for a named set"""
        if set_name not in self.anomaly_sets:
            return []
        
        return [self.anomalies[aid] for aid in self.anomaly_sets[set_name] 
                if aid in self.anomalies]
    
    def get_active_anomalies_for_context(self, context: Dict[str, Any]) -> List[BaseAnomaly]:
        """Determine which anomalies should be active based on context"""
        active_anomalies = []
        
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
    
    def add_context_rule(self, rule_func: Callable):
        """Add a function that determines active anomalies based on context"""
        self.context_rules.append(rule_func)
    
    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get statistics about registered anomalies"""
        return {
            "total_anomalies": len(self.anomalies),
            "anomaly_sets": len(self.anomaly_sets),
            "context_rules": len(self.context_rules),
            "by_severity": self._group_by_severity()
        }
    
    def _group_by_severity(self) -> Dict[str, int]:
        """Group anomalies by severity level"""
        groups = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for anomaly in self.anomalies.values():
            if anomaly.severity < 0.3:
                groups["low"] += 1
            elif anomaly.severity < 0.6:
                groups["medium"] += 1
            elif anomaly.severity < 0.9:
                groups["high"] += 1
            else:
                groups["critical"] += 1
        return groups

# Global registry instance
anomaly_registry = AnomalyRegistry()
```

### **1.3 Language Integration**

**Goal**: Integrate anomaly system with Grimoire interpreter

**Files to Modify**:

- `grimoire/lexer.py` - Add anomaly keywords
- `grimoire/parser.py` - Parse anomaly definitions
- `grimoire/interpreter.py` - Execute anomaly operations

**Implementation**:

```python
# Add to grimoire/lexer.py
class TokenType(Enum):
    # ... existing tokens ...
    ANOMALY = "ANOMALY"
    DETECT = "DETECT"
    ESCALATE = "ESCALATE"
    WATCH = "WATCH"
    SEVERITY = "SEVERITY"

# Add to keyword mapping
KEYWORDS = {
    # ... existing keywords ...
    "anomaly": TokenType.ANOMALY,
    "detect": TokenType.DETECT,
    "escalate": TokenType.ESCALATE,
    "watch": TokenType.WATCH,
    "severity": TokenType.SEVERITY,
}

# Add to grimoire/parser.py
def parse_anomaly_definition(self):
    """Parse anomaly artifact definition"""
    self.consume(TokenType.ANOMALY, "Expected 'anomaly'")
    name = self.consume(TokenType.IDENTIFIER, "Expected anomaly name").lexeme
    
    if self.match(TokenType.EXTENDS):
        base_class = self.consume(TokenType.IDENTIFIER, "Expected base class name").lexeme
    else:
        base_class = "BaseAnomaly"
    
    self.consume(TokenType.COLON, "Expected ':' after anomaly declaration")
    
    # Parse anomaly body (properties and methods)
    body = self.parse_block()
    
    return AnomalyDefinitionNode(name, base_class, body)

# Add to grimoire/interpreter.py
def execute_anomaly_definition(self, node):
    """Execute anomaly definition and register with system"""
    # Create anomaly class dynamically
    anomaly_class = self.create_anomaly_class(node)
    
    # Register with interpreter environment
    self.environment.define(node.name, anomaly_class)
    
    return anomaly_class

def builtin_create_anomaly(self, name, severity=0.5, description=""):
    """Built-in function to create anomaly instances"""
    # Implementation depends on specific anomaly type
    pass

def builtin_register_anomaly(self, anomaly):
    """Built-in function to register anomaly with global registry"""
    from grimoire.anomalies.registry import anomaly_registry
    return anomaly_registry.register_anomaly(anomaly)
```

## Phase 2: Agent Integration (Week 2-3)

### **2.1 Familiar Anomaly Detection Mixin**

**Goal**: Add anomaly detection capabilities to existing familiar system

**Files to Create/Modify**:

- `grimoire/familiars/anomaly_mixin.py` - Detection capabilities
- `grimoire/familiars/base.py` - Integrate mixin

**Implementation**:

```python
# grimoire/familiars/anomaly_mixin.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..anomalies.base import BaseAnomaly
from ..anomalies.registry import anomaly_registry

class AnomalyDetectorMixin:
    """Mixin to add anomaly detection capabilities to familiars"""
    
    def __init__(self):
        if not hasattr(self, 'watched_anomalies'):
            self.watched_anomalies: List[BaseAnomaly] = []
        if not hasattr(self, 'detection_log'):
            self.detection_log: List[Dict[str, Any]] = []
        if not hasattr(self, 'escalation_threshold'):
            self.escalation_threshold = 5  # Escalate after 5 detections
        
        # Add anomaly-specific sockets
        if hasattr(self, 'add_socket'):
            self.add_socket("anomaly_output")
            self.add_socket("escalation_output")
            self.add_socket("anomaly_config_input")
    
    def add_anomaly_watch(self, anomaly: BaseAnomaly):
        """Add an anomaly to watch for"""
        if anomaly not in self.watched_anomalies:
            self.watched_anomalies.append(anomaly)
    
    def remove_anomaly_watch(self, anomaly: BaseAnomaly):
        """Remove an anomaly from watch list"""
        if anomaly in self.watched_anomalies:
            self.watched_anomalies.remove(anomaly)
    
    def update_anomaly_watch_list(self, new_anomalies: List[BaseAnomaly]):
        """Replace entire watch list with new anomalies"""
        self.watched_anomalies = new_anomalies.copy()
    
    def scan_for_anomalies(self, entity, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check entity against all watched anomalies"""
        detected_anomalies = []
        
        # Get entity state
        if hasattr(entity, 'properties'):
            entity_state = entity.properties
        elif hasattr(entity, 'get_state'):
            entity_state = entity.get_state()
        else:
            entity_state = {"entity": entity}
        
        # Check each watched anomaly
        for anomaly in self.watched_anomalies:
            if not anomaly.enabled:
                continue
                
            try:
                if anomaly.detect(entity_state, world_state):
                    report = anomaly.report_detection(entity, world_state)
                    detected_anomalies.append(report)
                    self.detection_log.append(report)
                    
                    # Send via socket if available
                    if hasattr(self, 'send_to_socket'):
                        self.send_to_socket("anomaly_output", report)
                    
                    # Check for escalation
                    if anomaly.should_escalate():
                        self.escalate_anomaly(report)
                        
            except Exception as e:
                # Log error but don't break detection for other anomalies
                error_report = {
                    "error": "anomaly_detection_failed",
                    "anomaly": anomaly.name,
                    "exception": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.detection_log.append(error_report)
        
        return detected_anomalies
    
    def escalate_anomaly(self, report: Dict[str, Any]):
        """Send critical anomaly to higher-level agents"""
        escalation_report = {
            "type": "critical_anomaly",
            "original_report": report,
            "escalation_level": "immediate",
            "escalated_by": getattr(self, 'name', 'unknown_familiar'),
            "escalation_time": datetime.now().isoformat()
        }
        
        if hasattr(self, 'send_to_socket'):
            self.send_to_socket("escalation_output", escalation_report)
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of detection activity"""
        total_detections = len(self.detection_log)
        by_anomaly = {}
        recent_detections = []
        
        # Count detections by anomaly type
        for detection in self.detection_log:
            anomaly_type = detection.get("anomaly_type", "unknown")
            by_anomaly[anomaly_type] = by_anomaly.get(anomaly_type, 0) + 1
            
            # Keep recent detections (last 24 hours)
            detection_time = datetime.fromisoformat(detection["timestamp"])
            if (datetime.now() - detection_time).total_seconds() < 86400:
                recent_detections.append(detection)
        
        return {
            "total_detections": total_detections,
            "detections_by_type": by_anomaly,
            "recent_detections": len(recent_detections),
            "watched_anomalies": len(self.watched_anomalies),
            "last_detection": self.detection_log[-1]["timestamp"] if self.detection_log else None
        }
    
    def configure_from_context(self, context: Dict[str, Any]):
        """Configure anomaly detection based on context"""
        active_anomalies = anomaly_registry.get_active_anomalies_for_context(context)
        self.update_anomaly_watch_list(active_anomalies)

# Modify grimoire/familiars/base.py
from .anomaly_mixin import AnomalyDetectorMixin

class GrimoireFamiliar(AnomalyDetectorMixin):
    def __init__(self, name, familiar_type=None):
        # Initialize base functionality
        self.name = name
        self.familiar_type = familiar_type
        self.sockets = {}
        self.pacts = []
        
        # Initialize anomaly detection mixin
        AnomalyDetectorMixin.__init__(self)
    
    # ... rest of existing familiar functionality ...
    
    def process_entity(self, entity, world_state):
        """Process entity and check for anomalies"""
        # Do normal processing
        result = self.normal_processing(entity, world_state)
        
        # Check for anomalies during processing
        detected_anomalies = self.scan_for_anomalies(entity, world_state)
        
        if detected_anomalies:
            # Log or handle detected anomalies
            for anomaly in detected_anomalies:
                self.handle_detected_anomaly(anomaly)
        
        return result
```

### **2.2 Hierarchical Anomaly Reporting**

**Goal**: Integrate anomaly detection with existing agent hierarchy

**Implementation**:

```python
# grimoire/agents/anomaly_integration.py
class AnomalyAwareAgent:
    """Base class for agents that handle anomaly reports"""
    
    def __init__(self):
        self.anomaly_reports = []
        self.escalation_rules = []
        
    def receive_anomaly_report(self, report: Dict[str, Any]):
        """Handle incoming anomaly report"""
        self.anomaly_reports.append(report)
        
        # Check escalation rules
        for rule in self.escalation_rules:
            if rule.should_escalate(report, self.anomaly_reports):
                self.escalate_to_superior(report)
                break
    
    def add_escalation_rule(self, rule):
        """Add rule for when to escalate anomalies"""
        self.escalation_rules.append(rule)
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get summary of handled anomalies"""
        return {
            "total_reports": len(self.anomaly_reports),
            "recent_reports": len([r for r in self.anomaly_reports 
                                 if self._is_recent(r["timestamp"])]),
            "severity_distribution": self._group_by_severity()
        }

# Extend existing agent classes
class AnomalyAwareArchon(Archon, AnomalyAwareAgent):
    def __init__(self, name, domain, goals):
        Archon.__init__(self, name, domain, goals)
        AnomalyAwareAgent.__init__(self)
        
        # Add anomaly management goals
        self.add_goal(AnomalyManagementGoal("maintain_system_health", 0.7))

class AnomalyAwareSpirit(Spirit, AnomalyAwareAgent):
    def __init__(self, name, domain, domain_authority):
        Spirit.__init__(self, name, domain, domain_authority)
        AnomalyAwareAgent.__init__(self)
        
        # Configure domain-specific anomalies
        self.configure_domain_anomalies(domain)
```

## Phase 3: Predefined Anomaly Library (Week 3-4)

### **3.1 Game Development Anomalies**

**Goal**: Create common anomaly types for game development

**Files to Create**:

- `grimoire/anomalies/game.py` - Game-specific anomalies
- `grimoire/anomalies/examples.py` - Usage examples

**Implementation**:

```python
# grimoire/anomalies/game.py
from .base import BaseAnomaly
from typing import Dict, Any

class UndeadEntityAnomaly(BaseAnomaly):
    """Detect entities with negative health that are still active"""
    
    def __init__(self):
        super().__init__(
            name="undead_entity",
            severity=0.9,
            description="Entity with negative health still active"
        )
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        health = entity_state.get("health", 1)
        is_active = entity_state.get("active", False)
        return health <= 0 and is_active

class ResourceLeakAnomaly(BaseAnomaly):
    """Detect entities consuming resources without producing value"""
    
    def __init__(self, max_idle_time: int = 300):
        super().__init__(
            name="resource_leak",
            severity=0.7,
            description="Entity consuming resources without producing value"
        )
        self.max_idle_time = max_idle_time
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        resource_usage = entity_state.get("resource_usage", 0)
        value_produced = entity_state.get("value_generated", 0)
        idle_time = entity_state.get("idle_time", 0)
        
        return (resource_usage > 0 and 
                value_produced == 0 and 
                idle_time > self.max_idle_time)

class CheatDetectionAnomaly(BaseAnomaly):
    """Detect suspicious player behavior patterns"""
    
    def __init__(self):
        super().__init__(
            name="cheat_detection",
            severity=0.8,
            description="Player behavior suggests cheating or exploits"
        )
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        actions_per_second = entity_state.get("action_rate", 0)
        impossible_movements = entity_state.get("teleport_count", 0)
        resource_gain_rate = entity_state.get("resource_acceleration", 0)
        
        # Multiple suspicious indicators
        suspicious_factors = 0
        if actions_per_second > 20:
            suspicious_factors += 1
        if impossible_movements > 0:
            suspicious_factors += 1
        if resource_gain_rate > 1000:
            suspicious_factors += 1
            
        return suspicious_factors >= 2

class PerformanceAnomaly(BaseAnomaly):
    """Detect performance issues in game entities"""
    
    def __init__(self, response_threshold: float = 1000.0):
        super().__init__(
            name="performance_issue",
            severity=0.6,
            description="Entity response time exceeds threshold"
        )
        self.response_threshold = response_threshold
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        response_time = entity_state.get("last_response_time", 0)
        return response_time > self.response_threshold
    
    def configure_for_environment(self, environment: str):
        """Adjust thresholds based on environment"""
        if environment == "production":
            self.response_threshold = 500.0
            self.severity = 0.9
        elif environment == "testing":
            self.response_threshold = 2000.0
            self.severity = 0.3
        elif environment == "development":
            self.response_threshold = 5000.0
            self.severity = 0.1
```

### **3.2 Business Application Anomalies**

```python
# grimoire/anomalies/business.py
class NegativeBalanceAnomaly(BaseAnomaly):
    """Detect accounts with negative balances beyond limits"""
    
    def __init__(self):
        super().__init__(
            name="negative_balance",
            severity=0.8,
            description="Account balance below acceptable threshold"
        )
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        balance = entity_state.get("balance", 0)
        account_type = entity_state.get("account_type", "checking")
        
        # Different thresholds for different account types
        if account_type == "checking" and balance < -100:
            return True
        elif account_type == "credit" and balance < -10000:
            return True
        elif account_type == "savings" and balance < 0:
            return True
        
        return False

class StagnantInvestmentAnomaly(BaseAnomaly):
    """Detect investments with no growth over extended periods"""
    
    def __init__(self, min_days: int = 90):
        super().__init__(
            name="stagnant_investment",
            severity=0.6,
            description="Investment with no growth over extended period"
        )
        self.min_days = min_days
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        initial_value = entity_state.get("initial_investment", 0)
        current_value = entity_state.get("current_value", 0)
        days_held = entity_state.get("days_since_purchase", 0)
        
        return (days_held > self.min_days and 
                current_value <= initial_value and
                initial_value > 0)

class FraudIndicatorAnomaly(BaseAnomaly):
    """Detect patterns that might indicate fraudulent activity"""
    
    def __init__(self):
        super().__init__(
            name="fraud_indicator",
            severity=0.9,
            description="Transaction pattern suggests possible fraud"
        )
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        transaction_amount = entity_state.get("amount", 0)
        account_age = entity_state.get("days_since_opened", 0)
        recent_deposits = entity_state.get("recent_deposit_count", 0)
        transaction_hour = entity_state.get("transaction_hour", 12)
        
        # Multi-factor fraud detection
        risk_factors = 0
        
        if transaction_amount > 10000 and account_age < 30:
            risk_factors += 1
        if recent_deposits > 5 and account_age < 7:
            risk_factors += 1
        if transaction_hour < 6 or transaction_hour > 22:
            risk_factors += 1
        if transaction_amount > entity_state.get("average_transaction", 0) * 10:
            risk_factors += 1
            
        return risk_factors >= 2
```

## Phase 4: Context-Aware Anomaly Management (Week 4-5)

### **4.1 Dynamic Anomaly Sets**

**Goal**: Implement context-based anomaly activation

**Files to Create**:

- `grimoire/anomalies/context.py` - Context management
- `grimoire/anomalies/sets.py` - Anomaly set definitions

**Implementation**:
```python
# grimoire/anomalies/context.py
from typing import Dict, Any, List, Callable
from datetime import datetime
from .base import BaseAnomaly
from .registry import anomaly_registry

class ContextManager:
    """Manages context-aware anomaly activation"""
    
    def __init__(self):
        self.context_rules: List[Callable] = []
        self.current_context: Dict[str, Any] = {}
        
    def update_context(self, new_context: Dict[str, Any]):
        """Update current context and notify agents"""
        self.current_context.update(new_context)
        self.notify_context_change()
    
    def add_context_rule(self, rule_func: Callable):
        """Add function that determines active anomalies based on context"""
        self.context_rules.append(rule_func)
    
    def get_active_anomalies(self) -> List[BaseAnomaly]:
        """Get list of anomalies that should be active in current context"""
        active_anomalies = []
        
        for rule in self.context_rules:
            try:
                rule_anomalies = rule(self.current_context, anomaly_registry)
                if rule_anomalies:
                    active_anomalies.extend(rule_anomalies)
            except Exception as e:
                print(f"Error in context rule: {e}")
        
        return self._deduplicate_anomalies(active_anomalies)
    
    def _deduplicate_anomalies(self, anomalies: List[BaseAnomaly]) -> List[BaseAnomaly]:
        """Remove duplicate anomalies while preserving order"""
        seen = set()
        unique = []
        for anomaly in anomalies:
            if anomaly.anomaly_id not in seen:
                seen.add(anomaly.anomaly_id)
                unique.append(anomaly)
        return unique
    
    def notify_context_change(self):
        """Notify all registered agents of context change"""
        active_anomalies = self.get_active_anomalies()
        # Implementation depends on agent communication system
        pass

# Context rule examples
def game_mode_context_rule(context: Dict[str, Any], registry) -> List[BaseAnomaly]:
   """Select anomalies based on game mode"""
   game_mode = context.get("game_mode", "normal")
   
   if game_mode == "pvp":
       return registry.get_anomaly_set("pvp_anomalies")
   elif game_mode == "pve":
       return registry.get_anomaly_set("pve_anomalies")
   elif game_mode == "maintenance":
       return registry.get_anomaly_set("maintenance_anomalies")
   else:
       return registry.get_anomaly_set("default_anomalies")

def time_based_context_rule(context: Dict[str, Any], registry) -> List[BaseAnomaly]:
   """Select anomalies based on time of day and day of week"""
   current_time = datetime.now()
   hour = current_time.hour
   day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
   
   if day_of_week >= 5:  # Weekend
       return registry.get_anomaly_set("weekend_anomalies")
   elif 9 <= hour <= 17:  # Business hours
       return registry.get_anomaly_set("business_hours_anomalies")
   else:  # Off hours
       return registry.get_anomaly_set("off_hours_anomalies")

def system_load_context_rule(context: Dict[str, Any], registry) -> List[BaseAnomaly]:
   """Adjust anomaly detection based on system load"""
   cpu_usage = context.get("cpu_usage", 0.5)
   memory_usage = context.get("memory_usage", 0.5)
   
   if cpu_usage > 0.8 or memory_usage > 0.8:
       # High load - only critical anomalies
       return registry.get_anomaly_set("critical_only_anomalies")
   else:
       # Normal load - all anomalies
       return registry.get_anomaly_set("full_anomalies")

def business_period_context_rule(context: Dict[str, Any], registry) -> List[BaseAnomaly]:
   """Select anomalies based on business period (month-end, audit, etc.)"""
   business_period = context.get("business_period", "normal")
   
   if business_period == "month_end":
       return registry.get_anomaly_set("month_end_anomalies")
   elif business_period == "audit_prep":
       return registry.get_anomaly_set("audit_anomalies")
   elif business_period == "year_end":
       return registry.get_anomaly_set("year_end_anomalies")
   else:
       return registry.get_anomaly_set("normal_business_anomalies")

# grimoire/anomalies/sets.py
from .game import UndeadEntityAnomaly, ResourceLeakAnomaly, CheatDetectionAnomaly, PerformanceAnomaly
from .business import NegativeBalanceAnomaly, StagnantInvestmentAnomaly, FraudIndicatorAnomaly
from .registry import anomaly_registry

def initialize_default_anomaly_sets():
   """Initialize predefined anomaly sets"""
   
   # Game anomaly sets
   pvp_anomalies = [
       CheatDetectionAnomaly(),
       PerformanceAnomaly(),
       UndeadEntityAnomaly()
   ]
   
   pve_anomalies = [
       ResourceLeakAnomaly(),
       PerformanceAnomaly(),
       UndeadEntityAnomaly()
   ]
   
   maintenance_anomalies = [
       ResourceLeakAnomaly(max_idle_time=60),  # Stricter during maintenance
       PerformanceAnomaly(response_threshold=500.0)
   ]
   
   # Business anomaly sets
   normal_business_anomalies = [
       NegativeBalanceAnomaly(),
       FraudIndicatorAnomaly()
   ]
   
   month_end_anomalies = [
       NegativeBalanceAnomaly(),
       StagnantInvestmentAnomaly(min_days=30),  # More aggressive at month-end
       FraudIndicatorAnomaly()
   ]
   
   audit_anomalies = [
       NegativeBalanceAnomaly(),
       StagnantInvestmentAnomaly(),
       FraudIndicatorAnomaly()
   ]
   
   # Register all anomalies
   all_anomalies = (pvp_anomalies + pve_anomalies + maintenance_anomalies + 
                   normal_business_anomalies + month_end_anomalies + audit_anomalies)
   
   for anomaly in all_anomalies:
       anomaly_registry.register_anomaly(anomaly)
   
   # Create anomaly sets
   anomaly_registry.create_anomaly_set("pvp_anomalies", [a.anomaly_id for a in pvp_anomalies])
   anomaly_registry.create_anomaly_set("pve_anomalies", [a.anomaly_id for a in pve_anomalies])
   anomaly_registry.create_anomaly_set("maintenance_anomalies", [a.anomaly_id for a in maintenance_anomalies])
   anomaly_registry.create_anomaly_set("normal_business_anomalies", [a.anomaly_id for a in normal_business_anomalies])
   anomaly_registry.create_anomaly_set("month_end_anomalies", [a.anomaly_id for a in month_end_anomalies])
   anomaly_registry.create_anomaly_set("audit_anomalies", [a.anomaly_id for a in audit_anomalies])
```

### **4.2 Adaptive Anomaly Management**

```python
# grimoire/anomalies/adaptive.py
from typing import Dict, Any, List
import threading
import time
from .context import ContextManager
from .registry import anomaly_registry

class AdaptiveAnomalyManager:
    """Manages dynamic anomaly activation based on changing conditions"""
    
    def __init__(self, update_interval: int = 60):
        self.context_manager = ContextManager()
        self.update_interval = update_interval
        self.running = False
        self.update_thread = None
        self.registered_agents = []
        
    def start(self):
        """Start adaptive management"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def stop(self):
        """Stop adaptive management"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
    
    def register_agent(self, agent):
        """Register agent to receive anomaly updates"""
        if hasattr(agent, 'update_anomaly_watch_list'):
            self.registered_agents.append(agent)
    
    def _update_loop(self):
        """Main update loop that monitors context and adjusts anomalies"""
        while self.running:
            try:
                # Gather current context
                current_context = self._gather_context()
                
                # Update context manager
                self.context_manager.update_context(current_context)
                
                # Get active anomalies for current context
                active_anomalies = self.context_manager.get_active_anomalies()
                
                # Update all registered agents
                for agent in self.registered_agents:
                    try:
                        agent.update_anomaly_watch_list(active_anomalies)
                    except Exception as e:
                        print(f"Error updating agent {getattr(agent, 'name', 'unknown')}: {e}")
                
                # Sleep until next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in adaptive anomaly update loop: {e}")
                time.sleep(self.update_interval)
    
    def _gather_context(self) -> Dict[str, Any]:
        """Gather current system context"""
        context = {}
        
        # Time-based context
        current_time = time.time()
        context['timestamp'] = current_time
        context['hour'] = time.localtime(current_time).tm_hour
        context['day_of_week'] = time.localtime(current_time).tm_wday
        
        # System resource context
        try:
            import psutil
            context['cpu_usage'] = psutil.cpu_percent(interval=1) / 100.0
            context['memory_usage'] = psutil.virtual_memory().percent / 100.0
            context['disk_usage'] = psutil.disk_usage('/').percent / 100.0
        except ImportError:
            # Fallback if psutil not available
            context['cpu_usage'] = 0.5
            context['memory_usage'] = 0.5
            context['disk_usage'] = 0.5
        
        # Application-specific context (to be customized)
        context.update(self._get_application_context())
        
        return context
    
    def _get_application_context(self) -> Dict[str, Any]:
        """Get application-specific context - override in subclasses"""
        return {}

class GameAdaptiveManager(AdaptiveAnomalyManager):
    """Adaptive manager specialized for game applications"""
    
    def _get_application_context(self) -> Dict[str, Any]:
        context = {}
        
        # Game-specific context gathering
        # This would integrate with your game engine
        context['player_count'] = self._get_current_player_count()
        context['game_mode'] = self._get_current_game_mode()
        context['server_load'] = self._get_server_load()
        
        return context
    
    def _get_current_player_count(self) -> int:
        # Implementation depends on game engine
        return 0
    
    def _get_current_game_mode(self) -> str:
        # Implementation depends on game engine
        return "normal"
    
    def _get_server_load(self) -> float:
        # Implementation depends on game engine
        return 0.5

class BusinessAdaptiveManager(AdaptiveAnomalyManager):
    """Adaptive manager specialized for business applications"""
    
    def _get_application_context(self) -> Dict[str, Any]:
        context = {}
        
        # Business-specific context
        context['business_period'] = self._get_business_period()
        context['transaction_volume'] = self._get_transaction_volume()
        context['system_maintenance'] = self._is_maintenance_window()
        
        return context
    
    def _get_business_period(self) -> str:
        # Determine if it's month-end, quarter-end, year-end, etc.
        current_time = time.localtime()
        day = current_time.tm_mday
        month = current_time.tm_mon
        
        if day >= 28:  # Last few days of month
            return "month_end"
        elif month in [3, 6, 9, 12] and day >= 25:
            return "quarter_end"
        elif month == 12 and day >= 20:
            return "year_end"
        else:
            return "normal"
    
    def _get_transaction_volume(self) -> float:
        # Implementation depends on business system
        return 1.0
    
    def _is_maintenance_window(self) -> bool:
        # Implementation depends on business system
        current_hour = time.localtime().tm_hour
        return 2 <= current_hour <= 6  # Typical maintenance window
```

## Phase 5: Integration and Testing (Week 5-6)

### **5.1 Complete Integration Example**

**Goal**: Demonstrate full anomaly system working with agent hierarchy

**Files to Create**:

- `grimoire/examples/anomaly_demo.py` - Complete working example
- `grimoire/examples/anomaly_demo.grim` - Grimoire language example

**Implementation**:
```python
# grimoire/examples/anomaly_demo.py
from grimoire.anomalies.registry import anomaly_registry
from grimoire.anomalies.game import UndeadEntityAnomaly, ResourceLeakAnomaly, CheatDetectionAnomaly
from grimoire.anomalies.business import NegativeBalanceAnomaly, FraudIndicatorAnomaly
from grimoire.anomalies.adaptive import GameAdaptiveManager
from grimoire.familiars.entity_familiar import EntityFamiliar
from grimoire.familiars.ai_familiar import AIFamiliar
from grimoire.agents.archon import Archon
from grimoire.agents.spirit import Spirit

def setup_anomaly_demo():
    """Complete anomaly detection system demonstration"""
    
    print("🔮 Grimoire Anomaly Detection System Demo")
    print("=" * 50)
    
    # 1. Create and register anomalies
    print("\n📋 Creating anomaly definitions...")
    
    undead_anomaly = UndeadEntityAnomaly()
    resource_leak_anomaly = ResourceLeakAnomaly(max_idle_time=120)
    cheat_anomaly = CheatDetectionAnomaly()
    balance_anomaly = NegativeBalanceAnomaly()
    fraud_anomaly = FraudIndicatorAnomaly()
    
    # Register with global registry
    for anomaly in [undead_anomaly, resource_leak_anomaly, cheat_anomaly, 
                   balance_anomaly, fraud_anomaly]:
        anomaly_registry.register_anomaly(anomaly)
    
    print(f"✅ Registered {len(anomaly_registry.anomalies)} anomalies")
    
    # 2. Create entity familiars with test data
    print("\n🎮 Creating test entities...")
    
    # Game entities
    player_entity = EntityFamiliar("Player1", {
        "health": -10,  # ANOMALY: Negative health
        "active": True,
        "resource_usage": 15,
        "value_generated": 0,
        "idle_time": 300,  # ANOMALY: Resource leak
        "action_rate": 25,  # ANOMALY: Suspicious activity
        "teleport_count": 3
    })
    
    npc_entity = EntityFamiliar("Goblin1", {
        "health": 100,
        "active": True,
        "resource_usage": 2,
        "value_generated": 10,
        "idle_time": 30
    })
    
    # Business entities
    customer_account = EntityFamiliar("Customer123", {
        "balance": -500,  # ANOMALY: Negative balance
        "account_type": "checking",
        "amount": 15000,  # ANOMALY: Large transaction
        "days_since_opened": 5,  # ANOMALY: New account
        "recent_deposit_count": 8,
        "transaction_hour": 3,  # ANOMALY: Odd hours
        "average_transaction": 200
    })
    
    entities = [player_entity, npc_entity, customer_account]
    
    # 3. Create monitoring familiars
    print("\n👁️ Creating monitoring agents...")
    
    game_monitor = EntityFamiliar("GameMonitor", {})
    game_monitor.add_anomaly_watch(undead_anomaly)
    game_monitor.add_anomaly_watch(resource_leak_anomaly)
    game_monitor.add_anomaly_watch(cheat_anomaly)
    
    business_monitor = EntityFamiliar("BusinessMonitor", {})
    business_monitor.add_anomaly_watch(balance_anomaly)
    business_monitor.add_anomaly_watch(fraud_anomaly)
    
    # 4. Create agent hierarchy
    print("\n🏛️ Creating agent hierarchy...")
    
    # Archon - strategic level
    security_archon = Archon("SecurityArchon", "Security", ["maintain_system_integrity"])
    
    # Spirits - tactical level  
    game_security_spirit = Spirit("GameSecurity", "GameMonitoring", "game_security")
    business_security_spirit = Spirit("BusinessSecurity", "FinanceMonitoring", "finance_security")
    
    # Connect hierarchy (simplified)
    security_archon.managed_spirits = [game_security_spirit, business_security_spirit]
    game_security_spirit.managed_familiars = [game_monitor]
    business_security_spirit.managed_familiars = [business_monitor]
    
    # 5. Run anomaly detection simulation
    print("\n🔍 Running anomaly detection...")
    
    world_state = {
        "timestamp": "2024-01-15T14:30:00",
        "system_load": 0.6,
        "total_entities": len(entities)
    }
    
    # Process each entity through monitoring familiars
    total_anomalies = 0
    for entity in entities:
        print(f"\n  Processing {entity.name}...")
        
        # Game monitor checks game entities
        if entity.name.startswith(("Player", "Goblin")):
            anomalies = game_monitor.scan_for_anomalies(entity, world_state)
            if anomalies:
                print(f"    🚨 Game anomalies detected: {len(anomalies)}")
                for anomaly in anomalies:
                    print(f"      - {anomaly['anomaly_type']}: {anomaly.get('severity', 'unknown')} severity")
                total_anomalies += len(anomalies)
        
        # Business monitor checks business entities  
        if entity.name.startswith("Customer"):
            anomalies = business_monitor.scan_for_anomalies(entity, world_state)
            if anomalies:
                print(f"    🚨 Business anomalies detected: {len(anomalies)}")
                for anomaly in anomalies:
                    print(f"      - {anomaly['anomaly_type']}: {anomaly.get('severity', 'unknown')} severity")
                total_anomalies += len(anomalies)
    
    # 6. Show detection summary
    print(f"\n📊 Detection Summary:")
    print(f"   Total entities processed: {len(entities)}")
    print(f"   Total anomalies detected: {total_anomalies}")
    print(f"   Game monitor detections: {len(game_monitor.detection_log)}")
    print(f"   Business monitor detections: {len(business_monitor.detection_log)}")
    
    # 7. Show agent hierarchy response
    print(f"\n🏛️ Agent Hierarchy Response:")
    
    # Spirits aggregate reports
    game_spirit_summary = {
        "domain": game_security_spirit.domain,
        "familiars_managed": len(game_security_spirit.managed_familiars),
        "anomalies_reported": len(game_monitor.detection_log)
    }
    
    business_spirit_summary = {
        "domain": business_security_spirit.domain, 
        "familiars_managed": len(business_security_spirit.managed_familiars),
        "anomalies_reported": len(business_monitor.detection_log)
    }
    
    print(f"   Game Security Spirit: {game_spirit_summary}")
    print(f"   Business Security Spirit: {business_spirit_summary}")
    
    # Archon strategic overview
    archon_summary = {
        "total_spirits": len(security_archon.managed_spirits),
        "total_anomalies": total_anomalies,
        "security_status": "ALERT" if total_anomalies > 5 else "NORMAL"
    }
    
    print(f"   Security Archon: {archon_summary}")
    
    # 8. Demonstrate adaptive management
    print(f"\n🔄 Adaptive Management Demo:")
    
    adaptive_manager = GameAdaptiveManager(update_interval=5)
    adaptive_manager.register_agent(game_monitor)
    adaptive_manager.register_agent(business_monitor)
    
    print("   Started adaptive anomaly manager")
    print("   Anomalies will be automatically adjusted based on context")
    
    return {
        "entities": entities,
        "monitors": [game_monitor, business_monitor],
        "spirits": [game_security_spirit, business_security_spirit],
        "archon": security_archon,
        "adaptive_manager": adaptive_manager,
        "total_anomalies": total_anomalies
    }

if __name__ == "__main__":
    demo_results = setup_anomaly_demo()
    print("\n✨ Anomaly detection system demo completed!")
    print("🔮 The magical sentries are now watching for anomalies...")
```

### **5.2 Grimoire Language Integration Example**
```grimoire
# grimoire/examples/anomaly_demo.grim
# Complete Grimoire Anomaly Detection System Example

ritual main():
    scry $SCROLL(🔮 Grimoire Anomaly Detection Demo)
    scry $SCROLL(=====================================)
    
    # Create custom anomaly definitions
    anomaly HealthViolationAnomaly extends BaseAnomaly:
        bind name = $SCROLL(health_violation)
        bind severity = 0.9
        bind description = $SCROLL(Entity health below safe threshold)
        
        ritual detect(entity_state, world_state):
            bind health = entity_state.get_property($SCROLL(health))
            bind max_health = entity_state.get_property($SCROLL(max_health))
            
            # Detect entities with health below 10% of maximum
            if max_health > 0:
                bind health_percentage = health divided by max_health
                return health_percentage < 0.1
            return false
    
    anomaly SuspiciousTransactionAnomaly extends BaseAnomaly:
        bind name = $SCROLL(suspicious_transaction)
        bind severity = 0.8
        bind description = $SCROLL(Transaction pattern suggests fraud)
        
        ritual detect(entity_state, world_state):
            bind amount = entity_state.get_property($SCROLL(transaction_amount))
            bind account_age = entity_state.get_property($SCROLL(account_age_days))
            bind hour = entity_state.get_property($SCROLL(transaction_hour))
            
            # Multiple risk factors
            bind risk_score = 0
            
            if amount > 5000 and account_age < 30:
                risk_score = risk_score added to 1
            if hour < 6 or hour > 22:
                risk_score = risk_score added to 1
            if amount > entity_state.get_property($SCROLL(avg_transaction)) multiplied by 10:
                risk_score = risk_score added to 1
                
            return risk_score >= 2
    
    # Create anomaly instances
    bind health_anomaly = conjure HealthViolationAnomaly upon
    bind transaction_anomaly = conjure SuspiciousTransactionAnomaly upon
    
    # Register anomalies
    register_anomaly upon health_anomaly
    register_anomaly upon transaction_anomaly
    
    # Create test entities
    bind player = create_entity_familiar upon $SCROLL(TestPlayer), {
        health: 5,
        max_health: 100,
        active: true
    }
    
    bind customer = create_entity_familiar upon $SCROLL(TestCustomer), {
        transaction_amount: 25000,
        account_age_days: 7,
        transaction_hour: 3,
        avg_transaction: 500
    }
    
    # Create monitoring familiars with anomaly detection
    bind game_monitor = create_entity_familiar upon $SCROLL(GameMonitor), {}
    bind finance_monitor = create_entity_familiar upon $SCROLL(FinanceMonitor), {}
    
    # Assign anomalies to monitors
    game_monitor.add_anomaly_watch(health_anomaly)
    finance_monitor.add_anomaly_watch(transaction_anomaly)
    
    # Create agent hierarchy
    bind security_archon = create_archon upon $SCROLL(SecurityChief), $SCROLL(Security)
    bind game_spirit = create_spirit upon $SCROLL(GameSecurity), $SCROLL(GameMonitoring), $SCROLL(game_security)
    bind finance_spirit = create_spirit upon $SCROLL(FinanceSecurity), $SCROLL(FinanceMonitoring), $SCROLL(finance_security)
    
    # Assign familiars to spirits via pacts
    bind game_monitor_pact = create_familiar_with_pact upon game_spirit, $SCROLL(GameMonitor), [
        $SCROLL(monitor_entities), $SCROLL(detect_anomalies), $SCROLL(report_violations)
    ]
    
    bind finance_monitor_pact = create_familiar_with_pact upon finance_spirit, $SCROLL(FinanceMonitor), [
        $SCROLL(monitor_transactions), $SCROLL(detect_anomalies), $SCROLL(report_violations)
    ]
    
    # Set up socket communication for anomaly reporting
    connect_socket upon game_monitor.anomaly_output, game_spirit.anomaly_input
    connect_socket upon finance_monitor.anomaly_output, finance_spirit.anomaly_input
    connect_socket upon game_spirit.escalation_output, security_archon.threat_input
    connect_socket upon finance_spirit.escalation_output, security_archon.threat_input
    
    # Simulate anomaly detection
    scry $SCROLL()
    scry $SCROLL(🔍 Running anomaly detection...)
    
    bind world_state = {
        timestamp: get_current_time upon,
        system_load: 0.6,
        active_monitoring: true
    }
    
    # Process entities through monitors
    bind game_anomalies = game_monitor.scan_for_anomalies(player, world_state)
    bind finance_anomalies = finance_monitor.scan_for_anomalies(customer, world_state)
    
    # Report results
    scry $SCROLL()
    scry $SCROLL(📊 Detection Results:)
    scry $SCROLL(Game anomalies detected: ) added to game_anomalies.length
    scry $SCROLL(Finance anomalies detected: ) added to finance_anomalies.length
    
    # Show anomaly details
    if game_anomalies.length > 0:
        scry $SCROLL()
        scry $SCROLL(🚨 Game Anomalies:)
        for anomaly in game_anomalies:
            scry $SCROLL(  - ) added to anomaly.anomaly_type added to $SCROLL( (severity: ) added to anomaly.severity added to $SCROLL())
    
    if finance_anomalies.length > 0:
        scry $SCROLL()
        scry $SCROLL(🚨 Finance Anomalies:)
        for anomaly in finance_anomalies:
            scry $SCROLL(  - ) added to anomaly.anomaly_type added to $SCROLL( (severity: ) added to anomaly.severity added to $SCROLL())
    
    # Demonstrate context-aware anomaly switching
    scry $SCROLL()
    scry $SCROLL(🔄 Testing context-aware anomaly management...)
    
    # Change context (e.g., switching to maintenance mode)
    bind maintenance_context = {
        mode: $SCROLL(maintenance),
        priority_level: $SCROLL(high),
        monitoring_intensity: $SCROLL(critical_only)
    }
    
    # Update monitoring based on context
    configure_monitoring_for_context upon maintenance_context
    
    scry $SCROLL(✅ Anomaly detection system configured for maintenance mode)
    scry $SCROLL()
    scry $SCROLL(🔮 Anomaly detection demo completed!)
    scry $SCROLL(The magical sentries are now vigilant...)

# Run the demonstration
main upon
```

### **5.3 Testing Framework

```python
# grimoire/tests/test_anomaly_system.py
import unittest
from grimoire.anomalies.base import BaseAnomaly, CompositeAnomaly, AdaptiveAnomaly
from grimoire.anomalies.registry import AnomalyRegistry
from grimoire.anomalies.game import UndeadEntityAnomaly, ResourceLeakAnomaly
from grimoire.familiars.entity_familiar import EntityFamiliar

class TestAnomalySystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = AnomalyRegistry()
        self.test_entities = self.create_test_entities()
        self.world_state = {"timestamp": "2024-01-15T10:00:00", "system_load": 0.5}
    
    def create_test_entities(self):
        """Create test entities with various states"""
        return {
            "healthy_entity": EntityFamiliar("HealthyEntity", {
                "health": 100, "active": True, "resource_usage": 5, "value_generated": 10
            }),
            "dead_entity": EntityFamiliar("DeadEntity", {
                "health": -10, "active": True, "resource_usage": 0, "value_generated": 0
            }),
            "leaking_entity": EntityFamiliar("LeakingEntity", {
                "health": 50, "active": True, "resource_usage": 15, "value_generated": 0, "idle_time": 400
            })
        }
    
    def test_undead_anomaly_detection(self):
        """Test detection of entities with negative health"""
        anomaly = UndeadEntityAnomaly()
        
        # Healthy entity should not trigger
        self.assertFalse(anomaly.detect(
            self.test_entities["healthy_entity"].properties, 
            self.world_state
        ))
        
        # Dead but active entity should trigger
        self.assertTrue(anomaly.detect(
            self.test_entities["dead_entity"].properties, 
            self.world_state
        ))
    
    def test_resource_leak_detection(self):
        """Test detection of resource leaking entities"""
        anomaly = ResourceLeakAnomaly(max_idle_time=300)
        
        # Healthy entity should not trigger
        self.assertFalse(anomaly.detect(
            self.test_entities["healthy_entity"].properties, 
            self.world_state
        ))
        
        # Leaking entity should trigger
        self.assertTrue(anomaly.detect(
            self.test_entities["leaking_entity"].properties, 
            self.world_state
        ))
    
    def test_composite_anomaly(self):
        """Test composite anomaly that requires multiple conditions"""
        sub_anomaly1 = UndeadEntityAnomaly()
        sub_anomaly2 = ResourceLeakAnomaly(max_idle_time=300)
        
        # Composite requiring both anomalies
        composite = CompositeAnomaly(
            "critical_failure", 
            [sub_anomaly1, sub_anomaly2], 
            threshold=2
        )
        
        # Single anomaly should not trigger composite
        self.assertFalse(composite.detect(
            self.test_entities["dead_entity"].properties, 
            self.world_state
        ))
        
        # Entity with both conditions should trigger
        multi_problem_entity = EntityFamiliar("MultiProblem", {
            "health": -5, "active": True, "resource_usage": 10, 
            "value_generated": 0, "idle_time": 500
        })
        
        self.assertTrue(composite.detect(
            multi_problem_entity.properties, 
            self.world_state
        ))
    
    def test_adaptive_anomaly_learning(self):
        """Test adaptive anomaly baseline learning"""
        anomaly = AdaptiveAnomaly("adaptive_test", ["health", "resource_usage"])
        
        # Train with normal data
        normal_samples = [
            {"health": 95, "resource_usage": 5},
            {"health": 98, "resource_usage": 4},
            {"health": 92, "resource_usage": 6},
            {"health": 100, "resource_usage": 3},
            {"health": 96, "resource_usage": 5},
        ]
       for sample in normal_samples:
           anomaly.learn_from_sample(sample)
       
       # Normal data should not trigger after learning
       self.assertFalse(anomaly.detect(
           {"health": 94, "resource_usage": 5}, 
           self.world_state
       ))
       
       # Outlier data should trigger
       self.assertTrue(anomaly.detect(
           {"health": 50, "resource_usage": 20},  # Significant deviation
           self.world_state
       ))
   
   def test_familiar_anomaly_integration(self):
       """Test anomaly detection integration with familiars"""
       monitor = EntityFamiliar("TestMonitor", {})
       
       # Add anomalies to watch
       undead_anomaly = UndeadEntityAnomaly()
       leak_anomaly = ResourceLeakAnomaly()
       
       monitor.add_anomaly_watch(undead_anomaly)
       monitor.add_anomaly_watch(leak_anomaly)
       
       # Test detection on problematic entity
       detected = monitor.scan_for_anomalies(
           self.test_entities["dead_entity"], 
           self.world_state
       )
       
       self.assertEqual(len(detected), 1)  # Should detect undead anomaly
       self.assertEqual(detected[0]["anomaly_type"], "undead_entity")
   
   def test_anomaly_registry(self):
       """Test anomaly registry functionality"""
       registry = AnomalyRegistry()
       
       # Register anomalies
       anomaly1 = UndeadEntityAnomaly()
       anomaly2 = ResourceLeakAnomaly()
       
       id1 = registry.register_anomaly(anomaly1)
       id2 = registry.register_anomaly(anomaly2)
       
       self.assertNotEqual(id1, id2)
       self.assertEqual(len(registry.anomalies), 2)
       
       # Create and test anomaly set
       registry.create_anomaly_set("test_set", [id1, id2])
       test_set = registry.get_anomaly_set("test_set")
       
       self.assertEqual(len(test_set), 2)
       self.assertIn(anomaly1, test_set)
       self.assertIn(anomaly2, test_set)
   
   def test_escalation_logic(self):
       """Test anomaly escalation conditions"""
       anomaly = UndeadEntityAnomaly()
       
       # Initial detection should not escalate
       self.assertFalse(anomaly.should_escalate())
       
       # Simulate multiple detections
       for i in range(12):
           anomaly.detection_count += 1
       
       # High detection count should trigger escalation
       self.assertTrue(anomaly.should_escalate())
       
       # High severity should also trigger escalation
       high_severity_anomaly = UndeadEntityAnomaly()
       high_severity_anomaly.severity = 0.95
       self.assertTrue(high_severity_anomaly.should_escalate())
   
   def test_context_based_activation(self):
       """Test context-based anomaly activation"""
       registry = AnomalyRegistry()
       
       # Register test anomalies
       pvp_anomaly = UndeadEntityAnomaly()
       pve_anomaly = ResourceLeakAnomaly()
       
       registry.register_anomaly(pvp_anomaly)
       registry.register_anomaly(pve_anomaly)
       
       # Create context sets
       registry.create_anomaly_set("pvp_anomalies", [pvp_anomaly.anomaly_id])
       registry.create_anomaly_set("pve_anomalies", [pve_anomaly.anomaly_id])
       
       # Add context rule
       def game_mode_rule(context, reg):
           mode = context.get("game_mode", "normal")
           if mode == "pvp":
               return reg.get_anomaly_set("pvp_anomalies")
           elif mode == "pve":
               return reg.get_anomaly_set("pve_anomalies")
           return []
       
       registry.add_context_rule(game_mode_rule)
       
       # Test PvP context
       pvp_context = {"game_mode": "pvp"}
       active_anomalies = registry.get_active_anomalies_for_context(pvp_context)
       self.assertEqual(len(active_anomalies), 1)
       self.assertEqual(active_anomalies[0].name, "undead_entity")
       
       # Test PvE context
       pve_context = {"game_mode": "pve"}
       active_anomalies = registry.get_active_anomalies_for_context(pve_context)
       self.assertEqual(len(active_anomalies), 1)
       self.assertEqual(active_anomalies[0].name, "resource_leak")

class TestAnomalyPerformance(unittest.TestCase):
   """Performance tests for anomaly system"""
   
   def test_large_scale_detection(self):
       """Test anomaly detection performance with many entities"""
       import time
       
       # Create monitor with multiple anomalies
       monitor = EntityFamiliar("PerformanceMonitor", {})
       monitor.add_anomaly_watch(UndeadEntityAnomaly())
       monitor.add_anomaly_watch(ResourceLeakAnomaly())
       
       # Create many test entities
       entities = []
       for i in range(1000):
           entity = EntityFamiliar(f"Entity{i}", {
               "health": 100 - (i % 150),  # Some will be negative
               "active": True,
               "resource_usage": i % 20,
               "value_generated": i % 15,
               "idle_time": i % 500
           })
           entities.append(entity)
       
       world_state = {"timestamp": "2024-01-15T10:00:00"}
       
       # Measure detection time
       start_time = time.time()
       
       total_detections = 0
       for entity in entities:
           detections = monitor.scan_for_anomalies(entity, world_state)
           total_detections += len(detections)
       
       end_time = time.time()
       detection_time = end_time - start_time
       
       print(f"Processed {len(entities)} entities in {detection_time:.3f}s")
       print(f"Detection rate: {len(entities)/detection_time:.1f} entities/sec")
       print(f"Total anomalies detected: {total_detections}")
       
       # Performance should be reasonable (adjust threshold as needed)
       self.assertLess(detection_time, 5.0, "Anomaly detection took too long")
       self.assertGreater(total_detections, 0, "Should detect some anomalies")

if __name__ == "__main__":
   unittest.main()
```

### **5.4 Documentation and Usage Guide**

````python
# grimoire/anomalies/documentation.py
"""
Grimoire Anomaly Detection System - Usage Guide

This system provides proactive anomaly detection integrated with Grimoire's
agent hierarchy. Instead of periodic searches, agents detect problems as
they encounter them during normal operations.

## Basic Usage

### 1. Define Custom Anomalies

```grimoire
anomaly CustomAnomaly extends BaseAnomaly:
    bind name = $SCROLL(custom_anomaly)
    bind severity = 0.7
    bind description = $SCROLL(Custom condition detector)
    
    ritual detect(entity_state, world_state):
        # Your detection logic here
        bind value = entity_state.get_property($SCROLL(some_property))
        return value > threshold
````

### 2. Register Anomalies
```grimoire
bind anomaly = conjure CustomAnomaly upon
register_anomaly upon anomaly
```

### 3. Assign to Monitoring Familiars

```grimoire
bind monitor = create_entity_familiar upon $SCROLL(Monitor), {}
monitor.add_anomaly_watch(anomaly)
```

### 4. Process Entities

```grimoire
bind world_state = get_current_world_state upon
bind detections = monitor.scan_for_anomalies(entity, world_state)
```

## Advanced Features

### Context-Aware Anomaly Sets

Create different anomaly profiles for different situations:

```grimoire
# Different anomalies for different game modes
bind pvp_anomalies = [cheat_detector, performance_monitor]
bind pve_anomalies = [resource_leak_detector, undead_detector]

# Context-based activation
if game_mode == $SCROLL(pvp):
    activate_anomaly_set upon pvp_anomalies
else:
    activate_anomaly_set upon pve_anomalies
```

### Hierarchical Reporting

Connect anomaly detection to agent hierarchy:

```grimoire
# Familiar detects -> Spirit aggregates -> Archon decides
connect_socket upon monitor.anomaly_output, spirit.anomaly_input
connect_socket upon spirit.escalation_output, archon.threat_input
```

### Adaptive Anomaly Management

Automatically adjust monitoring based on system conditions:

```grimoire
bind adaptive_manager = create_adaptive_manager upon
adaptive_manager.register_agent(monitor)
# Manager automatically updates anomaly sets based on context
```

## Performance Tips

1. **Use specific anomalies**: Target specific conditions rather than broad checks
2. **Implement context switching**: Don't run expensive anomalies when not needed
3. **Use composite anomalies**: Combine multiple simple checks efficiently
4. **Enable adaptive learning**: Let anomalies learn normal patterns
5. **Monitor detection rates**: Adjust thresholds if too many false positives

## Integration Patterns

### Game Development

- Monitor entity health/state violations
- Detect cheating or exploit patterns
- Track performance issues
- Validate game rule compliance

### Business Applications

- Detect fraudulent transactions
- Monitor account violations
- Track data integrity issues
- Validate business rule compliance

### System Administration

- Monitor resource leaks
- Detect security breaches
- Track performance degradation
- Validate system constraints

## Error Handling

The anomaly system is designed to be robust:

- Individual anomaly failures don't break the system
- Detection errors are logged but don't stop processing
- Malformed anomalies are skipped with warnings
- System continues operating even with anomaly failures

## Best Practices

1. **Start simple**: Begin with basic anomalies, add complexity gradually
2. **Test thoroughly**: Validate anomalies with known test cases
3. **Monitor performance**: Track detection rates and system impact
4. **Use meaningful names**: Anomaly names should clearly indicate purpose
5. **Document conditions**: Include clear descriptions of what triggers anomalies
6. **Regular review**: Periodically review and update anomaly definitions
7. **Context awareness**: Use different anomaly sets for different situations 

```python
def print_usage_examples(): """Print comprehensive usage examples""" examples = [ "Game Health Monitoring", "Financial Fraud Detection", "System Resource Monitoring", "Data Integrity Validation", "Performance Issue Detection", "Security Breach Detection" ]

print("🔮 Grimoire Anomaly Detection - Usage Examples")
print("=" * 50)

for i, example in enumerate(examples, 1):
    print(f"{i}. {example}")

print("\nSee documentation for detailed implementation examples.")
```

## Phase 6: Optimization and Production Readiness (Week 6)

### **6.1 Performance Optimization**

```python
# grimoire/anomalies/optimization.py
import threading
import queue
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class OptimizedAnomalyProcessor:
    """High-performance anomaly detection with threading and batching"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.processing_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.running = False
        
    def start_processing(self):
        """Start background anomaly processing"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_loop)
        self.processor_thread.daemon = True
        self.processor_thread.start()
    
    def stop_processing(self):
        """Stop background processing"""
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join()
    
    def submit_for_processing(self, monitor, entity, world_state):
        """Submit entity for anomaly detection"""
        self.processing_queue.put((monitor, entity, world_state))
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all available detection results"""
        results = []
        while not self.result_queue.empty():
            try:
                results.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
        return results
    
    def _process_loop(self):
        """Main processing loop with batching"""
        while self.running:
            batch = self._collect_batch()
            if batch:
                self._process_batch(batch)
            else:
                time.sleep(0.01)  # Brief pause if no work
    
    def _collect_batch(self) -> List:
        """Collect a batch of items to process"""
        batch = []
        deadline = time.time() + 0.1  # 100ms max wait
        
        while len(batch) < self.batch_size and time.time() < deadline:
            try:
                item = self.processing_queue.get(timeout=0.01)
                batch.append(item)
            except queue.Empty:
                break
        
        return batch
    
    def _process_batch(self, batch: List):
        """Process a batch of anomaly checks in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all detection tasks
            future_to_item = {
                executor.submit(self._detect_anomalies, monitor, entity, world_state): (monitor, entity)
                for monitor, entity, world_state in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_item):
                monitor, entity = future_to_item[future]
                try:
                    detections = future.result()
                    if detections:
                        self.result_queue.put({
                            "monitor": monitor.name,
                            "entity": entity.name,
                            "detections": detections,
                            "timestamp": time.time()
                        })
                except Exception as e:
                    # Log error but continue processing
                    self.result_queue.put({
                        "error": str(e),
                        "monitor": monitor.name,
                        "entity": entity.name,
                        "timestamp": time.time()
                    })
    
    def _detect_anomalies(self, monitor, entity, world_state):
        """Perform anomaly detection on single entity"""
        return monitor.scan_for_anomalies(entity, world_state)

class AnomalyCache:
    """Cache anomaly detection results to avoid redundant checks"""
    
    def __init__(self, cache_ttl: int = 300):  # 5 minute default TTL
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.lock = threading.RLock()
    
    def get_cached_result(self, entity_id: str, anomaly_id: str, entity_hash: str):
        """Get cached detection result if still valid"""
        with self.lock:
            key = f"{entity_id}:{anomaly_id}:{entity_hash}"
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return result
                else:
                    # Expired, remove from cache
                    del self.cache[key]
            return None
    
    def cache_result(self, entity_id: str, anomaly_id: str, entity_hash: str, result: bool):
        """Cache detection result"""
        with self.lock:
            key = f"{entity_id}:{anomaly_id}:{entity_hash}"
            self.cache[key] = (result, time.time())
    
    def clear_expired(self):
        """Clear expired cache entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in self.cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            for key in expired_keys:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "total_entries": len(self.cache),
                "cache_ttl": self.cache_ttl,
                "memory_usage_estimate": len(self.cache) * 100  # Rough estimate
            }
````

### **6.2 Production Monitoring and Metrics**

```python
# grimoire/anomalies/monitoring.py
import time
import json
from typing import Dict, Any, List
from collections import defaultdict, deque
from datetime import datetime, timedelta

class AnomalySystemMonitor:
    """Production monitoring for anomaly detection system"""
    
    def __init__(self, metrics_window: int = 3600):  # 1 hour window
        self.metrics_window = metrics_window
        self.metrics = defaultdict(lambda: deque())
        self.start_time = time.time()
        
        # System health metrics
        self.detection_counts = defaultdict(int)
        self.processing_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.escalation_counts = defaultdict(int)
        
    def record_detection(self, anomaly_type: str, processing_time: float, severity: float):
        """Record successful anomaly detection"""
        current_time = time.time()
        
        self.detection_counts[anomaly_type] += 1
        self.processing_times.append(processing_time)
        
        # Store timestamped metric
        self.metrics['detections'].append((current_time, anomaly_type, severity))
        self._cleanup_old_metrics()
    
    def record_error(self, error_type: str, context: str):
        """Record detection error"""
        current_time = time.time()
        
        self.error_counts[error_type] += 1
        self.metrics['errors'].append((current_time, error_type, context))
        self._cleanup_old_metrics()
    
    def record_escalation(self, anomaly_type: str, escalation_reason: str):
        """Record anomaly escalation"""
        current_time = time.time()
        
        self.escalation_counts[anomaly_type] += 1
        self.metrics['escalations'].append((current_time, anomaly_type, escalation_reason))
        self._cleanup_old_metrics()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate detection rate
        recent_detections = [
            m for m in self.metrics['detections']
            if current_time - m[0] < 300  # Last 5 minutes
        ]
        
        detection_rate = len(recent_detections) / 300 if recent_detections else 0
        
        # Calculate average processing time
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        # Calculate error rate
        recent_errors = [
            m for m in self.metrics['errors']
            if current_time - m[0] < 300
        ]
        
        error_rate = len(recent_errors) / 300 if recent_errors else 0
        
        return {
            "uptime_seconds": uptime,
            "total_detections": sum(self.detection_counts.values()),
            "detection_rate_per_second": detection_rate,
            "average_processing_time_ms": avg_processing_time * 1000,
            "total_errors": sum(self.error_counts.values()),
            "error_rate_per_second": error_rate,
            "total_escalations": sum(self.escalation_counts.values()),
            "detection_by_type": dict(self.detection_counts),
            "error_by_type": dict(self.error_counts),
            "escalation_by_type": dict(self.escalation_counts)
        }
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        current_time = time.time()
        
        # Group metrics by time buckets (5-minute intervals)
        buckets = defaultdict(lambda: {"detections": 0, "errors": 0, "escalations": 0})
        
        for timestamp, anomaly_type, severity in self.metrics['detections']:
            bucket = int((timestamp - self.start_time) // 300) * 300  # 5-minute buckets
            buckets[bucket]["detections"] += 1
        
        for timestamp, error_type, context in self.metrics['errors']:
            bucket = int((timestamp - self.start_time) // 300) * 300
            buckets[bucket]["errors"] += 1
        
        for timestamp, anomaly_type, reason in self.metrics['escalations']:
            bucket = int((timestamp - self.start_time) // 300) * 300
            buckets[bucket]["escalations"] += 1
        
        # Convert to time series
        time_series = []
        for bucket_start in sorted(buckets.keys()):
            time_series.append({
                "timestamp": self.start_time + bucket_start,
                "detections": buckets[bucket_start]["detections"],
                "errors": buckets[bucket_start]["errors"],
                "escalations": buckets[bucket_start]["escalations"]
            })
        
        return {
            "time_series": time_series,
            "total_buckets": len(time_series),
            "bucket_size_seconds": 300
        }
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than the metrics window"""
        current_time = time.time()
        cutoff_time = current_time - self.metrics_window
        
        for metric_type in self.metrics:
            while self.metrics[metric_type] and self.metrics[metric_type][0][0] < cutoff_time:
                self.metrics[metric_type].popleft()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        health = self.get_system_health()
        trends = self.get_performance_trends()
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "system_health": health,
            "performance_trends": trends
        }
        
        if format == "json":
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global monitoring instance
anomaly_monitor = AnomalySystemMonitor()
```

### **6.3 Final Integration and Deployment**

```python
# grimoire/anomalies/__init__.py
"""
Grimoire Anomaly Detection System

A comprehensive anomaly detection framework integrated with Grimoire's
agent hierarchy for proactive problem detection.
"""

from .base import BaseAnomaly, CompositeAnomaly, AdaptiveAnomaly
from .registry import AnomalyRegistry, anomaly_registry
from .context import ContextManager
from .adaptive import AdaptiveAnomalyManager, GameAdaptiveManager, BusinessAdaptiveManager
from .optimization import OptimizedAnomalyProcessor, AnomalyCache
from .monitoring import AnomalySystemMonitor, anomaly_monitor

# Pre-built anomaly types
from .game import UndeadEntityAnomaly, ResourceLeakAnomaly, CheatDetectionAnomaly, PerformanceAnomaly
from .business import NegativeBalanceAnomaly, StagnantInvestmentAnomaly, FraudIndicatorAnomaly

# Initialize default anomaly sets
from .sets import initialize_default_anomaly_sets

__version__ = "1.0.0"
__all__ = [
    # Core classes
    "BaseAnomaly", "CompositeAnomaly", "AdaptiveAnomaly",
    "AnomalyRegistry", "anomaly_registry",
    "ContextManager", "AdaptiveAnomalyManager",
    "OptimizedAnomalyProcessor", "AnomalyCache",
    "AnomalySystemMonitor", "anomaly_monitor",
    
    # Specialized managers
    "GameAdaptiveManager", "BusinessAdaptiveManager",
    
    # Pre-built anomalies
    "UndeadEntityAnomaly", "ResourceLeakAnomaly", "CheatDetectionAnomaly", "PerformanceAnomaly",
    "NegativeBalanceAnomaly", "StagnantInvestmentAnomaly", "FraudIndicatorAnomaly",
    
    # Initialization
    "initialize_default_anomaly_sets"
]

def setup_anomaly_system(config: dict = None):
    """One-line setup for complete anomaly system"""
    config = config or {}
    
    # Initialize default anomaly sets
    initialize_default_anomaly_sets()
    
    # Set up adaptive manager based on application type
    app_type = config.get("application_type", "game")
    
    if app_type == "game":
        manager = GameAdaptiveManager(
            update_interval=config.get("update_interval", 60)
        )
    elif app_type == "business":
        manager = BusinessAdaptiveManager(
            update_interval=config.get("update_interval", 300)
        )
    else:
        manager = AdaptiveAnomalyManager(
            update_interval=config.get("update_interval", 60)
        )
    
    # Start monitoring
    manager.start()
    
    # Set up optimization if requested
    if config.get("enable_optimization", True):
        processor = OptimizedAnomalyProcessor(
            max_workers=config.get("max_workers", 4),
            batch_size=config.get("batch_size", 100)
        )
        processor.start_processing()
    else:
        processor = None
    
    return {
        "adaptive_manager": manager,
        "processor": processor,
        "monitor": anomaly_monitor,
        "registry": anomaly_registry
    }

# Auto-setup with default configuration
_default_system = None

def get_default_system():
    """Get or create default anomaly system"""
    global _default_system
    if _default_system is None:
        _default_system = setup_anomaly_system()
    return _default_system
```

## Success Criteria and Testing

### **Phase 1 Success Criteria**

- [ ]  BaseAnomaly class implemented with detect() method
- [ ]  CompositeAnomaly and AdaptiveAnomaly working
- [ ]  AnomalyRegistry manages anomaly definitions and sets
- [ ]  Language integration allows anomaly definition in Grimoire

### **Phase 2 Success Criteria**

- [ ]  AnomalyDetectorMixin adds detection to familiars
- [ ]  Familiars can watch multiple anomalies simultaneously
- [ ]  Socket integration reports anomalies to higher agents
- [ ]  Escalation system works with agent hierarchy

### **Phase 3 Success Criteria**

- [ ]  Game and business anomaly libraries implemented
- [ ]  Common anomaly patterns work out-of-the-box
- [ ]  Anomalies integrate with existing entity/AI familiar system

### **Phase 4 Success Criteria**

- [ ]  Context-aware anomaly activation works
- [ ]  Time-based and load-based context switching
- [ ]  Adaptive management adjusts anomalies automatically

### **Phase 5 Success Criteria**

- [ ]  Complete integration demo runs successfully
- [ ]  Grimoire language syntax for anomalies works
- [ ]  Testing framework validates all components
- [ ]  Performance meets requirements (1000+ entities/sec)

### **Phase 6 Success Criteria**

- [ ]  Optimized processing handles high loads
- [ ]  Production monitoring provides useful metrics
- [ ]  System is ready for real-world deployment
- [ ]  Documentation is complete and comprehensive

