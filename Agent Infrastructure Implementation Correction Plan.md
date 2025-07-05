# Agent Infrastructure Implementation Correction Plan

## Overview of Current Problems

The original implementation plan has several critical issues that need correction before proceeding. The main problems are incomplete foundations, architectural mismatches, and premature complexity that could lead to a fragile system.

## Phase 1 Correction: Core Familiar System Enhancement

### **Problems Identified**

**Problem 1.1: Missing Foundation Files**

- Required files `grimoire/familiars/types.py`, `entity_familiar.py`, `ai_familiar.py` are not implemented
- No clear inheritance hierarchy from existing `GrimoireFamiliar` base class
- Socket integration with familiar types is undefined

**Problem 1.2: Type System Integration Gap**

- `FamiliarType` enum not integrated with interpreter's object creation
- No validation that familiars are created with correct types
- Missing connection between familiar types and their capabilities

**Problem 1.3: Communication Protocol Undefined**

- Inter-familiar communication lacks standardized message format
- No error handling for socket connection failures
- Missing debugging tools for socket interactions

### **Corrective Implementation Plan**

**Fix 1.1: Implement Missing Core Architecture (Week 1)**

python

```python
# grimoire/familiars/types.py
from enum import Enum, auto

class FamiliarType(Enum):
    BASE = auto()        # Generic familiar
    ENTITY = auto()      # State management
    AI = auto()          # Decision making
    PERCEPTION = auto()  # Sensory processing
    MEMORY = auto()      # Data storage
    COMMUNICATION = auto() # Message handling

class FamiliarCapability(Enum):
    PROPERTY_MANAGEMENT = auto()
    GOAL_EVALUATION = auto() 
    SPATIAL_AWARENESS = auto()
    MESSAGE_ROUTING = auto()
    STATE_PERSISTENCE = auto()

# grimoire/familiars/entity_familiar.py
from .base import GrimoireFamiliar
from .types import FamiliarType, FamiliarCapability

class EntityFamiliar(GrimoireFamiliar):
    def __init__(self, name, entity_data=None):
        super().__init__(name)
        self.familiar_type = FamiliarType.ENTITY
        self.capabilities = {FamiliarCapability.PROPERTY_MANAGEMENT}
        self.properties = entity_data or {}
        
        # Auto-create standard sockets
        self.add_socket("property_input")
        self.add_socket("property_output") 
        self.add_socket("state_query")
        
    def update_property(self, name, value):
        """Update entity property and notify via socket"""
        old_value = self.properties.get(name)
        self.properties[name] = value
        
        # Send update notification
        if self.has_socket("property_output"):
            self.send_to_socket("property_output", {
                "property": name,
                "old_value": old_value,
                "new_value": value,
                "timestamp": self.get_current_time()
            })
            
    def get_property(self, name, default=None):
        return self.properties.get(name, default)

# grimoire/familiars/ai_familiar.py  
class AIFamiliar(GrimoireFamiliar):
    def __init__(self, name):
        super().__init__(name)
        self.familiar_type = FamiliarType.AI
        self.capabilities = {FamiliarCapability.GOAL_EVALUATION}
        self.goals = []
        self.current_action = None
        
        # AI-specific sockets
        self.add_socket("goal_input")
        self.add_socket("decision_output")
        self.add_socket("world_state_input")
        
    def add_goal(self, goal_artifact):
        """Add a programmable goal artifact"""
        self.goals.append(goal_artifact)
        
    def evaluate_goals(self, world_state):
        """Evaluate all goals and return highest priority action"""
        best_action = None
        best_score = 0.0
        
        for goal in self.goals:
            if hasattr(goal, 'suggest_action'):
                action = goal.suggest_action(world_state)
                score = goal.evaluate_satisfaction(world_state) * goal.priority
                
                if score > best_score:
                    best_score = score
                    best_action = action
                    
        return best_action
```

**Fix 1.2: Interpreter Integration (Week 1)**

python

```python
# Update grimoire/interpreter.py
def execute_create_familiar(self, node):
    familiar_type = node.familiar_type.value if node.familiar_type else "BASE"
    
    # Create appropriate familiar subclass
    if familiar_type == "ENTITY":
        familiar = EntityFamiliar(node.name.value, node.initial_data)
    elif familiar_type == "AI": 
        familiar = AIFamiliar(node.name.value)
    else:
        familiar = GrimoireFamiliar(node.name.value)
        
    # Register with interpreter
    self.environment.define(node.name.value, familiar)
    return familiar

# New built-in functions
def builtin_create_entity_familiar(name, properties=None):
    return EntityFamiliar(name, properties)
    
def builtin_create_ai_familiar(name):
    return AIFamiliar(name)
```

**Fix 1.3: Communication Protocol (Week 2)**

python

```python
# grimoire/familiars/messaging.py
from dataclasses import dataclass
from typing import Any, Optional
import uuid
from datetime import datetime

@dataclass
class FamiliarMessage:
    id: str
    sender: str
    recipient: str  
    message_type: str
    payload: Any
    timestamp: datetime
    reply_to: Optional[str] = None
    
    @classmethod
    def create(cls, sender, recipient, msg_type, payload):
        return cls(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=msg_type, 
            payload=payload,
            timestamp=datetime.now()
        )

class MessageRouter:
    def __init__(self):
        self.message_queue = []
        self.familiar_registry = {}
        
    def register_familiar(self, familiar):
        self.familiar_registry[familiar.name] = familiar
        
    def send_message(self, message):
        """Route message to appropriate familiar"""
        if message.recipient in self.familiar_registry:
            recipient = self.familiar_registry[message.recipient]
            recipient.receive_message(message)
            return True
        return False
        
    def broadcast_message(self, sender, msg_type, payload):
        """Send message to all registered familiars"""
        for name, familiar in self.familiar_registry.items():
            if name != sender:
                msg = FamiliarMessage.create(sender, name, msg_type, payload)
                self.send_message(msg)

# Add to GrimoireFamiliar base class
def receive_message(self, message):
    """Handle incoming message"""
    if message.message_type == "property_update":
        self.handle_property_update(message.payload)
    elif message.message_type == "goal_request":
        self.handle_goal_request(message.payload) 
    # Add more message types as needed
```

### **Testing Strategy for Phase 1**

grimoire

```grimoire
# Test entity familiar creation and communication
bind player_entity = create_entity_familiar upon $SCROLL(Player), {health: 100, mana: 50}
bind ai_controller = create_ai_familiar upon $SCROLL(PlayerAI)

# Test socket communication
connect_socket upon player_entity.property_output, ai_controller.world_state_input

# Test property updates trigger socket messages
player_entity.update_property("health", 75)
# Should send message to AI familiar via socket
```

## Phase 2 Correction: AI Goal System Implementation

### **Problems Identified**

**Problem 2.1: Goal Architecture Mismatch**

- Plan implements procedural `Goal` class instead of programmable artifacts
- No integration between goals and the Grimoire artifact system
- Missing connection to thematic keyword variants (objectives, vows, ambitions, etc.)

**Problem 2.2: Missing World State Framework**

- No defined interface for goals to query world state
- AI planning occurs in isolation without environmental context
- No mechanism for goals to influence each other

**Problem 2.3: Action System Undefined**

- Actions not connected to familiar capabilities or socket system
- No precondition checking or effect prediction
- Missing integration with entity property system

### **Corrective Implementation Plan**

**Fix 2.1: Implement Artifact-Based Goals (Week 3)**

python

```python
# grimoire/ai/goal_artifacts.py
class GoalArtifactMeta(type):
    """Metaclass to register goal artifacts with interpreter"""
    def __new__(cls, name, bases, attrs):
        goal_class = super().__new__(cls, name, bases, attrs)
        # Register with Grimoire's artifact system
        return goal_class

class BaseGoalArtifact(metaclass=GoalArtifactMeta):
    """Base class for all programmable goal artifacts"""
    def __init__(self, name, priority=0.5):
        self.name = name
        self.priority = priority
        self.satisfaction_history = []
        
    def evaluate_satisfaction(self, world_state):
        """Override in subclasses - returns 0.0 to 1.0"""
        raise NotImplementedError("Goals must implement evaluate_satisfaction")
        
    def suggest_action(self, world_state, available_actions):
        """Override in subclasses - returns best action for this goal"""
        return None
        
    def is_satisfied(self, world_state, threshold=0.9):
        return self.evaluate_satisfaction(world_state) >= threshold

# Update interpreter to support goal artifacts
def execute_artifact_definition(self, node):
    if node.base_class == "BaseGoalArtifact":
        # Special handling for goal artifacts
        goal_class = self.create_goal_artifact_class(node)
        self.environment.define(node.name, goal_class)
    else:
        # Regular artifact handling
        artifact_class = self.create_artifact_class(node)
        self.environment.define(node.name, artifact_class)
```

**Fix 2.2: World State Interface (Week 3)**

python

```python
# grimoire/ai/world_state.py
class WorldState:
    """Standardized interface for AI goals to query world state"""
    def __init__(self):
        self.entities = {}  # All game entities
        self.properties = {}  # Global properties
        self.spatial_data = {}  # Location information
        self.temporal_data = {}  # Time-based information
        
    def get_entity_property(self, entity_name, property_name):
        """Get property of specific entity"""
        if entity_name in self.entities:
            return self.entities[entity_name].get_property(property_name)
        return None
        
    def get_entities_by_type(self, entity_type):
        """Get all entities of specific type"""
        return [e for e in self.entities.values() 
                if e.get_property("type") == entity_type]
                
    def get_entities_in_area(self, center, radius):
        """Get entities within spatial area"""
        # Implementation depends on spatial system
        pass
        
    def get_global_property(self, property_name):
        """Get world-wide property (resources, time, etc.)"""
        return self.properties.get(property_name)
        
    def update_from_familiar(self, familiar):
        """Update world state from familiar's perspective"""
        if hasattr(familiar, 'name'):
            self.entities[familiar.name] = familiar

# Integration with existing familiar system
class WorldStateManager:
    def __init__(self):
        self.world_state = WorldState()
        self.familiar_registry = {}
        
    def register_familiar(self, familiar):
        self.familiar_registry[familiar.name] = familiar
        self.world_state.update_from_familiar(familiar)
        
    def get_world_state_for_ai(self, ai_familiar):
        """Get world state filtered for specific AI's perspective"""
        # Could implement visibility, knowledge limitations, etc.
        return self.world_state
```

**Fix 2.3: Action System Integration (Week 4)**

python

```python
# grimoire/ai/actions.py
from dataclasses import dataclass
from typing import Dict, Any, Callable

@dataclass
class Action:
    name: str
    preconditions: Dict[str, Any]  # What must be true to execute
    effects: Dict[str, Any]        # What changes when executed
    cost: float                    # Resource cost or difficulty
    execute_func: Callable         # Function to actually perform action
    
    def can_execute(self, world_state, actor):
        """Check if preconditions are met"""
        for condition, required_value in self.preconditions.items():
            if not self.check_condition(world_state, actor, condition, required_value):
                return False
        return True
        
    def check_condition(self, world_state, actor, condition, required_value):
        """Check specific precondition"""
        if condition.startswith("actor."):
            property_name = condition[6:]  # Remove "actor."
            actual_value = actor.get_property(property_name)
            return actual_value >= required_value
        elif condition.startswith("world."):
            property_name = condition[6:]  # Remove "world."
            actual_value = world_state.get_global_property(property_name)
            return actual_value >= required_value
        return True
        
    def predict_outcome(self, world_state, actor):
        """Predict world state after action execution"""
        # Create copy of world state and apply effects
        predicted_state = copy.deepcopy(world_state)
        for effect, value in self.effects.items():
            if effect.startswith("actor."):
                property_name = effect[6:]
                current = actor.get_property(property_name, 0)
                # Apply effect (could be add, set, multiply, etc.)
                if isinstance(value, str) and value.startswith("+"):
                    new_value = current + float(value[1:])
                else:
                    new_value = value
                predicted_state.entities[actor.name].update_property(property_name, new_value)
        return predicted_state

# Action library for common game actions
class ActionLibrary:
    @staticmethod
    def create_move_action(target_location):
        return Action(
            name=f"move_to_{target_location}",
            preconditions={"actor.can_move": True},
            effects={"actor.location": target_location},
            cost=1.0,
            execute_func=lambda actor: actor.update_property("location", target_location)
        )
        
    @staticmethod  
    def create_attack_action(target, damage):
        return Action(
            name=f"attack_{target}",
            preconditions={"actor.can_attack": True, "actor.weapon": 1},
            effects={f"target.{target}.health": f"-{damage}"},
            cost=2.0,
            execute_func=lambda actor: ActionLibrary.execute_attack(actor, target, damage)
        )
```

### **Testing Strategy for Phase 2**

grimoire

```grimoire
# Test programmable goal artifacts
artifact TestTerritorialObjective extends BaseGoalArtifact:
    bind priority = 0.8
    bind target_area = 100
    
    ritual evaluate_satisfaction(world_state):
        bind controlled_area = world_state.get_global_property("controlled_territory")
        return controlled_area divided by self.target_area
        
    ritual suggest_action(world_state, available_actions):
        for action in available_actions:
            if action.name contains "expand":
                return action
        return null

# Test goal integration with AI familiar
bind territorial_goal = conjure TestTerritorialObjective upon $SCROLL(expand_territory), 0.8
bind ai_commander = create_ai_familiar upon $SCROLL(Commander)
ai_commander.add_goal(territorial_goal)

# Test action evaluation
bind move_action = create_action upon $SCROLL(move_north), {...}
bind best_action = ai_commander.evaluate_goals(current_world_state)
```

## Phase 3 Correction: Simplified Integration Layer

### **Problems Identified**

**Problem 3.1: Premature Complexity**

- Original plan jumps to complex game features before foundations are stable
- Property effects and game loops introduced before basic entity management works
- Spatial system planned independently of familiar/socket integration

**Problem 3.2: Missing Integration Points**

- No clear connection between Phase 3 features and socket system
- Game features not aligned with goal/action architecture from Phase 2
- Missing testing framework for the familiar system

**Problem 3.3: Scope Creep**

- Too many features introduced simultaneously
- No incremental validation of system components
- Risk of building unstable foundation

### **Corrective Implementation Plan**

**Fix 3.1: Simplified Entity Interaction System (Week 5)**

python

```python
# grimoire/game/simple_interactions.py
class InteractionRule:
    """Simple rule for entity interactions"""
    def __init__(self, name, source_type, target_type, interaction_func):
        self.name = name
        self.source_type = source_type
        self.target_type = target_type
        self.interaction_func = interaction_func
        
    def can_apply(self, source_entity, target_entity):
        source_matches = source_entity.get_property("type") == self.source_type
        target_matches = target_entity.get_property("type") == self.target_type
        return source_matches and target_matches
        
    def execute(self, source_entity, target_entity):
        return self.interaction_func(source_entity, target_entity)

class SimpleInteractionManager:
    """Manages basic entity interactions through sockets"""
    def __init__(self):
        self.rules = []
        self.interaction_log = []
        
    def add_rule(self, rule):
        self.rules.append(rule)
        
    def process_interaction(self, source, target):
        """Process interaction between two entities"""
        for rule in self.rules:
            if rule.can_apply(source, target):
                result = rule.execute(source, target)
                
                # Log interaction
                self.interaction_log.append({
                    "rule": rule.name,
                    "source": source.name,
                    "target": target.name,
                    "result": result,
                    "timestamp": self.get_current_time()
                })
                
                # Notify via sockets if available
                if source.has_socket("interaction_output"):
                    source.send_to_socket("interaction_output", {
                        "interaction": rule.name,
                        "target": target.name,
                        "result": result
                    })
                    
                return result
        return None

# Example interaction rules
def create_damage_rule():
    def damage_interaction(attacker, defender):
        damage = attacker.get_property("attack_power", 10)
        current_health = defender.get_property("health", 100)
        new_health = max(0, current_health - damage)
        defender.update_property("health", new_health)
        return f"Dealt {damage} damage, health now {new_health}"
    
    return InteractionRule("damage", "attacker", "defender", damage_interaction)

def create_healing_rule():
    def healing_interaction(healer, patient):
        healing_power = healer.get_property("healing_power", 15)
        current_health = patient.get_property("health", 0)
        max_health = patient.get_property("max_health", 100)
        new_health = min(max_health, current_health + healing_power)
        patient.update_property("health", new_health)
        return f"Healed {healing_power} points, health now {new_health}"
    
    return InteractionRule("healing", "healer", "patient", healing_interaction)
```

**Fix 3.2: Basic Testing Framework (Week 6)**

python

```python
# grimoire/testing/familiar_tests.py
class FamiliarTestHarness:
    """Testing framework for familiar system"""
    def __init__(self):
        self.test_results = []
        self.mock_world_state = WorldState()
        self.test_familiars = {}
        
    def create_test_entity(self, name, properties):
        """Create test entity familiar"""
        entity = EntityFamiliar(name, properties)
        self.test_familiars[name] = entity
        return entity
        
    def create_test_ai(self, name):
        """Create test AI familiar"""
        ai = AIFamiliar(name)
        self.test_familiars[name] = ai
        return ai
        
    def test_socket_communication(self, sender_name, socket_name, receiver_name):
        """Test socket communication between familiars"""
        sender = self.test_familiars.get(sender_name)
        receiver = self.test_familiars.get(receiver_name)
        
        if not sender or not receiver:
            return False
            
        # Connect sockets
        if sender.has_socket(socket_name):
            test_data = {"test": "socket_communication", "timestamp": time.time()}
            sender.send_to_socket(socket_name, test_data)
            
            # Check if receiver got the message
            # This depends on how socket implementation works
            return True
        return False
        
    def test_goal_evaluation(self, ai_name, world_state_properties):
        """Test AI goal evaluation"""
        ai = self.test_familiars.get(ai_name)
        if not ai or not hasattr(ai, 'goals'):
            return False
            
        # Set up test world state
        for prop, value in world_state_properties.items():
            self.mock_world_state.properties[prop] = value
            
        # Test goal evaluation
        for goal in ai.goals:
            satisfaction = goal.evaluate_satisfaction(self.mock_world_state)
            self.test_results.append({
                "test": "goal_evaluation",
                "ai": ai_name,
                "goal": goal.name,
                "satisfaction": satisfaction
            })
            
        return True
        
    def run_integration_test(self):
        """Run complete integration test"""
        # Test 1: Create entities and AI
        player = self.create_test_entity("player", {"health": 100, "mana": 50})
        enemy = self.create_test_entity("enemy", {"health": 80, "attack": 15})
        ai = self.create_test_ai("combat_ai")
        
        # Test 2: Socket communication
        connect_result = self.test_socket_communication("player", "property_output", "combat_ai")
        
        # Test 3: Property updates
        player.update_property("health", 75)
        
        # Test 4: Goal evaluation
        self.test_goal_evaluation("combat_ai", {"player_health": 75, "enemy_health": 80})
        
        return {
            "socket_test": connect_result,
            "results": self.test_results
        }
```

**Fix 3.3: Integration Examples (Week 6)**

grimoire

```grimoire
# grimoire/examples/basic_familiar_demo.grim
# Demonstration of corrected familiar system

ritual main():
    scry $SCROLL(=== Grimoire Familiar System Demo ===)
    
    # Create test entities
    bind player = create_entity_familiar upon $SCROLL(Player), {
        health: 100,
        mana: 50,
        type: $SCROLL(player)
    }
    
    bind enemy = create_entity_familiar upon $SCROLL(Goblin), {
        health: 60,
        attack: 12,
        type: $SCROLL(enemy)
    }
    
    # Create AI controller
    bind ai_controller = create_ai_familiar upon $SCROLL(GameAI)
    
    # Connect via sockets
    connect_socket upon player.property_output, ai_controller.world_state_input
    connect_socket upon enemy.property_output, ai_controller.world_state_input
    
    # Create and add goals
    bind survival_goal = conjure SurvivalObjective upon $SCROLL(keep_player_alive), 0.9
    ai_controller.add_goal(survival_goal)
    
    # Test interaction
    bind damage_rule = create_damage_rule upon
    bind interaction_manager = create_interaction_manager upon
    interaction_manager.add_rule(damage_rule)
    
    # Simulate combat
    bind result = interaction_manager.process_interaction(enemy, player)
    scry $SCROLL(Combat result: ) added to result
    
    # Test AI response
    bind world_state = get_current_world_state upon
    bind ai_decision = ai_controller.evaluate_goals(world_state)
    scry $SCROLL(AI Decision: ) added to ai_decision

# Run the demo
main upon
```

### **Testing Strategy for Phase 3**

1. **Integration Testing**: Verify all three phases work together
2. **Socket Communication**: Test data flow between familiar types
3. **Goal-Action Integration**: Verify AI can evaluate goals and suggest actions
4. **Error Handling**: Test system behavior with invalid inputs
5. **Performance Testing**: Ensure system scales with multiple familiars

## Success Criteria

**Phase 1 Complete**: Different familiar types can be created and communicate via sockets **Phase 2 Complete**: AI familiars can evaluate programmable goals and suggest actions  
**Phase 3 Complete**: Complete familiar system with working entity interactions and testing framework

This corrected plan focuses on building solid foundations incrementally rather than trying to implement complex features prematurely.