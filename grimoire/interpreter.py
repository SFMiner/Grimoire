#!/usr/bin/env python3
"""
Grimoire Programming Language Interpreter

This module implements a tree-walking interpreter for the Grimoire programming language.
"""

import sys
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .lexer import TokenType
from .parser import (
    Program, Statement, Expression, ASTNode,
    LiteralExpression, IdentifierExpression, BinaryExpression, UnaryExpression,
    CallExpression, PropertyAccessExpression, ConjureExpression, PortalExpression,
    PropertyAssignmentExpression, ExpressionStatement, BindStatement, ScryStatement,
    IfStatement, WhileStatement, ForStatement, BlockStatement, ReturnStatement,
    BreakStatement, ContinueStatement,
    RitualStatement, ArtifactStatement, FamiliarStatement, ArchonStatement, SpiritStatement,
    PlaneStatement, EffectStatement, CommandStatement
)


# =============================================================================
# Runtime Values and Environment
# =============================================================================

@dataclass
class GrimoireFunction:
    """Represents a runtime function (ritual)."""
    name: str
    parameters: List[str]
    body: BlockStatement
    closure: 'Environment'
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> Any:
        """Execute the function with given arguments."""
        if len(arguments) != len(self.parameters):
            raise RuntimeError(f"Expected {len(self.parameters)} arguments but got {len(arguments)}")
        
        # Create new environment for function execution
        function_env = Environment(self.closure)
        
        # Bind parameters to arguments
        for param, arg in zip(self.parameters, arguments):
            function_env.define(param, arg)
        
        # Execute function body
        try:
            interpreter.execute_block(self.body.statements, function_env)
        except ReturnValue as return_val:
            return return_val.value
        
        return None


@dataclass
class GrimoireClass:
    """Represents a runtime class (artifact)."""
    name: str
    superclass: Optional['GrimoireClass']
    methods: Dict[str, GrimoireFunction]
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> 'GrimoireInstance':
        """Create a new instance of this class."""
        instance = GrimoireInstance(self)
        
        # Look for constructor (invoke method)
        if "invoke" in self.methods:
            self.methods["invoke"].call(interpreter, [instance] + arguments)
        
        return instance


class GrimoireInstance:
    """Represents a runtime instance of a class."""
    
    def __init__(self, grimoire_class: GrimoireClass):
        self.grimoire_class = grimoire_class
        self.fields = {}
    
    def get(self, name: str) -> Any:
        """Get a property value."""
        if name in self.fields:
            return self.fields[name]
        
        # Look for method
        method = self.grimoire_class.methods.get(name)
        if method:
            return BoundMethod(self, method)
        
        raise RuntimeError(f"Undefined property '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """Set a property value."""
        self.fields[name] = value


# =============================================================================
# Familiar System
# =============================================================================

class FamiliarCapability(ABC):
    """Base class for familiar capabilities."""
    
    @abstractmethod
    def execute(self, command: str, arguments: List[Any]) -> Any:
        """Execute a command with given arguments."""
        pass
    
    @abstractmethod
    def inquire(self, query: str) -> Any:
        """Handle an inquiry about the familiar's state."""
        pass


class MemoryImpCapability(FamiliarCapability):
    """Memory management familiar capability."""
    
    def __init__(self):
        self.allocated_memory = 0
        self.max_memory = 1024 * 1024  # 1MB default
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "allocate":
            if len(arguments) != 1:
                raise RuntimeError("allocate expects 1 argument (bytes)")
            bytes_to_allocate = arguments[0]
            if self.allocated_memory + bytes_to_allocate > self.max_memory:
                raise RuntimeError("Not enough memory available")
            self.allocated_memory += bytes_to_allocate
            return f"Allocated {bytes_to_allocate} bytes"
        elif command == "deallocate":
            if len(arguments) != 1:
                raise RuntimeError("deallocate expects 1 argument (bytes)")
            bytes_to_free = arguments[0]
            self.allocated_memory = max(0, self.allocated_memory - bytes_to_free)
            return f"Deallocated {bytes_to_free} bytes"
        else:
            raise RuntimeError(f"Unknown memory command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "free_space":
            return self.max_memory - self.allocated_memory
        elif query == "used_space":
            return self.allocated_memory
        elif query == "total_space":
            return self.max_memory
        else:
            raise RuntimeError(f"Unknown memory query: {query}")


class FileSpriteCapability(FamiliarCapability):
    """File system operations familiar capability."""
    
    def __init__(self):
        self.open_files = {}
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "read":
            if len(arguments) != 1:
                raise RuntimeError("read expects 1 argument (filename)")
            filename = arguments[0]
            try:
                with open(filename, 'r') as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to read file: {e}")
        elif command == "write":
            if len(arguments) != 2:
                raise RuntimeError("write expects 2 arguments (filename, content)")
            filename, content = arguments
            try:
                with open(filename, 'w') as f:
                    f.write(str(content))
                return f"Wrote to {filename}"
            except Exception as e:
                raise RuntimeError(f"Failed to write file: {e}")
        elif command == "append":
            if len(arguments) != 2:
                raise RuntimeError("append expects 2 arguments (filename, content)")
            filename, content = arguments
            try:
                with open(filename, 'a') as f:
                    f.write(str(content))
                return f"Appended to {filename}"
            except Exception as e:
                raise RuntimeError(f"Failed to append to file: {e}")
        else:
            raise RuntimeError(f"Unknown file command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "open_files":
            return list(self.open_files.keys())
        else:
            raise RuntimeError(f"Unknown file query: {query}")


class LogScribeCapability(FamiliarCapability):
    """Logging and tracing familiar capability."""
    
    def __init__(self):
        self.log_entries = []
        self.log_level = "INFO"
    
    def execute(self, command: str, arguments: List[Any]) -> Any:
        if command == "log":
            if len(arguments) < 1:
                raise RuntimeError("log expects at least 1 argument (message)")
            message = arguments[0]
            level = arguments[1] if len(arguments) > 1 else "INFO"
            self.log_entries.append(f"[{level}] {message}")
            return f"Logged: {message}"
        elif command == "clear":
            self.log_entries.clear()
            return "Log cleared"
        elif command == "set_level":
            if len(arguments) != 1:
                raise RuntimeError("set_level expects 1 argument (level)")
            self.log_level = arguments[0]
            return f"Log level set to {self.log_level}"
        else:
            raise RuntimeError(f"Unknown log command: {command}")
    
    def inquire(self, query: str) -> Any:
        if query == "entries":
            return self.log_entries.copy()
        elif query == "level":
            return self.log_level
        elif query == "count":
            return len(self.log_entries)
        else:
            raise RuntimeError(f"Unknown log query: {query}")


# The GrimoireFamiliar class is now defined below with full hierarchical agent integration


# =============================================================================
# Hierarchical Agent System: Goals, Archons, Spirits
# =============================================================================

@dataclass
class Goal:
    """Represents a goal for an agent."""
    name: str
    priority: int
    weight: float
    satisfaction_threshold: float
    current_satisfaction: float = 0.0
    
    def is_satisfied(self) -> bool:
        """Check if the goal is satisfied."""
        return self.current_satisfaction >= self.satisfaction_threshold
    
    def get_urgency(self) -> float:
        """Calculate urgency based on satisfaction level."""
        return (1.0 - self.current_satisfaction) * self.weight


class GoalSeeker:
    """Mixin class for agents that can pursue goals."""
    
    def __init__(self):
        self.goals: List[Goal] = []
    
    def add_goal(self, name: str, priority: int, weight: float = 1.0, threshold: float = 1.0):
        """Add a goal to this agent."""
        goal = Goal(name, priority, weight, threshold)
        self.goals.append(goal)
        # Sort by priority (highest first)
        self.goals.sort(key=lambda g: g.priority, reverse=True)
    
    def evaluate_goals(self) -> Dict[str, float]:
        """Evaluate satisfaction of all goals."""
        satisfaction = {}
        for goal in self.goals:
            satisfaction[goal.name] = goal.current_satisfaction
        return satisfaction
    
    def get_priority_goal(self) -> Optional[Goal]:
        """Get the highest priority unsatisfied goal."""
        for goal in self.goals:
            if not goal.is_satisfied():
                return goal
        return None
    
    def update_goal_satisfaction(self, goal_name: str, satisfaction: float):
        """Update the satisfaction level of a goal."""
        for goal in self.goals:
            if goal.name == goal_name:
                goal.current_satisfaction = max(0.0, min(1.0, satisfaction))
                break


class InteractionMatrix:
    """Manages relationships and interactions between agents."""
    
    def __init__(self):
        self.relationships: Dict[str, str] = {}  # "agent1-agent2" -> "relationship_type"
        self.communication_protocols: Dict[str, str] = {}
        self.cooperation_history: Dict[str, List[str]] = {}
    
    def establish_relationship(self, agent_a: str, agent_b: str, relationship_type: str):
        """Establish a relationship between two agents."""
        key = f"{agent_a}-{agent_b}"
        reverse_key = f"{agent_b}-{agent_a}"
        
        self.relationships[key] = relationship_type
        self.relationships[reverse_key] = relationship_type
        
        # Set communication protocol based on relationship
        if relationship_type == "cooperative":
            protocol = "full_sharing"
        elif relationship_type == "competitive":
            protocol = "limited_sharing"
        elif relationship_type == "hierarchical":
            protocol = "command_structure"
        else:
            protocol = "minimal_sharing"
        
        self.communication_protocols[key] = protocol
        self.communication_protocols[reverse_key] = protocol
    
    def get_relationship(self, agent_a: str, agent_b: str) -> str:
        """Get the relationship type between two agents."""
        key = f"{agent_a}-{agent_b}"
        return self.relationships.get(key, "neutral")
    
    def can_communicate(self, agent_a: str, agent_b: str) -> bool:
        """Check if two agents can communicate."""
        relationship = self.get_relationship(agent_a, agent_b)
        return relationship != "hostile"


class GrimoireArchon(GoalSeeker):
    """Strategic-level AI agent that manages multiple spirits."""
    
    def __init__(self, name: str, domain: str):
        super().__init__()
        self.name = name
        self.domain = domain
        self.spirits: List['GrimoireSpirit'] = []
        self.resource_budget = 1000
        self.strategic_goals: List[str] = []
        self.methods: Dict[str, GrimoireFunction] = {}
        self.state = "active"
        
        # Initialize domain-specific goals
        self.initialize_strategic_goals()
    
    def initialize_strategic_goals(self):
        """Initialize goals based on domain."""
        if self.domain == "Combat":
            self.add_goal("territorial_control", 10, 1.0, 0.8)
            self.add_goal("force_projection", 8, 0.8, 0.7)
            self.add_goal("resource_security", 6, 0.6, 0.6)
        elif self.domain == "Economy":
            self.add_goal("resource_maximization", 10, 1.0, 0.8)
            self.add_goal("trade_expansion", 7, 0.7, 0.6)
            self.add_goal("infrastructure_development", 5, 0.5, 0.5)
        elif self.domain == "Diplomacy":
            self.add_goal("alliance_building", 9, 0.9, 0.7)
            self.add_goal("information_gathering", 8, 0.8, 0.6)
            self.add_goal("reputation_management", 6, 0.6, 0.5)
        else:
            # General archon
            self.add_goal("survival", 10, 1.0, 0.8)
            self.add_goal("growth", 5, 0.5, 0.5)
    
    def summon_spirit(self, spirit_type: str, objectives: List[str]) -> 'GrimoireSpirit':
        """Create and manage a new spirit."""
        spirit = GrimoireSpirit(f"{self.name}_{spirit_type}_{len(self.spirits)}", spirit_type)
        spirit.archon_ref = self
        
        # Assign objectives to spirit
        for i, objective in enumerate(objectives):
            spirit.add_goal(objective, 10 - i)
        
        self.spirits.append(spirit)
        return spirit
    
    def autonomous_update(self):
        """Perform autonomous strategic decision making."""
        if self.state != "active":
            return
        
        # Evaluate current strategic situation
        priority_goal = self.get_priority_goal()
        if priority_goal:
            self.execute_strategic_action(priority_goal)
        
        # Update spirits
        for spirit in self.spirits:
            spirit.autonomous_update()
        
        # Resource allocation
        self.allocate_resources()
    
    def execute_strategic_action(self, goal: Goal):
        """Execute a strategic action to pursue a goal."""
        # This would contain domain-specific strategic logic
        # For now, we'll implement basic goal pursuit
        if goal.name == "territorial_control":
            self.expand_territory()
        elif goal.name == "resource_maximization":
            self.optimize_resource_gathering()
        elif goal.name == "alliance_building":
            self.seek_alliances()
        
        # Update goal satisfaction (simplified)
        goal.current_satisfaction += 0.1
    
    def expand_territory(self):
        """Strategic action: expand territorial control."""
        # Summon combat spirits if needed
        if len([s for s in self.spirits if s.spirit_type == "Guardian"]) < 2:
            self.summon_spirit("Guardian", ["defend_territory", "patrol_borders"])
    
    def optimize_resource_gathering(self):
        """Strategic action: optimize resource gathering."""
        # Summon economic spirits if needed
        if len([s for s in self.spirits if s.spirit_type == "Harvester"]) < 1:
            self.summon_spirit("Harvester", ["gather_resources", "expand_operations"])
    
    def seek_alliances(self):
        """Strategic action: seek diplomatic alliances."""
        # This would involve inter-archon communication
        pass
    
    def allocate_resources(self):
        """Allocate resources among spirits."""
        if self.resource_budget > 0 and self.spirits:
            allocation_per_spirit = self.resource_budget // len(self.spirits)
            for spirit in self.spirits:
                spirit.resource_allocation = allocation_per_spirit


class GrimoireSpirit(GoalSeeker):
    """Tactical-level AI agent that manages multiple familiars."""
    
    def __init__(self, name: str, spirit_type: str):
        super().__init__()
        self.name = name
        self.spirit_type = spirit_type
        self.archon_ref: Optional[GrimoireArchon] = None
        self.familiars: List['GrimoireFamiliar'] = []
        self.resource_allocation = 0
        self.cooperation_network: List['GrimoireSpirit'] = []
        self.methods: Dict[str, GrimoireFunction] = {}
        self.state = "active"
        
        # Initialize type-specific behaviors
        self.initialize_tactical_behaviors()
    
    def initialize_tactical_behaviors(self):
        """Initialize behaviors based on spirit type."""
        if self.spirit_type == "Guardian":
            self.add_goal("defensive_positioning", 9, 0.9, 0.7)
            self.add_goal("threat_assessment", 8, 0.8, 0.6)
            self.add_goal("patrol_completion", 6, 0.6, 0.5)
        elif self.spirit_type == "Scout":
            self.add_goal("exploration_coverage", 10, 1.0, 0.8)
            self.add_goal("information_gathering", 9, 0.9, 0.7)
            self.add_goal("safe_return", 8, 0.8, 0.6)
        elif self.spirit_type == "Harvester":
            self.add_goal("resource_collection", 10, 1.0, 0.8)
            self.add_goal("efficiency_optimization", 7, 0.7, 0.6)
            self.add_goal("site_security", 6, 0.6, 0.5)
        else:
            # General spirit
            self.add_goal("objective_completion", 8, 0.8, 0.6)
            self.add_goal("familiar_coordination", 6, 0.6, 0.5)
    
    def spawn_familiar(self, familiar_type: str, objectives: List[str]) -> GrimoireFamiliar:
        """Create and manage a new familiar."""
        capabilities = FAMILIAR_TYPES.get(familiar_type, lambda: {})()
        familiar = GrimoireFamiliar(f"{self.name}_{familiar_type}_{len(self.familiars)}", familiar_type, capabilities)
        familiar.spirit_ref = self
        
        self.familiars.append(familiar)
        return familiar
    
    def autonomous_update(self):
        """Perform autonomous tactical decision making."""
        if self.state != "active":
            return
        
        # Assess current situation
        priority_goal = self.get_priority_goal()
        if priority_goal:
            self.execute_tactical_action(priority_goal)
        
        # Coordinate with peer spirits
        for peer in self.cooperation_network:
            self.coordinate_with(peer)
        
        # Update familiars
        for familiar in self.familiars:
            familiar.autonomous_update()
        
        # Report to archon
        self.report_to_archon()
    
    def execute_tactical_action(self, goal: Goal):
        """Execute a tactical action to pursue a goal."""
        if goal.name == "defensive_positioning":
            self.position_defensively()
        elif goal.name == "exploration_coverage":
            self.explore_area()
        elif goal.name == "resource_collection":
            self.collect_resources()
        
        # Update goal satisfaction
        goal.current_satisfaction += 0.2
    
    def position_defensively(self):
        """Tactical action: position familiars defensively."""
        # Ensure we have scout familiars
        if len([f for f in self.familiars if f.familiar_type == "Scout"]) < 1:
            self.spawn_familiar("Scout", ["perimeter_patrol"])
    
    def explore_area(self):
        """Tactical action: explore unknown areas."""
        # Spawn scout familiars for exploration
        if len([f for f in self.familiars if f.familiar_type == "Scout"]) < 2:
            self.spawn_familiar("Scout", ["area_exploration"])
    
    def collect_resources(self):
        """Tactical action: collect resources."""
        # Spawn harvester familiars
        if len([f for f in self.familiars if f.familiar_type == "Harvester"]) < 1:
            self.spawn_familiar("Harvester", ["resource_collection"])
    
    def coordinate_with(self, other_spirit: 'GrimoireSpirit'):
        """Coordinate actions with another spirit."""
        # Find common goals
        common_goals = set(g.name for g in self.goals) & set(g.name for g in other_spirit.goals)
        
        if common_goals:
            # Negotiate joint action for first common goal
            joint_goal = list(common_goals)[0]
            self.negotiate_joint_action(other_spirit, joint_goal)
    
    def negotiate_joint_action(self, other_spirit: 'GrimoireSpirit', goal_name: str):
        """Negotiate a joint action with another spirit."""
        # Simple cooperation: share resource allocation
        if self.resource_allocation > 0:
            shared_resources = self.resource_allocation // 2
            other_spirit.resource_allocation += shared_resources
            self.resource_allocation -= shared_resources
    
    def report_to_archon(self):
        """Report status to managing archon."""
        if self.archon_ref:
            # Update archon's goal satisfaction based on our progress
            for goal in self.goals:
                if goal.current_satisfaction > 0.5:
                    # Find corresponding archon goal and update it
                    for archon_goal in self.archon_ref.goals:
                        if self.is_related_goal(goal.name, archon_goal.name):
                            archon_goal.current_satisfaction += 0.05
                            break
    
    def is_related_goal(self, spirit_goal: str, archon_goal: str) -> bool:
        """Check if a spirit goal relates to an archon goal."""
        # Simplified relationship mapping
        relations = {
            "defensive_positioning": ["territorial_control", "force_projection"],
            "exploration_coverage": ["territorial_control", "information_gathering"],
            "resource_collection": ["resource_maximization", "resource_security"]
        }
        
        return archon_goal in relations.get(spirit_goal, [])


# Enhanced Familiar with Spirit Integration
class GrimoireFamiliar:
    """Represents a runtime familiar - a semi-autonomous agent."""
    
    def __init__(self, name: str, familiar_type: str, capabilities: Dict[str, FamiliarCapability]):
        self.name = name
        self.familiar_type = familiar_type
        self.capabilities = capabilities
        self.charge = None  # The entity this familiar manages
        self.spirit_ref: Optional[GrimoireSpirit] = None  # Reference to managing spirit
        self.state = "active"  # active, inactive, dismissed
        self.properties = {}
        self.reactive_behaviors = []
        self.interaction_protocols = []
        
        # Initialize reactive behaviors
        self.initialize_reactive_behaviors()
    
    def initialize_reactive_behaviors(self):
        """Initialize reactive behaviors based on type."""
        if self.familiar_type == "Scout":
            self.reactive_behaviors.extend(["proximity_response", "threat_detection", "path_finding"])
        elif self.familiar_type == "Harvester":
            self.reactive_behaviors.extend(["resource_seeking", "efficiency_optimization", "storage_management"])
        elif self.familiar_type == "Guardian":
            self.reactive_behaviors.extend(["threat_assessment", "defensive_positioning", "ally_protection"])
        else:
            # Default behaviors
            self.reactive_behaviors.extend(["proximity_response", "basic_navigation"])
    
    def autonomous_update(self):
        """Perform autonomous operational-level actions."""
        if self.state != "active":
            return
        
        # Execute reactive behaviors
        for behavior in self.reactive_behaviors:
            self.execute_reactive_behavior(behavior)
        
        # Interact with nearby agents
        self.interact_with_nearby_agents()
        
        # Report to spirit
        self.report_to_spirit()
    
    def execute_reactive_behavior(self, behavior: str):
        """Execute a reactive behavior."""
        if behavior == "proximity_response":
            self.respond_to_proximity()
        elif behavior == "threat_detection":
            self.detect_threats()
        elif behavior == "resource_seeking":
            self.seek_resources()
        elif behavior == "efficiency_optimization":
            self.optimize_efficiency()
    
    def respond_to_proximity(self):
        """React to nearby entities."""
        # Simplified proximity response
        pass
    
    def detect_threats(self):
        """Detect and respond to threats."""
        # Simplified threat detection
        pass
    
    def seek_resources(self):
        """Seek out resources to collect."""
        # Simplified resource seeking
        pass
    
    def optimize_efficiency(self):
        """Optimize operational efficiency."""
        # Simplified efficiency optimization
        pass
    
    def interact_with_nearby_agents(self):
        """Interact with nearby familiars and spirits."""
        # Simplified agent interaction
        pass
    
    def report_to_spirit(self):
        """Report status to managing spirit."""
        if self.spirit_ref:
            # Update spirit's goal satisfaction based on our actions
            for goal in self.spirit_ref.goals:
                if self.contributes_to_goal(goal.name):
                    goal.current_satisfaction += 0.01
    
    def contributes_to_goal(self, goal_name: str) -> bool:
        """Check if this familiar contributes to a goal."""
        # Simplified goal contribution mapping
        contributions = {
            "Scout": ["exploration_coverage", "information_gathering", "threat_assessment"],
            "Harvester": ["resource_collection", "efficiency_optimization"],
            "Guardian": ["defensive_positioning", "threat_assessment", "patrol_completion"]
        }
        
        return goal_name in contributions.get(self.familiar_type, [])
    
    def command(self, command: str, arguments: List[Any]) -> Any:
        """Execute a command on this familiar."""
        if self.state != "active":
            raise RuntimeError(f"Familiar {self.name} is not active")
        
        # Handle built-in commands
        if command == "activate":
            self.state = "active"
            return f"Familiar {self.name} activated"
        elif command == "deactivate":
            self.state = "inactive"
            return f"Familiar {self.name} deactivated"
        elif command == "set_charge":
            if len(arguments) != 1:
                raise RuntimeError("set_charge expects 1 argument (entity)")
            self.charge = arguments[0]
            return f"Familiar {self.name} now manages {self.charge}"
        
        # Look for capability that can handle this command
        for capability in self.capabilities.values():
            try:
                return capability.execute(command, arguments)
            except RuntimeError:
                continue
        
        raise RuntimeError(f"Unknown command '{command}' for familiar {self.name}")
    
    def inquire(self, query: str) -> Any:
        """Handle an inquiry about the familiar's state."""
        if self.state != "active":
            raise RuntimeError(f"Familiar {self.name} is not active")
        
        # Handle built-in queries
        if query == "state":
            return self.state
        elif query == "type":
            return self.familiar_type
        elif query == "charge":
            return self.charge
        elif query == "capabilities":
            return list(self.capabilities.keys())
        elif query == "spirit":
            return self.spirit_ref.name if self.spirit_ref else None
        
        # Look for capability that can handle this query
        for capability in self.capabilities.values():
            try:
                return capability.inquire(query)
            except RuntimeError:
                continue
        
        raise RuntimeError(f"Unknown query '{query}' for familiar {self.name}")
    
    def dismiss(self) -> str:
        """Dismiss this familiar."""
        self.state = "dismissed"
        return f"Familiar {self.name} dismissed"


# Built-in familiar types
FAMILIAR_TYPES = {
    "MemoryImp": lambda: {"memory": MemoryImpCapability()},
    "FileSprite": lambda: {"file": FileSpriteCapability()},
    "LogScribe": lambda: {"log": LogScribeCapability()},
    "Scout": lambda: {},  # Operational scouting
    "Harvester": lambda: {},  # Resource collection
    "Guardian": lambda: {},  # Defensive operations
    "TimeKeeper": lambda: {},  # TODO: Implement time-based capabilities
    "ErrorBanshee": lambda: {},  # TODO: Implement error handling capabilities
}


@dataclass
class BoundMethod:
    """Represents a method bound to an instance."""
    instance: GrimoireInstance
    method: GrimoireFunction
    
    def call(self, interpreter: 'GrimoireInterpreter', arguments: List[Any]) -> Any:
        """Execute the bound method."""
        return self.method.call(interpreter, [self.instance] + arguments)


class Environment:
    """Manages variable scoping and symbol tables."""
    
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any) -> None:
        """Define a new variable."""
        self.values[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable's value."""
        if name in self.values:
            return self.values[name]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def assign(self, name: str, value: Any) -> None:
        """Assign to an existing variable."""
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'")


# =============================================================================
# Control Flow Exceptions
# =============================================================================

class ReturnValue(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value
        super().__init__()


class BreakException(Exception):
    """Exception used to implement break statements."""
    pass


class ContinueException(Exception):
    """Exception used to implement continue statements."""
    pass


# =============================================================================
# Interpreter Implementation
# =============================================================================

class GrimoireInterpreter:
    """Tree-walking interpreter for the Grimoire programming language."""
    
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.familiars = {}  # Active familiars
        self.archons = {}   # Active archons
        self.spirits = {}   # Active spirits
        self.interaction_matrix = InteractionMatrix()  # Agent relationships
        
        # Define built-in functions
        self._define_builtins()
    
    def _define_builtins(self) -> None:
        """Define built-in functions and constants."""
        # Built-in scry function for output
        def scry_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("scry expects exactly 1 argument")
            print(self._grimoire_to_string(arguments[0]))
            return None
        
        # Built-in summon function for creating familiars
        def summon_builtin(interpreter, arguments):
            if len(arguments) < 1:
                raise RuntimeError("summon expects at least 1 argument (familiar type)")
            familiar_type = arguments[0]
            familiar_name = arguments[1] if len(arguments) > 1 else f"{familiar_type.lower()}_familiar"
            
            if familiar_type not in FAMILIAR_TYPES:
                raise RuntimeError(f"Unknown familiar type: {familiar_type}")
            
            capabilities = FAMILIAR_TYPES[familiar_type]()
            familiar = GrimoireFamiliar(familiar_name, familiar_type, capabilities)
            self.familiars[familiar_name] = familiar
            return familiar
        
        # Built-in function for creating archons
        def create_archon_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("create_archon expects 2 arguments (name, domain)")
            archon_name = arguments[0]
            domain = arguments[1]
            
            archon = GrimoireArchon(archon_name, domain)
            self.archons[archon_name] = archon
            return archon
        
        # Built-in function for creating spirits
        def create_spirit_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("create_spirit expects 2 arguments (name, spirit_type)")
            spirit_name = arguments[0]
            spirit_type = arguments[1]
            
            spirit = GrimoireSpirit(spirit_name, spirit_type)
            self.spirits[spirit_name] = spirit
            return spirit
        
        # Built-in function for autonomous updates
        def autonomous_update_builtin(interpreter, arguments):
            # Update all agents autonomously
            for archon in self.archons.values():
                archon.autonomous_update()
            for spirit in self.spirits.values():
                spirit.autonomous_update()
            for familiar in self.familiars.values():
                familiar.autonomous_update()
            return "Autonomous update completed"
        
        self.globals.define("scry", scry_builtin)
        self.globals.define("summon", summon_builtin)
        self.globals.define("create_archon", create_archon_builtin)
        self.globals.define("create_spirit", create_spirit_builtin)
        self.globals.define("autonomous_update", autonomous_update_builtin)
    
    def _grimoire_to_string(self, value: Any) -> str:
        """Convert a Grimoire value to its string representation."""
        if value is None:
            return "void"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float, str)):
            return str(value)
        elif isinstance(value, GrimoireInstance):
            return f"<{value.grimoire_class.name} instance>"
        elif isinstance(value, GrimoireClass):
            return f"<artifact {value.name}>"
        elif isinstance(value, GrimoireFunction):
            return f"<ritual {value.name}>"
        elif isinstance(value, GrimoireFamiliar):
            return f"<familiar {value.name} ({value.familiar_type})>"
        else:
            return str(value)
    
    def interpret(self, program: Program) -> bool:
        """Interpret a Grimoire program."""
        try:
            for statement in program.statements:
                self.execute(statement)
        except RuntimeError as e:
            print(f"Runtime Error: {e}", file=sys.stderr)
            return False
        return True
    
    def execute(self, statement: Statement) -> None:
        """Execute a statement."""
        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
        
        elif isinstance(statement, BindStatement):
            value = None
            if statement.initializer:
                value = self.evaluate(statement.initializer)
            self.environment.define(statement.name, value)
        
        elif isinstance(statement, ScryStatement):
            value = self.evaluate(statement.expression)
            print(self._grimoire_to_string(value))
        
        elif isinstance(statement, IfStatement):
            condition = self.evaluate(statement.condition)
            if self._is_truthy(condition):
                self.execute(statement.then_branch)
            elif statement.else_branch:
                self.execute(statement.else_branch)
        
        elif isinstance(statement, WhileStatement):
            try:
                while self._is_truthy(self.evaluate(statement.condition)):
                    try:
                        self.execute(statement.body)
                    except ContinueException:
                        continue
            except BreakException:
                pass
        
        elif isinstance(statement, ForStatement):
            # For now, implement basic iteration (would need iterable support)
            raise RuntimeError("For loops not yet implemented")
        
        elif isinstance(statement, BlockStatement):
            self.execute_block(statement.statements, Environment(self.environment))
        
        elif isinstance(statement, ReturnStatement):
            value = None
            if statement.value:
                value = self.evaluate(statement.value)
            raise ReturnValue(value)
        
        elif isinstance(statement, BreakStatement):
            raise BreakException()
        
        elif isinstance(statement, ContinueStatement):
            raise ContinueException()
        
        elif isinstance(statement, RitualStatement):
            function = GrimoireFunction(
                statement.name,
                statement.parameters,
                statement.body,
                self.environment
            )
            self.environment.define(statement.name, function)
        
        elif isinstance(statement, ArtifactStatement):
            superclass = None
            if statement.superclass:
                superclass = self.environment.get(statement.superclass)
                if not isinstance(superclass, GrimoireClass):
                    raise RuntimeError("Superclass must be an artifact")
            
            methods = {}
            for method in statement.methods:
                methods[method.name] = GrimoireFunction(
                    method.name,
                    method.parameters,
                    method.body,
                    self.environment
                )
            
            artifact = GrimoireClass(statement.name, superclass, methods)
            self.environment.define(statement.name, artifact)
        
        elif isinstance(statement, FamiliarStatement):
            # Handle familiar definitions - create a familiar type
            methods = {}
            for method in statement.methods:
                methods[method.name] = GrimoireFunction(
                    method.name,
                    method.parameters,
                    method.body,
                    self.environment
                )
            
            # For now, treat custom familiar definitions as creating a new familiar type
            # This is a simplified approach - in a full implementation, you'd want
            # to create a proper familiar class system
            familiar_class = GrimoireClass(statement.name, None, methods)
            self.environment.define(statement.name, familiar_class)
        
        elif isinstance(statement, CommandStatement):
            # Handle familiar commands
            familiar_expr = self.evaluate(statement.familiar)
            
            if isinstance(familiar_expr, GrimoireFamiliar):
                arguments = [self.evaluate(arg) for arg in statement.arguments]
                result = familiar_expr.command(statement.command, arguments)
                # Command results are usually printed or stored somewhere
                if result is not None:
                    print(self._grimoire_to_string(result))
            else:
                raise RuntimeError(f"Can only command familiars, not {type(familiar_expr)}")
        
        else:
            raise RuntimeError(f"Unknown statement type: {type(statement)}")
    
    def execute_block(self, statements: List[Statement], environment: Environment) -> None:
        """Execute a block of statements in a given environment."""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def evaluate(self, expression: Expression) -> Any:
        """Evaluate an expression and return its value."""
        if isinstance(expression, LiteralExpression):
            return expression.value
        
        elif isinstance(expression, IdentifierExpression):
            return self.environment.get(expression.name)
        
        elif isinstance(expression, BinaryExpression):
            left = self.evaluate(expression.left)
            right = self.evaluate(expression.right)
            
            token_type = expression.operator.type
            
            # Arithmetic operators
            if token_type == TokenType.ADDED_TO:
                return left + right
            elif token_type == TokenType.SUBTRACTED_FROM:
                return left - right
            elif token_type == TokenType.MULTIPLIED_BY:
                return left * right
            elif token_type == TokenType.DIVIDED_BY:
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
            elif token_type == TokenType.MODULO:
                return left % right
            elif token_type == TokenType.POWER:
                return left ** right
            
            # Comparison operators
            elif token_type == TokenType.IS_GREATER_THAN:
                return left > right
            elif token_type == TokenType.IS_LESSER_THAN:
                return left < right
            elif token_type == TokenType.IS_NOT_LESSER_THAN:
                return left >= right
            elif token_type == TokenType.IS_NOT_GREATER_THAN:
                return left <= right
            elif token_type == TokenType.IS_EQUAL_TO:
                return self._is_equal(left, right)
            elif token_type == TokenType.IS_NOT_EQUAL_TO:
                return not self._is_equal(left, right)
            
            # Logical operators
            elif token_type == TokenType.AND:
                return self._is_truthy(left) and self._is_truthy(right)
            elif token_type == TokenType.OR:
                return self._is_truthy(left) or self._is_truthy(right)
            
            else:
                raise RuntimeError(f"Unknown binary operator: {expression.operator.lexeme}")
        
        elif isinstance(expression, UnaryExpression):
            operand = self.evaluate(expression.operand)
            
            if expression.operator.type == TokenType.NOT:
                return not self._is_truthy(operand)
            elif expression.operator.type == TokenType.SUBTRACTED_FROM:
                return -operand
            else:
                raise RuntimeError(f"Unknown unary operator: {expression.operator.lexeme}")
        
        elif isinstance(expression, CallExpression):
            callee = self.evaluate(expression.callee)
            
            arguments = []
            for arg in expression.arguments:
                arguments.append(self.evaluate(arg))
            
            if isinstance(callee, GrimoireFunction):
                return callee.call(self, arguments)
            elif isinstance(callee, GrimoireClass):
                return callee.call(self, arguments)
            elif isinstance(callee, BoundMethod):
                return callee.call(self, arguments)
            elif callable(callee):  # Built-in function
                return callee(self, arguments)
            else:
                raise RuntimeError("Can only call functions and classes")
        
        elif isinstance(expression, PropertyAccessExpression):
            obj = self.evaluate(expression.object)
            
            if isinstance(obj, GrimoireInstance):
                return obj.get(expression.property)
            elif isinstance(obj, GrimoireFamiliar):
                # Handle familiar property access for inquiries
                return obj.inquire(expression.property)
            else:
                raise RuntimeError("Only instances and familiars have properties")
        
        elif isinstance(expression, ConjureExpression):
            artifact_class = self.environment.get(expression.artifact_type)
            
            if not isinstance(artifact_class, GrimoireClass):
                raise RuntimeError(f"'{expression.artifact_type}' is not an artifact")
            
            arguments = []
            for arg in expression.arguments:
                arguments.append(self.evaluate(arg))
            
            return artifact_class.call(self, arguments)
        
        elif isinstance(expression, PortalExpression):
            # For now, portal expressions are not implemented
            raise RuntimeError("Portal expressions not yet implemented")
        
        elif isinstance(expression, PropertyAssignmentExpression):
            # Handle property assignment (self.property = value)
            if isinstance(expression.target, PropertyAccessExpression):
                obj = self.evaluate(expression.target.object)
                value = self.evaluate(expression.value)
                
                if isinstance(obj, GrimoireInstance):
                    obj.set(expression.target.property, value)
                    return value
                else:
                    raise RuntimeError("Only instances have properties")
            else:
                raise RuntimeError("Invalid assignment target")
        
        else:
            raise RuntimeError(f"Unknown expression type: {type(expression)}")
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy in Grimoire."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True
    
    def _is_equal(self, left: Any, right: Any) -> bool:
        """Check if two values are equal in Grimoire."""
        return left == right


# =============================================================================
# Convenience Functions
# =============================================================================

def interpret_grimoire(source: str) -> bool:
    """Convenience function to interpret Grimoire source code."""
    from .lexer import GrimoireLexer
    from .parser import GrimoireParser
    
    try:
        # Tokenize
        lexer = GrimoireLexer(source)
        tokens = lexer.scan_tokens()
        
        # Parse
        parser = GrimoireParser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = GrimoireInterpreter()
        return interpreter.interpret(ast)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Example usage
    sample_code = '''
    ritual greet(name):
        scry $SCROLL(Hello, ) added to name
    
    artifact Wizard:
        essence name
        essence mana = 100
        
        ritual invoke(wizard_name):
            bind self.name = wizard_name
            scry $SCROLL(A wizard named ) added to wizard_name added to $SCROLL( appears!)
        
        ritual cast_spell():
            should self.mana is greater than 10:
                diminish self.mana by 10
                scry $SCROLL(Spell cast! Remaining mana: ) added to self.mana
            lest:
                scry $SCROLL(Not enough mana!)
    
    greet upon $SCROLL(World)
    
    bind merlin = conjure Wizard upon $SCROLL(Merlin)
    merlin.cast_spell upon
    merlin.cast_spell upon
    '''
    
    interpret_grimoire(sample_code)