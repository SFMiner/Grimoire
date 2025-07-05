#!/usr/bin/env python3
"""
Grimoire Anomaly Detection System Demo

This demo showcases the Phase 6 anomaly detection system, including:
- BaseAnomaly, AdaptiveAnomaly, and CompositeAnomaly classes
- Anomaly registry and context-aware activation
- Integration with familiars for proactive monitoring
- Real-time anomaly detection and escalation
"""

import time
import random
from typing import Dict, Any, List

# Import Grimoire components
from grimoire.anomalies import (
    BaseAnomaly, AdaptiveAnomaly, CompositeAnomaly,
    AnomalyRegistry, anomaly_registry,
    register_anomaly, get_anomaly, create_anomaly_set
)
from grimoire.interpreter import GrimoireInterpreter, GrimoireFamiliar


class HealthAnomaly(BaseAnomaly):
    """Custom anomaly for detecting health-related issues."""
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """Detect if entity health is critically low."""
        health = entity_state.get('health', 100)
        max_health = entity_state.get('max_health', 100)
        
        health_percentage = health / max_health
        return health_percentage < 0.2  # Critical if below 20%


class ResourceAnomaly(BaseAnomaly):
    """Custom anomaly for detecting resource depletion."""
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """Detect if resources are running low."""
        resources = entity_state.get('resources', {})
        
        for resource_type, amount in resources.items():
            if amount < 10:  # Critical threshold
                return True
        
        return False


class PerformanceAnomaly(BaseAnomaly):
    """Custom anomaly for detecting performance issues."""
    
    def detect(self, entity_state: Dict[str, Any], world_state: Dict[str, Any]) -> bool:
        """Detect if performance metrics are degraded."""
        cpu_usage = entity_state.get('cpu_usage', 0.0)
        memory_usage = entity_state.get('memory_usage', 0.0)
        
        return cpu_usage > 0.9 or memory_usage > 0.85


def create_sample_anomalies():
    """Create and register sample anomalies."""
    print("🔮 Creating Sample Anomalies...")
    
    # 1. Health monitoring anomaly
    health_anomaly = HealthAnomaly(
        name="critical_health",
        severity=0.9,
        description="Detects when entity health drops below 20%"
    )
    health_anomaly.add_tag("health")
    health_anomaly.add_tag("critical")
    register_anomaly(health_anomaly)
    
    # 2. Resource depletion anomaly
    resource_anomaly = ResourceAnomaly(
        name="resource_depletion",
        severity=0.7,
        description="Detects when any resource drops below critical threshold"
    )
    resource_anomaly.add_tag("resources")
    resource_anomaly.add_tag("economy")
    register_anomaly(resource_anomaly)
    
    # 3. Performance monitoring anomaly
    performance_anomaly = PerformanceAnomaly(
        name="performance_degradation",
        severity=0.6,
        description="Detects high CPU or memory usage"
    )
    performance_anomaly.add_tag("performance")
    performance_anomaly.add_tag("system")
    register_anomaly(performance_anomaly)
    
    # 4. Adaptive anomaly for player behavior
    player_behavior_anomaly = AdaptiveAnomaly(
        name="unusual_player_behavior",
        properties=["actions_per_minute", "movement_speed", "resource_consumption"],
        threshold_multiplier=2.5,
        min_samples=20,
        severity=0.5,
        description="Learns normal player behavior patterns and detects anomalies"
    )
    player_behavior_anomaly.add_tag("player")
    player_behavior_anomaly.add_tag("behavior")
    player_behavior_anomaly.add_tag("adaptive")
    register_anomaly(player_behavior_anomaly)
    
    # 5. Composite anomaly for coordinated attacks
    attack_detection_anomaly = CompositeAnomaly(
        name="coordinated_attack",
        sub_anomalies=[health_anomaly, resource_anomaly],
        threshold=2,  # Both must trigger
        severity=0.95,
        description="Detects coordinated attacks affecting health and resources"
    )
    attack_detection_anomaly.add_tag("security")
    attack_detection_anomaly.add_tag("attack")
    attack_detection_anomaly.add_tag("composite")
    register_anomaly(attack_detection_anomaly)
    
    print(f"✅ Created and registered {len([health_anomaly, resource_anomaly, performance_anomaly, player_behavior_anomaly, attack_detection_anomaly])} anomalies")
    return [health_anomaly, resource_anomaly, performance_anomaly, player_behavior_anomaly, attack_detection_anomaly]


def create_anomaly_sets():
    """Create named sets of anomalies for different contexts."""
    print("\n📦 Creating Anomaly Sets...")
    
    # Game monitoring set
    create_anomaly_set("game_monitoring", [
        "critical_health",
        "resource_depletion",
        "unusual_player_behavior"
    ])
    
    # Security monitoring set
    create_anomaly_set("security_monitoring", [
        "coordinated_attack",
        "unusual_player_behavior"
    ])
    
    # Performance monitoring set
    create_anomaly_set("performance_monitoring", [
        "performance_degradation"
    ])
    
    print("✅ Created anomaly sets: game_monitoring, security_monitoring, performance_monitoring")


def demonstrate_context_rules():
    """Demonstrate context-aware anomaly activation."""
    print("\n🎯 Setting Up Context Rules...")
    
    def game_context_rule(context: Dict[str, Any], registry: AnomalyRegistry) -> List[BaseAnomaly]:
        """Context rule for game environments."""
        environment = context.get("environment", "development")
        player_count = context.get("player_count", 0)
        
        active_anomalies = []
        
        # Always include critical health monitoring
        health_anomaly = registry.get_anomaly("critical_health")
        if health_anomaly:
            active_anomalies.append(health_anomaly)
        
        # Add security monitoring for multiplayer
        if player_count > 1:
            security_anomalies = registry.get_anomalies_by_tag("security")
            active_anomalies.extend(security_anomalies)
        
        # Add performance monitoring in production
        if environment == "production":
            performance_anomalies = registry.get_anomalies_by_tag("performance")
            active_anomalies.extend(performance_anomalies)
        
        return active_anomalies
    
    anomaly_registry.add_context_rule(game_context_rule)
    print("✅ Added game context rule")


def simulate_entity_states():
    """Generate realistic entity states for testing."""
    states = []
    
    # Normal state
    states.append({
        "name": "normal_player",
        "health": 85,
        "max_health": 100,
        "resources": {"gold": 150, "wood": 75, "food": 120},
        "cpu_usage": 0.3,
        "memory_usage": 0.4,
        "actions_per_minute": 45,
        "movement_speed": 5.2,
        "resource_consumption": 12
    })
    
    # Critical health state
    states.append({
        "name": "injured_player",
        "health": 15,
        "max_health": 100,
        "resources": {"gold": 200, "wood": 100, "food": 80},
        "cpu_usage": 0.2,
        "memory_usage": 0.3,
        "actions_per_minute": 30,
        "movement_speed": 3.1,
        "resource_consumption": 8
    })
    
    # Resource depletion state
    states.append({
        "name": "resource_depleted_player",
        "health": 90,
        "max_health": 100,
        "resources": {"gold": 5, "wood": 2, "food": 180},
        "cpu_usage": 0.4,
        "memory_usage": 0.5,
        "actions_per_minute": 60,
        "movement_speed": 6.8,
        "resource_consumption": 25
    })
    
    # Performance issue state
    states.append({
        "name": "performance_issue_player",
        "health": 70,
        "max_health": 100,
        "resources": {"gold": 100, "wood": 50, "food": 90},
        "cpu_usage": 0.95,
        "memory_usage": 0.9,
        "actions_per_minute": 15,
        "movement_speed": 2.1,
        "resource_consumption": 5
    })
    
    # Coordinated attack state (triggers multiple anomalies)
    states.append({
        "name": "under_attack_player",
        "health": 18,
        "max_health": 100,
        "resources": {"gold": 8, "wood": 3, "food": 5},
        "cpu_usage": 0.6,
        "memory_usage": 0.7,
        "actions_per_minute": 80,
        "movement_speed": 8.5,
        "resource_consumption": 35
    })
    
    return states


def test_anomaly_detection():
    """Test anomaly detection with various entity states."""
    print("\n🔍 Testing Anomaly Detection...")
    
    entity_states = simulate_entity_states()
    world_state = {
        "time_of_day": "night",
        "server_load": 0.6,
        "active_players": 250
    }
    
    # Get all registered anomalies
    all_anomalies = [
        get_anomaly("critical_health"),
        get_anomaly("resource_depletion"),
        get_anomaly("performance_degradation"),
        get_anomaly("unusual_player_behavior"),
        get_anomaly("coordinated_attack")
    ]
    
    for entity_state in entity_states:
        print(f"\n--- Testing Entity: {entity_state['name']} ---")
        
        detected_anomalies = []
        
        for anomaly in all_anomalies:
            if anomaly and anomaly.detect(entity_state, world_state):
                report = anomaly.report_detection(entity_state['name'], {
                    "detection_time": time.time(),
                    "entity_state": entity_state
                })
                detected_anomalies.append(report)
        
        if detected_anomalies:
            print(f"🚨 Detected {len(detected_anomalies)} anomalies:")
            for report in detected_anomalies:
                severity_emoji = "🔴" if report['severity'] >= 0.8 else "🟡" if report['severity'] >= 0.5 else "🟢"
                print(f"  {severity_emoji} {report['anomaly_name']}: {report['anomaly_type']} (severity: {report['severity']:.2f})")
                
                # Check if escalation is needed
                anomaly = get_anomaly(report['anomaly_name'])
                if anomaly and anomaly.should_escalate():
                    print(f"    ⬆️  ESCALATION REQUIRED (detection count: {anomaly.detection_count})")
        else:
            print("✅ No anomalies detected")


def test_adaptive_learning():
    """Test adaptive anomaly learning capabilities."""
    print("\n🧠 Testing Adaptive Learning...")
    
    adaptive_anomaly = get_anomaly("unusual_player_behavior")
    if not adaptive_anomaly:
        print("❌ Adaptive anomaly not found")
        return
    
    # Generate training data (normal behavior)
    print("📚 Training adaptive anomaly with normal behavior patterns...")
    for i in range(25):
        normal_state = {
            "actions_per_minute": random.uniform(40, 60),
            "movement_speed": random.uniform(4.5, 6.0),
            "resource_consumption": random.uniform(10, 20)
        }
        adaptive_anomaly.learn_from_sample(normal_state)
    
    print(f"✅ Trained with {adaptive_anomaly.sample_count} samples")
    
    # Test with normal and anomalous behavior
    test_cases = [
        {
            "name": "normal_behavior",
            "actions_per_minute": 50,
            "movement_speed": 5.2,
            "resource_consumption": 15
        },
        {
            "name": "suspicious_behavior",
            "actions_per_minute": 150,  # Extremely high
            "movement_speed": 12.0,     # Too fast
            "resource_consumption": 2   # Too low
        }
    ]
    
    for test_case in test_cases:
        is_anomalous = adaptive_anomaly.detect(test_case, {})
        print(f"🔍 {test_case['name']}: {'🚨 ANOMALOUS' if is_anomalous else '✅ Normal'}")
    
    # Show baseline statistics
    baseline_stats = adaptive_anomaly.get_baseline_stats()
    print("\n📊 Learned Baseline Statistics:")
    for prop, stats in baseline_stats.items():
        print(f"  {prop}: mean={stats['mean']:.2f}, std_dev={stats['std_dev']:.2f}")


def test_context_activation():
    """Test context-aware anomaly activation."""
    print("\n🎮 Testing Context-Aware Activation...")
    
    contexts = [
        {
            "name": "Development Environment",
            "environment": "development",
            "player_count": 1
        },
        {
            "name": "Multiplayer Production",
            "environment": "production",
            "player_count": 50
        },
        {
            "name": "Single Player Production",
            "environment": "production",
            "player_count": 1
        }
    ]
    
    for context in contexts:
        print(f"\n--- Context: {context['name']} ---")
        active_anomalies = anomaly_registry.get_active_anomalies_for_context(context)
        
        if active_anomalies:
            print(f"🎯 {len(active_anomalies)} anomalies activated:")
            for anomaly in active_anomalies:
                print(f"  • {anomaly.name} (severity: {anomaly.severity:.2f})")
        else:
            print("📭 No anomalies activated for this context")


def test_familiar_integration():
    """Test integration with familiar monitoring system."""
    print("\n🧙 Testing Familiar Integration...")
    
    # Create a mock familiar for testing
    class MockFamiliar:
        def __init__(self, name):
            self.name = name
            self.assigned_anomalies = []
            self.detection_reports = []
        
        def assign_anomaly(self, anomaly):
            self.assigned_anomalies.append(anomaly)
        
        def check_for_anomalies(self, entity_state, world_state):
            detected = []
            for anomaly in self.assigned_anomalies:
                if anomaly.detect(entity_state, world_state):
                    report = anomaly.report_detection(self, {
                        "familiar_check": True,
                        "check_time": time.time()
                    })
                    detected.append(report)
                    self.detection_reports.append(report)
            return detected
    
    # Create monitoring familiar
    monitor_familiar = MockFamiliar("security_monitor")
    
    # Assign security-related anomalies
    security_anomalies = anomaly_registry.get_anomalies_by_tag("security")
    for anomaly in security_anomalies:
        monitor_familiar.assign_anomaly(anomaly)
    
    print(f"🛡️  Assigned {len(security_anomalies)} security anomalies to familiar '{monitor_familiar.name}'")
    
    # Test with attack scenario
    attack_state = {
        "name": "player_under_siege",
        "health": 12,
        "max_health": 100,
        "resources": {"gold": 3, "wood": 1, "food": 2}
    }
    
    detected = monitor_familiar.check_for_anomalies(attack_state, {})
    
    if detected:
        print(f"🚨 Familiar detected {len(detected)} anomalies:")
        for report in detected:
            print(f"  • {report['anomaly_name']}: {report['anomaly_type']}")
            
            # Simulate escalation to spirit/archon
            if report['severity'] >= 0.8:
                print(f"    ⬆️  ESCALATING TO SPIRIT: High severity anomaly detected")
    else:
        print("✅ No anomalies detected by familiar")


def display_registry_statistics():
    """Display comprehensive registry statistics."""
    print("\n📈 Anomaly Registry Statistics")
    print("=" * 50)
    
    stats = anomaly_registry.get_registry_stats()
    
    print(f"Total Anomalies: {stats['total_anomalies']}")
    print(f"Anomaly Sets: {stats['anomaly_sets']}")
    print(f"Context Rules: {stats['context_rules']}")
    
    print("\nSeverity Distribution:")
    for level, count in stats['severity_distribution'].items():
        print(f"  {level.capitalize()}: {count}")
    
    print("\nTag Distribution:")
    for tag, count in stats['tag_distribution'].items():
        print(f"  {tag}: {count}")
    
    print("\nSet Sizes:")
    for set_name, size in stats['set_sizes'].items():
        print(f"  {set_name}: {size}")
    
    # Show individual anomaly metadata
    print("\n🔍 Registered Anomalies:")
    for anomaly_name in anomaly_registry.list_anomalies():
        anomaly = get_anomaly(anomaly_name)
        if anomaly:
            metadata = anomaly.get_metadata()
            print(f"  • {metadata['name']} ({metadata['type']})")
            print(f"    Severity: {metadata['severity']:.2f} | Detections: {metadata['detection_count']}")
            print(f"    Tags: {', '.join(metadata['tags'])}")


def main():
    """Main demo function."""
    print("🌟 Grimoire Anomaly Detection System Demo")
    print("=" * 60)
    
    try:
        # Phase 1: Create and register anomalies
        anomalies = create_sample_anomalies()
        
        # Phase 2: Create anomaly sets
        create_anomaly_sets()
        
        # Phase 3: Set up context rules
        demonstrate_context_rules()
        
        # Phase 4: Test basic anomaly detection
        test_anomaly_detection()
        
        # Phase 5: Test adaptive learning
        test_adaptive_learning()
        
        # Phase 6: Test context activation
        test_context_activation()
        
        # Phase 7: Test familiar integration
        test_familiar_integration()
        
        # Phase 8: Display comprehensive statistics
        display_registry_statistics()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Multiple anomaly types (Base, Adaptive, Composite)")
        print("  ✅ Anomaly registry and named sets")
        print("  ✅ Context-aware anomaly activation")
        print("  ✅ Adaptive learning and baseline establishment")
        print("  ✅ Escalation based on severity and frequency")
        print("  ✅ Familiar integration for proactive monitoring")
        print("  ✅ Comprehensive reporting and statistics")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()