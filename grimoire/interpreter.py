#!/usr/bin/env python3
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
    PropertyAssignmentExpression, TagLiteralExpression, ExpressionStatement, BindStatement, ScryStatement,
    IfStatement, WhileStatement, ForStatement, BlockStatement, ReturnStatement,
    BreakStatement, ContinueStatement,
    RitualStatement, ArtifactStatement, FamiliarStatement, ArchonStatement, SpiritStatement,
    PlaneStatement, ShiftStatement, EffectStatement, CommandStatement, AnomalyStatement
)
from .ai_system import (
    WorldModel, AgentWorldView, Entity, DecisionEngine, GoalEvaluator,
    ExperienceMemory, Action, UtilityFunction,
    create_archon_actions, create_spirit_actions, create_familiar_actions,
    create_utility_functions_for_agent
)
from .planes import PlaneManager, PlaneProperties, PlaneType, get_plane_manager


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
# Activity Reporting and Monitoring System
# =============================================================================

@dataclass
class Activity:
    """Represents an activity performed by a familiar."""
    timestamp: float
    familiar_name: str
    activity_type: str  # "self", "inter_familiar", "environmental", "command"
    description: str
    details: Dict[str, Any]
    
    def is_self(self) -> bool:
        """Check if this is a self-activity (internal processing)."""
        return self.activity_type == "self"
    
    def is_inter_familiar(self) -> bool:
        """Check if this involves interaction with other familiars."""
        return self.activity_type == "inter_familiar"
    
    def is_environmental(self) -> bool:
        """Check if this involves environmental interaction."""
        return self.activity_type == "environmental"
    
    def is_command(self) -> bool:
        """Check if this is a command execution."""
        return self.activity_type == "command"


class FamiliarWrangler:
    """Centralized manager for familiar reporting and monitoring."""
    
    def __init__(self):
        self.active_familiars: List['GrimoireFamiliar'] = []
        self.reporting_settings: Dict[str, Dict[str, Any]] = {}
        self.global_reports: List[Activity] = []
        self.is_active = True
    
    def register_familiar(self, familiar: 'GrimoireFamiliar') -> str:
        """Register a familiar for potential monitoring."""
        if familiar not in self.active_familiars:
            self.active_familiars.append(familiar)
            familiar.wrangler_ref = self
            return f"Familiar {familiar.name} registered with wrangler"
        return f"Familiar {familiar.name} already registered"
    
    def unregister_familiar(self, familiar: 'GrimoireFamiliar') -> str:
        """Unregister a familiar from monitoring."""
        if familiar in self.active_familiars:
            self.active_familiars.remove(familiar)
            familiar.wrangler_ref = None
            familiar.disable_reporting()
            return f"Familiar {familiar.name} unregistered from wrangler"
        return f"Familiar {familiar.name} not found in registry"
    
    def enable_reporting(self, familiar: 'GrimoireFamiliar', report_type: str = "all") -> str:
        """Enable reporting for a specific familiar."""
        if familiar not in self.active_familiars:
            self.register_familiar(familiar)
        
        familiar.enable_reporting(report_type)
        self.reporting_settings[familiar.name] = {
            "type": report_type,
            "enabled": True,
            "start_time": __import__('time').time()
        }
        return f"Reporting enabled for {familiar.name} (type: {report_type})"
    
    def disable_reporting(self, familiar: 'GrimoireFamiliar') -> str:
        """Disable reporting for a specific familiar."""
        familiar.disable_reporting()
        if familiar.name in self.reporting_settings:
            self.reporting_settings[familiar.name]["enabled"] = False
        return f"Reporting disabled for {familiar.name}"
    
    def enable_all_reporting(self, report_type: str = "all") -> str:
        """Enable reporting for all registered familiars."""
        enabled_count = 0
        for familiar in self.active_familiars:
            if familiar.state == "active":
                self.enable_reporting(familiar, report_type)
                enabled_count += 1
        return f"Reporting enabled for {enabled_count} familiars"
    
    def disable_all_reporting(self) -> str:
        """Disable reporting for all familiars."""
        disabled_count = 0
        for familiar in self.active_familiars:
            if familiar.is_reporting:
                self.disable_reporting(familiar)
                disabled_count += 1
        return f"Reporting disabled for {disabled_count} familiars"
    
    def get_report(self, familiar_name: Optional[str] = None) -> List[Activity]:
        """Get activity reports from familiars."""
        if familiar_name:
            # Get report from specific familiar
            for familiar in self.active_familiars:
                if familiar.name == familiar_name and familiar.is_reporting_enabled():
                    return familiar.get_report()
            return []
        else:
            # Get reports from all reporting familiars
            all_reports = []
            for familiar in self.active_familiars:
                if familiar.is_reporting_enabled():
                    all_reports.extend(familiar.get_report())
            return sorted(all_reports, key=lambda a: a.timestamp)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of wrangler status and activity."""
        total_familiars = len(self.active_familiars)
        reporting_familiars = len([f for f in self.active_familiars if f.is_reporting])
        active_familiars = len([f for f in self.active_familiars if f.state == "active"])
        
        total_activities = sum(len(f.activity_log) for f in self.active_familiars)
        
        return {
            "total_familiars": total_familiars,
            "active_familiars": active_familiars,
            "reporting_familiars": reporting_familiars,
            "total_activities_logged": total_activities,
            "wrangler_active": self.is_active,
            "reporting_settings": self.reporting_settings.copy()
        }
    
    def clear_reports(self, familiar_name: Optional[str] = None) -> str:
        """Clear activity reports."""
        if familiar_name:
            for familiar in self.active_familiars:
                if familiar.name == familiar_name:
                    familiar.clear_activity_log()
                    return f"Reports cleared for {familiar_name}"
            return f"Familiar {familiar_name} not found"
        else:
            cleared_count = 0
            for familiar in self.active_familiars:
                if familiar.activity_log:
                    familiar.clear_activity_log()
                    cleared_count += 1
            return f"Reports cleared for {cleared_count} familiars"
    
    def filter_activities(self, activity_type: Optional[str] = None, 
                         time_range: Optional[tuple] = None) -> List[Activity]:
        """Filter activities by type and/or time range."""
        all_activities = self.get_report()
        
        filtered = all_activities
        
        if activity_type:
            filtered = [a for a in filtered if a.activity_type == activity_type]
        
        if time_range:
            start_time, end_time = time_range
            filtered = [a for a in filtered if start_time <= a.timestamp <= end_time]
        
        return filtered
    
    def get_familiar_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each familiar."""
        stats = {}
        for familiar in self.active_familiars:
            activity_counts = {}
            for activity in familiar.activity_log:
                activity_type = activity.activity_type
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
            
            stats[familiar.name] = {
                "type": familiar.familiar_type,
                "state": familiar.state,
                "is_reporting": familiar.is_reporting,
                "report_type": familiar.report_type,
                "total_activities": len(familiar.activity_log),
                "activity_breakdown": activity_counts,
                "spirit": familiar.spirit_ref.name if familiar.spirit_ref else None
            }
        
        return stats


# =============================================================================
# Pact System: Spiritual Agreements and Domain Authority
# =============================================================================

@dataclass
class Pact:
    """Represents a binding agreement between a spirit and familiar."""
    spirit_name: str
    familiar_true_name: str
    pact_terms: List[str]  # Actions/permissions granted
    domain: str
    creation_timestamp: float
    conditions: Dict[str, Any]  # Additional pact conditions
    
    def is_action_permitted(self, action: str) -> bool:
        """Check if an action is permitted under this pact."""
        return action in self.pact_terms or "all_actions" in self.pact_terms
    
    def violates_conditions(self, familiar_state: Dict[str, Any]) -> bool:
        """Check if familiar state violates pact conditions."""
        for condition, expected_value in self.conditions.items():
            if condition in familiar_state:
                if familiar_state[condition] != expected_value:
                    return True
        return False


class PactRegistry:
    """Global registry of all active pacts in the system."""
    
    def __init__(self):
        self.active_pacts: Dict[str, Pact] = {}  # familiar_true_name -> pact
        self.spirit_pacts: Dict[str, List[str]] = {}  # spirit_name -> [familiar_names]
    
    def register_pact(self, pact: Pact) -> str:
        """Register a new pact in the system."""
        self.active_pacts[pact.familiar_true_name] = pact
        
        if pact.spirit_name not in self.spirit_pacts:
            self.spirit_pacts[pact.spirit_name] = []
        self.spirit_pacts[pact.spirit_name].append(pact.familiar_true_name)
        
        return f"Pact registered between {pact.spirit_name} and {pact.familiar_true_name}"
    
    def revoke_pact(self, spirit_name: str, familiar_true_name: str) -> str:
        """Revoke a pact from the registry."""
        if familiar_true_name in self.active_pacts:
            pact = self.active_pacts[familiar_true_name]
            if pact.spirit_name == spirit_name:
                del self.active_pacts[familiar_true_name]
                if spirit_name in self.spirit_pacts:
                    self.spirit_pacts[spirit_name].remove(familiar_true_name)
                return f"Pact revoked between {spirit_name} and {familiar_true_name}"
            else:
                raise RuntimeError(f"Only spirit {pact.spirit_name} can revoke this pact")
        return f"No pact found for {familiar_true_name}"
    
    def get_pact(self, familiar_true_name: str) -> Optional[Pact]:
        """Get the pact for a familiar."""
        return self.active_pacts.get(familiar_true_name)
    
    def get_spirit_pacts(self, spirit_name: str) -> List[Pact]:
        """Get all pacts managed by a spirit."""
        if spirit_name not in self.spirit_pacts:
            return []
        return [self.active_pacts[familiar_name] for familiar_name in self.spirit_pacts[spirit_name]]
    
    def is_action_permitted(self, spirit_name: str, familiar_true_name: str, action: str) -> bool:
        """Check if a spirit can perform an action on a familiar under their pact."""
        pact = self.get_pact(familiar_true_name)
        if not pact or pact.spirit_name != spirit_name:
            return False
        return pact.is_action_permitted(action)


class ForbiddenActionError(Exception):
    """Raised when a spirit attempts an action not permitted by pact."""
    pass


class NoPactError(Exception):
    """Raised when trying to invoke a pact that doesn't exist."""
    pass


class DomainViolationError(Exception):
    """Raised when a familiar violates its spirit's domain rules."""
    pass


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
    
    def __init__(self, name: str, domain: str, world_model: Optional[WorldModel] = None):
        super().__init__()
        self.name = name
        self.domain = domain
        self.spirits: List['GrimoireSpirit'] = []
        self.resource_budget = 1000
        self.strategic_goals: List[str] = []
        self.methods: Dict[str, GrimoireFunction] = {}
        self.state = "active"
        
        # Enhanced AI Components
        self.decision_engine = DecisionEngine(f"archon_{name}")
        self.goal_evaluator = GoalEvaluator()
        self.world_model = world_model
        self.world_view: Optional[AgentWorldView] = None
        self.agent_state = {
            "controlled_territory": 10,
            "total_resources": 160,
            "military_strength": 20,
            "defensive_strength": 15,
            "ally_count": 0,
            "reputation": 0,
            "diplomatic_power": 25,
            "spirit_count": 0,
            "economic_efficiency": 0.5,
            "resource_production_rate": 5
        }
        
        # Initialize domain-specific goals and AI system
        self.initialize_strategic_goals()
        self.initialize_ai_system()
    
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
    
    def initialize_ai_system(self):
        """Initialize the enhanced AI decision-making system."""
        # Add available actions based on archon type
        for action in create_archon_actions():
            self.decision_engine.add_action(action)
        
        # Add utility functions based on domain
        utility_functions = create_utility_functions_for_agent("archon", self.domain)
        for goal_name, utility_fn in utility_functions.items():
            self.decision_engine.add_utility_function(goal_name, utility_fn)
        
        # Update world view if world model is available
        if self.world_model:
            # Add archon as entity in world model
            archon_entity = Entity(
                id=f"archon_{self.name}",
                type="archon",
                position=(50, 50),  # Default starting position
                properties={"domain": self.domain, "name": self.name}
            )
            self.world_model.add_entity(archon_entity)
            self.world_view = self.world_model.get_agent_view(f"archon_{self.name}", vision_range=10)
    
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
        """Perform autonomous strategic decision making with enhanced AI."""
        if self.state != "active":
            return
        
        # Update world state perception
        self.update_world_state()
        
        # Update goal satisfaction based on objective measures
        self.update_goal_satisfaction_ai()
        
        # Get priority goal and make intelligent decision
        priority_goal = self.get_priority_goal()
        if priority_goal:
            # Use decision engine to select best action
            chosen_action = self.decision_engine.decide_action(priority_goal.name)
            if chosen_action:
                initial_state = self.agent_state.copy()
                self.execute_ai_action(chosen_action)
                final_state = self.agent_state.copy()
                
                # Record experience for learning
                utility_change = self.calculate_utility_change(initial_state, final_state, priority_goal.name)
                self.decision_engine.memory.record_experience(
                    initial_state, chosen_action, final_state, utility_change
                )
            else:
                # Fallback to basic action
                self.execute_strategic_action(priority_goal)
        
        # Update spirits
        for spirit in self.spirits:
            spirit.autonomous_update()
        
        # Resource allocation with AI considerations
        self.allocate_resources_ai()
    
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
    
    def update_world_state(self):
        """Update agent's perception of the world state."""
        # Update world view if available
        if self.world_model:
            self.world_view = self.world_model.get_agent_view(f"archon_{self.name}", vision_range=10)
        
        # Update agent state based on current situation
        self.agent_state.update({
            "controlled_territory": self.calculate_territory_control(),
            "total_resources": self.calculate_total_resources(),
            "spirit_count": len(self.spirits),
            "military_strength": self.calculate_military_strength(),
            "ally_count": self.calculate_ally_count(),
            "reputation": self.agent_state.get("reputation", 0),
            "diplomatic_power": self.agent_state.get("diplomatic_power", 25)
        })
        
        # Update decision engine world state
        self.decision_engine.update_world_state(self.agent_state)
    
    def update_goal_satisfaction_ai(self):
        """Update goal satisfaction using objective AI evaluation."""
        for goal in self.goals:
            if self.world_view:
                satisfaction = self.goal_evaluator.evaluate_goal(
                    goal.name, self.agent_state, self.world_view
                )
                goal.current_satisfaction = satisfaction
    
    def execute_ai_action(self, action: Action):
        """Execute an AI-selected action."""
        if action.name == "expand_territory":
            self.expand_territory_ai()
        elif action.name == "form_alliance":
            self.form_alliance_ai()
        elif action.name == "build_infrastructure":
            self.build_infrastructure_ai()
        elif action.name == "recruit_spirits":
            self.recruit_spirits_ai()
        else:
            # Fallback to basic execution
            self.execute_strategic_action_by_name(action.name)
    
    def calculate_utility_change(self, initial_state: Dict[str, Any], 
                               final_state: Dict[str, Any], goal_name: str) -> float:
        """Calculate utility change from action execution."""
        if goal_name not in self.decision_engine.utility_functions:
            return 0.0
        
        utility_fn = self.decision_engine.utility_functions[goal_name]
        initial_utility = utility_fn.evaluate(initial_state)
        final_utility = utility_fn.evaluate(final_state)
        
        return final_utility - initial_utility
    
    def allocate_resources_ai(self):
        """Allocate resources using AI-driven decisions."""
        if self.resource_budget > 0 and self.spirits:
            # Priority-based allocation
            spirit_priorities = []
            for spirit in self.spirits:
                priority_goal = spirit.get_priority_goal()
                priority = priority_goal.priority if priority_goal else 1
                spirit_priorities.append((spirit, priority))
            
            # Sort by priority
            spirit_priorities.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate more resources to higher priority spirits
            total_priority = sum(p[1] for p in spirit_priorities)
            for spirit, priority in spirit_priorities:
                allocation = int(self.resource_budget * (priority / total_priority))
                spirit.resource_allocation = allocation
    
    # Enhanced action implementations
    def expand_territory_ai(self):
        """AI-enhanced territorial expansion."""
        self.agent_state["controlled_territory"] += 5
        self.agent_state["total_resources"] -= 25
        if len([s for s in self.spirits if s.spirit_type == "Guardian"]) < 2:
            self.summon_spirit("Guardian", ["defend_territory", "patrol_borders"])
    
    def form_alliance_ai(self):
        """AI-enhanced alliance formation."""
        self.agent_state["ally_count"] += 1
        self.agent_state["diplomatic_power"] -= 5
        self.agent_state["reputation"] += 10
    
    def build_infrastructure_ai(self):
        """AI-enhanced infrastructure building."""
        self.agent_state["economic_efficiency"] += 0.1
        self.agent_state["total_resources"] -= 100
        self.agent_state["resource_production_rate"] += 2
    
    def recruit_spirits_ai(self):
        """AI-enhanced spirit recruitment."""
        spirit_type = self.determine_needed_spirit_type()
        objectives = self.generate_spirit_objectives(spirit_type)
        self.summon_spirit(spirit_type, objectives)
        self.agent_state["total_resources"] -= 30
    
    # Helper calculation methods
    def calculate_territory_control(self) -> int:
        """Calculate current territorial control."""
        base_territory = 10
        spirit_bonus = len(self.spirits) * 2
        return base_territory + spirit_bonus
    
    def calculate_total_resources(self) -> int:
        """Calculate total available resources."""
        return self.resource_budget + sum(spirit.resource_allocation for spirit in self.spirits)
    
    def calculate_military_strength(self) -> int:
        """Calculate military strength based on spirits."""
        guardian_count = len([s for s in self.spirits if s.spirit_type == "Guardian"])
        return 20 + guardian_count * 10
    
    def calculate_ally_count(self) -> int:
        """Calculate number of allies."""
        return self.agent_state.get("ally_count", 0)
    
    def determine_needed_spirit_type(self) -> str:
        """Determine what type of spirit is most needed."""
        guardian_count = len([s for s in self.spirits if s.spirit_type == "Guardian"])
        scout_count = len([s for s in self.spirits if s.spirit_type == "Scout"])
        harvester_count = len([s for s in self.spirits if s.spirit_type == "Harvester"])
        
        if self.domain == "Combat" and guardian_count < 2:
            return "Guardian"
        elif self.domain == "Economy" and harvester_count < 1:
            return "Harvester"
        elif scout_count < 1:
            return "Scout"
        else:
            return "Guardian"  # Default
    
    def generate_spirit_objectives(self, spirit_type: str) -> List[str]:
        """Generate objectives for a new spirit based on type and domain."""
        if spirit_type == "Guardian":
            return ["defend_territory", "patrol_borders", "threat_assessment"]
        elif spirit_type == "Scout":
            return ["exploration", "intelligence_gathering", "reconnaissance"]
        elif spirit_type == "Harvester":
            return ["resource_collection", "site_security", "efficiency_optimization"]
        else:
            return ["general_support", "coordination"]
    
    def execute_strategic_action_by_name(self, action_name: str):
        """Execute strategic action by name (fallback method)."""
        if action_name == "expand_territory":
            self.expand_territory()
        elif action_name == "form_alliance":
            self.seek_alliances()
        elif action_name == "build_infrastructure":
            self.optimize_resource_gathering()
        elif action_name == "recruit_spirits":
            spirit_type = self.determine_needed_spirit_type()
            objectives = self.generate_spirit_objectives(spirit_type)
            self.summon_spirit(spirit_type, objectives)


class GrimoireSpirit(GoalSeeker):
    """Tactical-level AI agent that manages multiple familiars."""
    
    def __init__(self, name: str, spirit_type: str, domain: str = "general"):
        super().__init__()
        self.name = name
        self.spirit_type = spirit_type
        self.domain = domain  # Spirit's domain of authority
        self.archon_ref: Optional[GrimoireArchon] = None
        self.familiars: List['GrimoireFamiliar'] = []
        self.resource_allocation = 0
        self.cooperation_network: List['GrimoireSpirit'] = []
        self.methods: Dict[str, GrimoireFunction] = {}
        self.state = "active"
        self.pact_registry_ref: Optional[PactRegistry] = None
        
        # Pact management
        self.pacts: Dict[str, Pact] = {}  # familiar_true_name -> pact
        self.domain_rules: Dict[str, Any] = {}
        
        # Initialize type-specific behaviors and domain rules
        self.initialize_tactical_behaviors()
        self.initialize_domain_rules()
    
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
    
    def initialize_domain_rules(self):
        """Initialize domain-specific rules and authorities."""
        if self.domain == "reality":
            self.domain_rules = {
                "enforce_physics": True,
                "monitor_anomalies": True,
                "correction_authority": ["position", "velocity", "state"]
            }
        elif self.domain == "security":
            self.domain_rules = {
                "access_control": True,
                "threat_detection": True,
                "correction_authority": ["permissions", "access_level", "security_state"]
            }
        elif self.domain == "resources":
            self.domain_rules = {
                "allocation_control": True,
                "efficiency_monitoring": True,
                "correction_authority": ["resource_usage", "allocation", "efficiency"]
            }
        elif self.domain == "communication":
            self.domain_rules = {
                "message_routing": True,
                "protocol_enforcement": True,
                "correction_authority": ["message_format", "routing", "protocol"]
            }
        else:
            # General domain
            self.domain_rules = {
                "general_oversight": True,
                "correction_authority": ["state", "behavior"]
            }
    
    def spawn_familiar(self, familiar_type: str, objectives: List[str]) -> 'GrimoireFamiliar':
        """Create and manage a new familiar without pact."""
        capabilities = FAMILIAR_TYPES.get(familiar_type, lambda: {})()
        familiar = GrimoireFamiliar(f"{self.name}_{familiar_type}_{len(self.familiars)}", familiar_type, capabilities)
        familiar.spirit_ref = self
        
        self.familiars.append(familiar)
        return familiar
    
    def create_familiar_with_pact(self, familiar_type: str, pact_terms: List[str], 
                                  pact_conditions: Optional[Dict[str, Any]] = None) -> 'GrimoireFamiliar':
        """Create a new familiar and establish a pact during initialization."""
        capabilities = FAMILIAR_TYPES.get(familiar_type, lambda: {})()
        familiar_name = f"{self.name}_{familiar_type}_{len(self.familiars)}"
        
        # Generate true name (immutable identifier)
        import hashlib
        true_name = hashlib.sha256(f"{familiar_name}_{self.name}_{__import__('time').time()}".encode()).hexdigest()[:16]
        
        familiar = GrimoireFamiliar(familiar_name, familiar_type, capabilities, true_name=true_name)
        familiar.spirit_ref = self
        
        # Create pact during initialization (security requirement)
        pact = Pact(
            spirit_name=self.name,
            familiar_true_name=true_name,
            pact_terms=pact_terms,
            domain=self.domain,
            creation_timestamp=__import__('time').time(),
            conditions=pact_conditions or {}
        )
        
        # Register pact
        if self.pact_registry_ref:
            self.pact_registry_ref.register_pact(pact)
        self.pacts[true_name] = pact
        familiar.add_pact(pact)
        
        self.familiars.append(familiar)
        return familiar
    
    def revoke_pact(self, familiar_true_name: str) -> str:
        """Revoke a pact with a familiar."""
        if familiar_true_name in self.pacts:
            if self.pact_registry_ref:
                self.pact_registry_ref.revoke_pact(self.name, familiar_true_name)
            del self.pacts[familiar_true_name]
            
            # Find and update the familiar
            for familiar in self.familiars:
                if familiar.true_name == familiar_true_name:
                    familiar.remove_pact(self.name)
                    break
            
            return f"Pact revoked with {familiar_true_name}"
        return f"No pact found with {familiar_true_name}"
    
    def invoke_pact(self, familiar_true_name: str, action: str, *args) -> Any:
        """Invoke a pact to perform an action on a familiar."""
        if familiar_true_name not in self.pacts:
            raise NoPactError(f"No pact exists with {familiar_true_name}")
        
        pact = self.pacts[familiar_true_name]
        if not pact.is_action_permitted(action):
            raise ForbiddenActionError(f"Action '{action}' not permitted under pact with {familiar_true_name}")
        
        # Find the familiar
        familiar = None
        for f in self.familiars:
            if f.true_name == familiar_true_name:
                familiar = f
                break
        
        if not familiar:
            raise RuntimeError(f"Familiar with true name {familiar_true_name} not found")
        
        # Perform the action based on pact terms
        if action == "command":
            return familiar.command(args[0], list(args[1:]))
        elif action == "modify_state":
            familiar.properties.update(args[0])
            return f"State modified for {familiar_true_name}"
        elif action == "relocate":
            familiar.properties["position"] = args[0]
            return f"Relocated {familiar_true_name}"
        elif action == "deactivate":
            familiar.state = "inactive"
            return f"Deactivated {familiar_true_name}"
        elif action == "activate":
            familiar.state = "active"
            return f"Activated {familiar_true_name}"
        else:
            # Custom action - delegate to familiar
            return familiar.execute_pact_action(action, args)
    
    def oversee_domain(self):
        """Monitor familiars in domain and correct violations."""
        violations_corrected = 0
        
        for familiar in self.familiars:
            if familiar.true_name in self.pacts:
                pact = self.pacts[familiar.true_name]
                familiar_state = {
                    "state": familiar.state,
                    "position": familiar.properties.get("position"),
                    "behavior": familiar.properties.get("current_behavior"),
                    **familiar.properties
                }
                
                if pact.violates_conditions(familiar_state):
                    self.correct_familiar_state(familiar, pact)
                    violations_corrected += 1
        
        return f"Domain oversight complete. {violations_corrected} violations corrected."
    
    def correct_familiar_state(self, familiar: 'GrimoireFamiliar', pact: Pact):
        """Correct a familiar's state to comply with pact conditions."""
        # Apply domain-specific corrections
        correction_authority = self.domain_rules.get("correction_authority", [])
        
        for condition, expected_value in pact.conditions.items():
            if condition in correction_authority:
                if condition in familiar.properties:
                    familiar.properties[condition] = expected_value
                elif condition == "state":
                    familiar.state = expected_value
        
        familiar.log_activity("domain_correction", 
                            f"State corrected by spirit {self.name}",
                            {"domain": self.domain, "corrections": pact.conditions})
    
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


# Enhanced Familiar with Spirit Integration and Reporting
class GrimoireFamiliar:
    """Represents a runtime familiar - a semi-autonomous agent."""
    
    def __init__(self, name: str, familiar_type: str, capabilities: Dict[str, FamiliarCapability], true_name: Optional[str] = None):
        self.name = name
        self.familiar_type = familiar_type
        self.capabilities = capabilities
        
        # True name - immutable identifier for pact security
        if true_name:
            self.true_name = true_name
        else:
            # Generate true name automatically if not provided
            import hashlib
            self.true_name = hashlib.sha256(f"{name}_{familiar_type}_{__import__('time').time()}".encode()).hexdigest()[:16]
        
        self.charge = None  # The entity this familiar manages
        self.spirit_ref: Optional[GrimoireSpirit] = None  # Reference to managing spirit
        self.wrangler_ref: Optional[FamiliarWrangler] = None  # Reference to wrangler
        self.state = "active"  # active, inactive, dismissed
        self.properties = {}
        self.reactive_behaviors = []
        self.interaction_protocols = []
        
        # Pact system - familiars can have multiple pacts with different spirits
        self.pacts: Dict[str, Pact] = {}  # spirit_name -> pact
        
        # Reporting system
        self.is_reporting = False
        self.report_type = "none"  # "none", "all", "self", "inter", "environmental", "command"
        self.activity_log: List[Activity] = []
        
        # --- Socket system -------------------------------------------------
        # Sockets are lazily created via `add_socket`.  Keys are socket names.
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from .sockets import Socket  # pragma: no cover
        self.sockets: Dict[str, "Socket"] = {}
        # ---------------------------------------------------------------

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
        
        self.log_activity("self", "Starting autonomous update", {"behaviors": len(self.reactive_behaviors)})
        
        # Execute reactive behaviors
        for behavior in self.reactive_behaviors:
            self.execute_reactive_behavior(behavior)
        
        # Interact with nearby agents
        self.interact_with_nearby_agents()
        
        # Report to spirit
        self.report_to_spirit()
        
        self.log_activity("self", "Completed autonomous update", {})
    
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
        
        self.log_activity("command", f"Executing command: {command}", {"arguments": arguments})
        
        # Handle built-in commands
        if command == "activate":
            self.state = "active"
            self.log_activity("self", "Activated", {"previous_state": "inactive"})
            return f"Familiar {self.name} activated"
        elif command == "deactivate":
            self.state = "inactive"
            self.log_activity("self", "Deactivated", {"previous_state": "active"})
            return f"Familiar {self.name} deactivated"
        elif command == "set_charge":
            if len(arguments) != 1:
                raise RuntimeError("set_charge expects 1 argument (entity)")
            old_charge = self.charge
            self.charge = arguments[0]
            self.log_activity("self", "Charge assigned", {"old_charge": old_charge, "new_charge": self.charge})
            return f"Familiar {self.name} now manages {self.charge}"
        
        # Look for capability that can handle this command
        for capability in self.capabilities.values():
            try:
                result = capability.execute(command, arguments)
                self.log_activity("command", f"Command executed successfully: {command}", {"result": result})
                return result
            except RuntimeError:
                continue
        
        self.log_activity("command", f"Command failed: {command}", {"error": "unknown command"})
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
        elif query == "sockets":
            return list(self.sockets.keys())
        # New: allow querying for a specific socket object or its value
        elif query.endswith("_socket") and query[:-7] in self.sockets:
            return self.sockets[query[:-7]]
        elif query in self.sockets:
            return self.sockets[query]
        
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
        self.disable_reporting()
        return f"Familiar {self.name} dismissed"
    
    # =============================================================================
    # Reporting System Methods
    # =============================================================================
    
    def enable_reporting(self, report_type: str = "all") -> str:
        """Enable activity reporting for this familiar."""
        self.is_reporting = True
        self.report_type = report_type
        self.log_activity("self", f"Reporting enabled (type: {report_type})", {"previous_state": "disabled"})
        return f"Reporting enabled for {self.name}"
    
    def disable_reporting(self) -> str:
        """Disable activity reporting for this familiar."""
        if self.is_reporting:
            self.log_activity("self", "Reporting disabled", {"activities_logged": len(self.activity_log)})
        self.is_reporting = False
        self.report_type = "none"
        return f"Reporting disabled for {self.name}"
    
    def is_reporting_enabled(self) -> bool:
        """Check if reporting is currently enabled."""
        return self.is_reporting and self.state == "active"
    
    def log_activity(self, activity_type: str, description: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an activity if reporting is enabled."""
        if not self.is_reporting:
            return
        
        # Check if this activity type should be logged based on report_type
        should_log = False
        
        if self.report_type == "all":
            should_log = True
        elif self.report_type == "self" and activity_type == "self":
            should_log = True
        elif self.report_type == "inter" and activity_type == "inter_familiar":
            should_log = True
        elif self.report_type == "environmental" and activity_type == "environmental":
            should_log = True
        elif self.report_type == "command" and activity_type == "command":
            should_log = True
        elif self.report_type == activity_type:  # Exact match
            should_log = True
        
        if should_log:
            activity = Activity(
                timestamp=__import__('time').time(),
                familiar_name=self.name,
                activity_type=activity_type,
                description=description,
                details=details or {}
            )
            self.activity_log.append(activity)
            
            # Limit activity log size to prevent memory issues
            if len(self.activity_log) > 1000:
                self.activity_log = self.activity_log[-500:]  # Keep last 500 activities
    
    def get_report(self) -> List[Activity]:
        """Get the current activity report."""
        return self.activity_log.copy()
    
    def clear_activity_log(self) -> str:
        """Clear the activity log."""
        cleared_count = len(self.activity_log)
        self.activity_log.clear()
        return f"Cleared {cleared_count} activities from {self.name}"
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get a summary of logged activities."""
        if not self.activity_log:
            return {"total": 0, "by_type": {}, "latest": None}
        
        by_type = {}
        for activity in self.activity_log:
            by_type[activity.activity_type] = by_type.get(activity.activity_type, 0) + 1
        
        return {
            "total": len(self.activity_log),
            "by_type": by_type,
            "latest": self.activity_log[-1].description if self.activity_log else None,
            "reporting_type": self.report_type,
            "is_reporting": self.is_reporting
        }
    
    # =============================================================================
    # Pact System Methods
    # =============================================================================
    
    def add_pact(self, pact: Pact) -> str:
        """Add a pact with a spirit (only during initialization)."""
        if pact.spirit_name in self.pacts:
            return f"Pact with {pact.spirit_name} already exists"
        
        self.pacts[pact.spirit_name] = pact
        self.log_activity("pact", f"Pact established with spirit {pact.spirit_name}", 
                         {"domain": pact.domain, "terms": pact.pact_terms})
        return f"Pact established with spirit {pact.spirit_name}"
    
    def remove_pact(self, spirit_name: str) -> str:
        """Remove a pact with a spirit."""
        if spirit_name in self.pacts:
            del self.pacts[spirit_name]
            self.log_activity("pact", f"Pact removed with spirit {spirit_name}", {})
            return f"Pact removed with spirit {spirit_name}"
        return f"No pact found with spirit {spirit_name}"
    
    def has_pact_with(self, spirit_name: str) -> bool:
        """Check if this familiar has a pact with a specific spirit."""
        return spirit_name in self.pacts
    
    def get_pact_terms(self, spirit_name: str) -> List[str]:
        """Get the terms of a pact with a specific spirit."""
        if spirit_name in self.pacts:
            return self.pacts[spirit_name].pact_terms
        return []
    
    def execute_pact_action(self, action: str, args: tuple) -> Any:
        """Execute a custom pact action."""
        self.log_activity("pact_action", f"Executing pact action: {action}", {"args": args})
        
        # Custom actions can be implemented here based on familiar type
        if action == "transform_state":
            old_state = self.state
            self.state = args[0] if args else "transformed"
            return f"State transformed from {old_state} to {self.state}"
        elif action == "modify_behavior":
            behavior_name = args[0] if args else "default"
            if behavior_name not in self.reactive_behaviors:
                self.reactive_behaviors.append(behavior_name)
            return f"Behavior {behavior_name} added"
        elif action == "grant_capability":
            capability_name = args[0] if args else "generic"
            # This would add new capabilities to the familiar
            return f"Capability {capability_name} granted"
        else:
            return f"Unknown pact action: {action}"
    
    def get_pact_summary(self) -> Dict[str, Any]:
        """Get a summary of all pacts for this familiar."""
        return {
            "true_name": self.true_name,
            "total_pacts": len(self.pacts),
            "spirit_pacts": {
                spirit_name: {
                    "domain": pact.domain,
                    "terms": pact.pact_terms,
                    "creation_time": pact.creation_timestamp
                }
                for spirit_name, pact in self.pacts.items()
            }
        }

    # ---------------------------------------------------------------------
    # Socket helpers
    # ---------------------------------------------------------------------
    def add_socket(self, name: str, *, data_type: str | None = None, direction: str = "input"):
        """Create a socket attached to this familiar.

        Returns the newly created socket so callers can chain operations
        or connect immediately.
        """
        from .sockets import Socket  # Local import to avoid cycles

        if name in self.sockets:
            raise RuntimeError(f"Socket '{name}' already exists on {self.name}")
        sock = Socket(self, name, data_type, direction=direction)
        self.sockets[name] = sock
        return sock

    def get_socket(self, name: str):
        """Return socket by *name* or raise."""
        if name not in self.sockets:
            raise RuntimeError(f"Socket '{name}' not found on {self.name}")
        return self.sockets[name]

    def send_to_socket(self, name: str, data):
        """Convenience wrapper for `self.get_socket(name).send(data)`."""
        sock = self.get_socket(name)
        sock.send(data)

    def receive_from_socket(self, name: str):
        """Return latest value received on socket (or None)."""
        sock = self.get_socket(name)
        val = sock.value
        # If structured message, log receipt
        from grimoire.messaging import is_message
        if is_message(val):
            self.log_activity("inter_familiar", "Message received", {"message": str(val)})
        return val


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
        self.familiar_wrangler = FamiliarWrangler()  # Familiar monitoring system
        self.pact_registry = PactRegistry()  # Global pact registry
        self.plane_manager = get_plane_manager()  # Planar system
        
        # Enhanced AI system components
        self.world_model = WorldModel(width=100, height=100)  # 100x100 world grid
        
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

            # Try specialised familiar class registry first
            try:
                from grimoire.familiars import get_familiar_class  # Local import
                FamiliarCls = get_familiar_class(familiar_type)
            except Exception:  # pragma: no cover
                FamiliarCls = None

            if FamiliarCls and FamiliarCls.__name__ != "GrimoireFamiliar":
                familiar = FamiliarCls(familiar_name)
            else:
                if familiar_type not in FAMILIAR_TYPES:
                    raise RuntimeError(f"Unknown familiar type: {familiar_type}")
                capabilities = FAMILIAR_TYPES[familiar_type]()
                familiar = GrimoireFamiliar(familiar_name, familiar_type, capabilities)

            self.familiars[familiar_name] = familiar
            self.familiar_wrangler.register_familiar(familiar)
            return familiar
        
        # Enhanced familiar creation functions
        def create_entity_familiar_builtin(interpreter, arguments):
            """create_entity_familiar(name, [properties]) -> EntityFamiliar"""
            if len(arguments) < 1:
                raise RuntimeError("create_entity_familiar expects at least 1 argument (name)")
            name = arguments[0]
            properties = arguments[1] if len(arguments) > 1 else {}
            
            try:
                from grimoire.familiars.entity_familiar import EntityFamiliar
                familiar = EntityFamiliar(name)  # Only pass name to constructor
                
                # Set properties after creation if provided
                if properties and isinstance(properties, dict):
                    for prop_name, prop_value in properties.items():
                        familiar.set_property(prop_name, prop_value, "initialization")
                
                self.familiars[name] = familiar
                self.familiar_wrangler.register_familiar(familiar)
                return familiar
            except ImportError:
                raise RuntimeError("EntityFamiliar not available")
        
        def create_ai_familiar_builtin(interpreter, arguments):
            """create_ai_familiar(name) -> AIFamiliar"""
            if len(arguments) < 1:
                raise RuntimeError("create_ai_familiar expects 1 argument (name)")
            name = arguments[0]
            
            try:
                from grimoire.familiars.ai_familiar import AIFamiliar
                familiar = AIFamiliar(name)
                self.familiars[name] = familiar
                self.familiar_wrangler.register_familiar(familiar)
                return familiar
            except ImportError:
                raise RuntimeError("AIFamiliar not available")
        
        # Built-in function for creating archons
        def create_archon_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("create_archon expects 2 arguments (name, domain)")
            archon_name = arguments[0]
            domain = arguments[1]
            
            # Pass world model to archon for enhanced AI
            archon = GrimoireArchon(archon_name, domain, self.world_model)
            self.archons[archon_name] = archon
            return archon
        
        # Built-in function for creating spirits
        def create_spirit_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("create_spirit expects 2 arguments (name, spirit_type)")
            spirit_name = arguments[0]
            spirit_type = arguments[1]
            domain = arguments[2] if len(arguments) > 2 else "general"
            
            spirit = GrimoireSpirit(spirit_name, spirit_type, domain)
            spirit.pact_registry_ref = self.pact_registry
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
        
        # Built-in wrangler functions
        def create_wrangler_builtin(interpreter, arguments):
            # Wrangler is already created, just return it
            return self.familiar_wrangler
        
        def register_familiar_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("register_familiar expects 1 argument (familiar)")
            familiar = arguments[0]
            if not isinstance(familiar, GrimoireFamiliar):
                raise RuntimeError("Argument must be a familiar")
            return self.familiar_wrangler.register_familiar(familiar)
        
        def enable_reporting_builtin(interpreter, arguments):
            if len(arguments) < 1:
                raise RuntimeError("enable_reporting expects at least 1 argument (familiar)")
            familiar = arguments[0]
            report_type = arguments[1] if len(arguments) > 1 else "all"
            if not isinstance(familiar, GrimoireFamiliar):
                raise RuntimeError("First argument must be a familiar")
            return self.familiar_wrangler.enable_reporting(familiar, report_type)
        
        def disable_reporting_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("disable_reporting expects 1 argument (familiar)")
            familiar = arguments[0]
            if not isinstance(familiar, GrimoireFamiliar):
                raise RuntimeError("Argument must be a familiar")
            return self.familiar_wrangler.disable_reporting(familiar)
        
        def get_wrangler_report_builtin(interpreter, arguments):
            familiar_name = arguments[0] if len(arguments) > 0 else None
            report = self.familiar_wrangler.get_report(familiar_name)
            # Convert activities to strings for display
            return [f"[{a.timestamp:.2f}] {a.familiar_name}: {a.description} ({a.activity_type})" for a in report]
        
        def get_wrangler_summary_builtin(interpreter, arguments):
            return self.familiar_wrangler.get_summary()
        
        def clear_wrangler_reports_builtin(interpreter, arguments):
            familiar_name = arguments[0] if len(arguments) > 0 else None
            return self.familiar_wrangler.clear_reports(familiar_name)
        
        def enable_all_reporting_builtin(interpreter, arguments):
            report_type = arguments[0] if len(arguments) > 0 else "all"
            return self.familiar_wrangler.enable_all_reporting(report_type)
        
        def disable_all_reporting_builtin(interpreter, arguments):
            return self.familiar_wrangler.disable_all_reporting()
        
        def get_familiar_stats_builtin(interpreter, arguments):
            return self.familiar_wrangler.get_familiar_stats()
        
        # Pact system functions
        def create_familiar_with_pact_builtin(interpreter, arguments):
            if len(arguments) < 3:
                raise RuntimeError("create_familiar_with_pact expects at least 3 arguments (spirit, familiar_type, pact_terms)")
            spirit = arguments[0]
            familiar_type = arguments[1]
            pact_terms = arguments[2] if isinstance(arguments[2], list) else [arguments[2]]
            pact_conditions = arguments[3] if len(arguments) > 3 else {}
            
            if not isinstance(spirit, GrimoireSpirit):
                raise RuntimeError("First argument must be a spirit")
            
            return spirit.create_familiar_with_pact(familiar_type, pact_terms, pact_conditions)
        
        def invoke_pact_builtin(interpreter, arguments):
            if len(arguments) < 3:
                raise RuntimeError("invoke_pact expects at least 3 arguments (spirit, familiar_true_name, action)")
            spirit = arguments[0]
            familiar_true_name = arguments[1]
            action = arguments[2]
            additional_args = arguments[3:] if len(arguments) > 3 else []
            
            if not isinstance(spirit, GrimoireSpirit):
                raise RuntimeError("First argument must be a spirit")
            
            return spirit.invoke_pact(familiar_true_name, action, *additional_args)
        
        def revoke_pact_builtin(interpreter, arguments):
            if len(arguments) != 2:
                raise RuntimeError("revoke_pact expects 2 arguments (spirit, familiar_true_name)")
            spirit = arguments[0]
            familiar_true_name = arguments[1]
            
            if not isinstance(spirit, GrimoireSpirit):
                raise RuntimeError("First argument must be a spirit")
            
            return spirit.revoke_pact(familiar_true_name)
        
        def oversee_domain_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("oversee_domain expects 1 argument (spirit)")
            spirit = arguments[0]
            
            if not isinstance(spirit, GrimoireSpirit):
                raise RuntimeError("Argument must be a spirit")
            
            return spirit.oversee_domain()
        
        def get_pact_summary_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("get_pact_summary expects 1 argument (familiar)")
            familiar = arguments[0]
            
            if not isinstance(familiar, GrimoireFamiliar):
                raise RuntimeError("Argument must be a familiar")
            
            return familiar.get_pact_summary()
        
        def get_spirit_pacts_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("get_spirit_pacts expects 1 argument (spirit)")
            spirit = arguments[0]
            
            if not isinstance(spirit, GrimoireSpirit):
                raise RuntimeError("Argument must be a spirit")
            
            # Return a simplified view of pacts
            return {
                "spirit_name": spirit.name,
                "domain": spirit.domain,
                "total_pacts": len(spirit.pacts),
                "familiar_pacts": {
                    true_name: {
                        "terms": pact.pact_terms,
                        "domain": pact.domain,
                        "creation_time": pact.creation_timestamp
                    }
                    for true_name, pact in spirit.pacts.items()
                }
            }
        
        # ------------------------------------------------------------------
        # Socket system built-ins
        # ------------------------------------------------------------------
        def create_socket_builtin(interpreter, arguments):
            """create_socket(familiar, name, direction='input'|'output') -> Socket"""
            if len(arguments) < 2:
                raise RuntimeError("create_socket expects at least 2 arguments (familiar, name)")
            familiar, name = arguments[0], arguments[1]
            direction = arguments[2] if len(arguments) > 2 else "input"
            if not isinstance(familiar, GrimoireFamiliar):
                raise RuntimeError("First argument must be a familiar")
            return familiar.add_socket(name, direction=direction)

        def connect_socket_builtin(interpreter, arguments):
            """connect_socket(output_socket, input_socket)
            Establish a unidirectional connection from an *output* socket to an
            *input* socket.  Both sockets are Python `Socket` objects exposed by
            familiars via property access or explicit creation.
            """
            if len(arguments) != 2:
                raise RuntimeError("connect_socket expects 2 arguments (output_socket, input_socket)")
            output_socket, input_socket = arguments
            from grimoire.sockets import Socket  # Local import to avoid cycles
            if not isinstance(output_socket, Socket):
                raise RuntimeError("First argument must be a Socket (output)")
            if not isinstance(input_socket, Socket):
                raise RuntimeError("Second argument must be a Socket (input)")
            output_socket.connect_to(input_socket)
            return f"Connected {output_socket.owner.name}.{output_socket.name} -> {input_socket.owner.name}.{input_socket.name}"

        def disconnect_socket_builtin(interpreter, arguments):
            if len(arguments) != 2:
                raise RuntimeError("disconnect_socket expects 2 arguments (output_socket, input_socket)")
            output_socket, input_socket = arguments
            from grimoire.sockets import Socket
            if not isinstance(output_socket, Socket) or not isinstance(input_socket, Socket):
                raise RuntimeError("Both arguments must be Socket objects")
            output_socket.disconnect_from(input_socket)
            return f"Disconnected {output_socket.owner.name}.{output_socket.name} -X- {input_socket.owner.name}.{input_socket.name}"
        
        # ------------------------------------------------------------------
        # Inter-familiar communication helpers (phase 1)
        # ------------------------------------------------------------------
        def link_familiars_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("link_familiars expects at least 2 arguments (fam1, fam2)")
            fam1, fam2 = arguments[0], arguments[1]
            connection_type = arguments[2] if len(arguments) > 2 else "direct"
            if not isinstance(fam1, GrimoireFamiliar) or not isinstance(fam2, GrimoireFamiliar):
                raise RuntimeError("Both arguments must be familiars")
            # For now: create generic message sockets
            from grimoire.sockets import SocketDirectionError
            try:
                out_sock = fam1.get_socket("message_output")
            except RuntimeError:
                out_sock = fam1.add_socket("message_output", direction="output")
            try:
                in_sock = fam2.get_socket("message_input")
            except RuntimeError:
                in_sock = fam2.add_socket("message_input", direction="input")
            try:
                out_sock.connect_to(in_sock)
            except SocketDirectionError:
                pass
            return f"{fam1.name} linked to {fam2.name} ({connection_type})"

        def send_familiar_message_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("send_familiar_message expects (familiar, message, [target])")
            fam = arguments[0]
            message = arguments[1]
            if not isinstance(fam, GrimoireFamiliar):
                raise RuntimeError("First argument must be a familiar")

            from grimoire.messaging import build_message  # Local import
            # Build structured message; fam.true_name is immutable unique id
            msg_obj = build_message(fam.true_name, message, category="direct")
            fam.send_to_socket("message_output", msg_obj)
            fam.log_activity("inter_familiar", "Message sent", {"message": str(msg_obj)})
            return "message sent"

        def familiar_broadcast_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("familiar_broadcast expects (familiar, message)")
            fam = arguments[0]
            msg = arguments[1]
            if not isinstance(fam, GrimoireFamiliar):
                raise RuntimeError("First argument must be a familiar")
            # Broadcast to all connected sinks
            sock = None
            try:
                sock = fam.get_socket("message_output")
            except RuntimeError:
                sock = fam.add_socket("message_output", direction="output")
            from grimoire.messaging import build_message
            msg_obj = build_message(fam.true_name, msg, category="broadcast")
            sock.send(msg_obj)
            fam.log_activity("inter_familiar", "Broadcast message", {"message": str(msg_obj), "receivers": len(sock.connections)})
            return "broadcast complete"

        # ------------------------------------------------------------------
        # AI goal/action helpers
        # ------------------------------------------------------------------
        def add_goal_builtin(interpreter, arguments):
            if len(arguments) < 4:
                raise RuntimeError("add_goal expects (ai_familiar, name, priority, condition_callable)")
            fam, name, priority, condition = arguments[:4]
            if not isinstance(fam, GrimoireFamiliar) or not hasattr(fam, 'add_goal'):
                raise RuntimeError("First argument must be an AI familiar")
            fam.add_goal(name, int(priority), condition)  # type: ignore[attr-defined]
            return "goal added"

        def add_action_builtin(interpreter, arguments):
            if len(arguments) < 4:
                raise RuntimeError("add_action expects (ai_familiar, goal_name, action_name, effect_callable, [precondition])")
            fam, goal_name, action_name, effect = arguments[:4]
            precond = arguments[4] if len(arguments) > 4 else (lambda _: True)
            if not isinstance(fam, GrimoireFamiliar) or not hasattr(fam, 'add_action'):
                raise RuntimeError("First argument must be an AI familiar")
            fam.add_action(goal_name, action_name, effect, precond)  # type: ignore[attr-defined]
            return "action added"

        def update_ai_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("update_ai expects 1 argument (ai_familiar)")
            fam = arguments[0]
            if not isinstance(fam, GrimoireFamiliar) or not hasattr(fam, 'plan'):
                raise RuntimeError("Argument must be an AI familiar")
            fam.plan()  # type: ignore[attr-defined]
            return "ai updated"

        from grimoire.game.interactions import apply_damage as _apply_damage
        def apply_damage_builtin(interpreter, arguments):
            if len(arguments) != 2:
                raise RuntimeError("apply_damage expects (entity_familiar, amount)")
            fam, amt = arguments
            return _apply_damage(fam, float(amt))

        # Game loop helpers -------------------------------------------------
        def start_game_loop_builtin(interpreter, arguments):
            from grimoire.game.loop import GameLoopFamiliar
            loop_type = arguments[0] if len(arguments) > 0 else 'real_time'
            rate = int(arguments[1]) if len(arguments) > 1 else 60
            loop = GameLoopFamiliar('game_loop', loop_type, rate)
            self.familiars['game_loop'] = loop
            loop.start()
            return loop

        def schedule_event_builtin(interpreter, arguments):
            if len(arguments) < 3:
                raise RuntimeError('schedule_event expects (game_loop, delay, callable, *args)')
            loop, delay, func, *rest = arguments
            from grimoire.game.loop import GameLoopFamiliar
            if not isinstance(loop, GameLoopFamiliar):
                raise RuntimeError('First arg must be a GameLoop familiar')
            loop.schedule(float(delay), func, *rest)
            return 'event scheduled'

        def pause_game_builtin(interpreter, arguments):
            loop = self.familiars.get('game_loop')
            if loop:
                return loop.pause()
            return 'no game loop'

        def resume_game_builtin(interpreter, arguments):
            loop = self.familiars.get('game_loop')
            if loop:
                return loop.resume()
            return 'no game loop'

        def move_entity_builtin(interpreter, arguments):
            if len(arguments) != 3:
                raise RuntimeError('move_entity expects (entity_familiar, x, y)')
            entity, x, y = arguments
            if not hasattr(entity, 'set_position'):
                raise RuntimeError('Familiar cannot be positioned')
            entity.set_position(int(x), int(y))
            return entity.position

        def add_move_to_goal_builtin(interpreter, arguments):
            if len(arguments) < 3:
                raise RuntimeError('add_move_to_goal(ai_familiar, target_entity, radius)')
            fam, target, radius = arguments[:3]
            from grimoire.ai.pos_goals import MoveToGoal
            if not hasattr(fam, 'add_custom_goal'):
                raise RuntimeError('First arg must be AI familiar')
            fam.add_custom_goal(MoveToGoal(target, int(radius)))  # type: ignore[attr-defined]
            return 'move-to goal added'

        # Phase 3: Goal Artifacts and World State
        def define_goal_builtin(interpreter, arguments):
            if len(arguments) < 2:
                raise RuntimeError("define_goal expects (name, artifact_class, [urgency_weight], [satisfaction_threshold])")
            
            name = arguments[0]
            artifact_class = arguments[1]
            urgency_weight = arguments[2] if len(arguments) > 2 else 1.0
            satisfaction_threshold = arguments[3] if len(arguments) > 3 else 1.0
            
            from grimoire.goals import register_goal_artifact
            
            # Create instance of goal artifact
            if isinstance(artifact_class, GrimoireClass):
                goal_instance = artifact_class.call(interpreter, [])
            else:
                raise RuntimeError("Second argument must be a goal artifact class")
            
            # Register the goal artifact
            register_goal_artifact(name, goal_instance, urgency_weight, satisfaction_threshold)
            return f"Goal artifact '{name}' defined"

        def get_world_state_builtin(interpreter, arguments):
            if len(arguments) == 0:
                # Return all world state
                from grimoire.world_state import WorldState
                return WorldState.get_instance().get_all_state()
            elif len(arguments) == 1:
                # Return specific key
                from grimoire.world_state import WorldState
                key = arguments[0]
                return WorldState.get_instance().get_state(key)
            else:
                raise RuntimeError("get_world_state expects 0 or 1 arguments")

        def set_world_state_builtin(interpreter, arguments):
            if len(arguments) != 2:
                raise RuntimeError("set_world_state expects (key, value)")
            
            key, value = arguments
            from grimoire.world_state import WorldState
            WorldState.get_instance().set_state(key, value)
            return f"World state '{key}' set to {value}"

        def subscribe_world_state_builtin(interpreter, arguments):
            if len(arguments) != 2:
                raise RuntimeError("subscribe_world_state expects (key, callback)")
            
            key, callback = arguments
            from grimoire.world_state import WorldState
            
            if not callable(callback):
                raise RuntimeError("Second argument must be a callable")
            
            WorldState.get_instance().subscribe(key, callback)
            return f"Subscribed to world state changes for '{key}'"

        def evaluate_goal_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("evaluate_goal expects (goal_name)")
            
            goal_name = arguments[0]
            from grimoire.goals import get_goal_artifact
            
            goal = get_goal_artifact(goal_name)
            if not goal:
                raise RuntimeError(f"Goal '{goal_name}' not found")
            
            # Use evaluate() method instead of is_satisfied()
            from grimoire.world_state import WorldState
            return goal.evaluate(WorldState.get_instance())

        def get_goal_urgency_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("get_goal_urgency expects (goal_name)")
            
            goal_name = arguments[0]
            from grimoire.goals import get_goal_artifact
            
            goal = get_goal_artifact(goal_name)
            if not goal:
                raise RuntimeError(f"Goal '{goal_name}' not found")
            
            return goal.get_urgency()

        def list_goals_builtin(interpreter, arguments):
            from grimoire.goals import list_goal_artifacts
            return list_goal_artifacts()

        # Phase 5: Developer Experience built-ins
        def debug_familiar_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("debug_familiar expects 1 argument (familiar_name)")
            
            familiar_name = arguments[0]
            familiar = self.familiars.get(familiar_name)
            
            if not familiar:
                raise RuntimeError(f"Familiar '{familiar_name}' not found")
            
            # Get comprehensive debug info
            debug_info = {
                "name": familiar.name,
                "true_name": familiar.true_name,
                "familiar_type": str(familiar.familiar_type),
                "state": familiar.state,
                "sockets": list(familiar.sockets.keys()) if hasattr(familiar, 'sockets') else [],
                "activity_log": familiar.get_report() if hasattr(familiar, 'get_report') else []
            }
            
            # Add type-specific debug info
            if hasattr(familiar, 'get_ai_status'):
                debug_info["ai_status"] = familiar.get_ai_status()
            
            if hasattr(familiar, 'properties'):
                debug_info["properties"] = familiar.properties
            
            return debug_info

        def profile_ai_builtin(interpreter, arguments):
            if len(arguments) != 1:
                raise RuntimeError("profile_ai expects 1 argument (familiar_name)")
            
            familiar_name = arguments[0]
            familiar = self.familiars.get(familiar_name)
            
            if not familiar:
                raise RuntimeError(f"Familiar '{familiar_name}' not found")
            
            if not hasattr(familiar, 'get_ai_status'):
                raise RuntimeError(f"Familiar '{familiar_name}' is not an AI familiar")
            
            # Get AI profiling information
            try:
                from grimoire.profiler import get_ai_profiler
                ai_profiler = get_ai_profiler()
                return ai_profiler.get_performance_insights(familiar_name)
            except ImportError:
                return {"error": "Profiler not available"}

        def create_player_builtin(interpreter, arguments):
            if len(arguments) < 1:
                raise RuntimeError("create_player expects at least 1 argument (name)")
            
            name = arguments[0]
            player_data = arguments[1] if len(arguments) > 1 else None
            
            try:
                from grimoire.standard_library import PlayerFamiliar
                player = PlayerFamiliar(name, player_data)
                self.familiars[name] = player
                return player
            except ImportError:
                raise RuntimeError("Standard library not available")

        def create_timer_builtin(interpreter, arguments):
            if len(arguments) < 1:
                raise RuntimeError("create_timer expects 1 argument (name)")
            
            name = arguments[0]
            
            try:
                from grimoire.standard_library import TimerFamiliar
                timer = TimerFamiliar(name)
                self.familiars[name] = timer
                return timer
            except ImportError:
                raise RuntimeError("Standard library not available")

        self.globals.define("scry", scry_builtin)
        self.globals.define("summon", summon_builtin)
        self.globals.define("create_entity_familiar", create_entity_familiar_builtin)
        self.globals.define("create_ai_familiar", create_ai_familiar_builtin)
        self.globals.define("create_archon", create_archon_builtin)
        self.globals.define("create_spirit", create_spirit_builtin)
        
        # Conjure aliases for mystical terminology
        self.globals.define("conjure_familiar", create_entity_familiar_builtin)
        self.globals.define("conjure_spirit", create_spirit_builtin)
        self.globals.define("conjure_archon", create_archon_builtin)
        self.globals.define("autonomous_update", autonomous_update_builtin)
        
        # Wrangler functions
        self.globals.define("create_wrangler", create_wrangler_builtin)
        self.globals.define("register_familiar", register_familiar_builtin)
        self.globals.define("enable_reporting", enable_reporting_builtin)
        self.globals.define("disable_reporting", disable_reporting_builtin)
        self.globals.define("get_wrangler_report", get_wrangler_report_builtin)
        self.globals.define("get_wrangler_summary", get_wrangler_summary_builtin)
        self.globals.define("clear_wrangler_reports", clear_wrangler_reports_builtin)
        self.globals.define("enable_all_reporting", enable_all_reporting_builtin)
        self.globals.define("disable_all_reporting", disable_all_reporting_builtin)
        self.globals.define("get_familiar_stats", get_familiar_stats_builtin)
        
        # Pact system functions
        self.globals.define("create_familiar_with_pact", create_familiar_with_pact_builtin)
        
        # Conjure pact alias for mystical terminology
        self.globals.define("conjure_familiar_with_pact", create_familiar_with_pact_builtin)
        self.globals.define("invoke_pact", invoke_pact_builtin)
        self.globals.define("revoke_pact", revoke_pact_builtin)
        self.globals.define("oversee_domain", oversee_domain_builtin)
        self.globals.define("get_pact_summary", get_pact_summary_builtin)
        self.globals.define("get_spirit_pacts", get_spirit_pacts_builtin)
        
        # Socket functions
        self.globals.define("create_socket", create_socket_builtin)
        self.globals.define("connect_socket", connect_socket_builtin)
        self.globals.define("disconnect_socket", disconnect_socket_builtin)
        self.globals.define("link_familiars", link_familiars_builtin)
        self.globals.define("send_familiar_message", send_familiar_message_builtin)
        self.globals.define("familiar_broadcast", familiar_broadcast_builtin)
        self.globals.define("add_goal", add_goal_builtin)
        self.globals.define("add_action", add_action_builtin)
        self.globals.define("update_ai", update_ai_builtin)
        self.globals.define("apply_damage", apply_damage_builtin)
        self.globals.define('start_game_loop', start_game_loop_builtin)
        self.globals.define('schedule_event', schedule_event_builtin)
        self.globals.define('pause_game', pause_game_builtin)
        self.globals.define('resume_game', resume_game_builtin)
        self.globals.define('move_entity', move_entity_builtin)
        self.globals.define('add_move_to_goal', add_move_to_goal_builtin)
        self.globals.define("define_goal", define_goal_builtin)
        self.globals.define("get_world_state", get_world_state_builtin)
        self.globals.define("set_world_state", set_world_state_builtin)
        self.globals.define("subscribe_world_state", subscribe_world_state_builtin)
        self.globals.define("evaluate_goal", evaluate_goal_builtin)
        self.globals.define("get_goal_urgency", get_goal_urgency_builtin)
        self.globals.define("list_goals", list_goals_builtin)
        self.globals.define("debug_familiar", debug_familiar_builtin)
        self.globals.define("profile_ai", profile_ai_builtin)
        self.globals.define("create_player", create_player_builtin)
        self.globals.define("create_timer", create_timer_builtin)
        
        # =====================================================================
        # Anomaly Detection System Built-ins
        # =====================================================================
        
        def register_anomaly_builtin(interpreter, arguments):
            """Register an anomaly in the global registry."""
            if len(arguments) != 1:
                raise RuntimeError("register_anomaly expects 1 argument (anomaly)")
            
            from .anomalies import register_anomaly
            anomaly = arguments[0]
            return register_anomaly(anomaly)
        
        def get_anomaly_builtin(interpreter, arguments):
            """Get an anomaly from the global registry."""
            if len(arguments) != 1:
                raise RuntimeError("get_anomaly expects 1 argument (identifier)")
            
            from .anomalies import get_anomaly
            identifier = arguments[0]
            return get_anomaly(identifier)
        
        def create_anomaly_set_builtin(interpreter, arguments):
            """Create a named set of anomalies."""
            if len(arguments) != 2:
                raise RuntimeError("create_anomaly_set expects 2 arguments (set_name, anomaly_identifiers)")
            
            from .anomalies import create_anomaly_set
            set_name, anomaly_identifiers = arguments
            return create_anomaly_set(set_name, anomaly_identifiers)
        
        def get_anomaly_set_builtin(interpreter, arguments):
            """Get a named set of anomalies."""
            if len(arguments) != 1:
                raise RuntimeError("get_anomaly_set expects 1 argument (set_name)")
            
            from .anomalies import get_anomaly_set
            set_name = arguments[0]
            return get_anomaly_set(set_name)
        
        def detect_anomaly_builtin(interpreter, arguments):
            """Detect anomalies in entity state."""
            if len(arguments) < 2:
                raise RuntimeError("detect_anomaly expects at least 2 arguments (anomaly, entity_state)")
            
            anomaly = arguments[0]
            entity_state = arguments[1]
            world_state = arguments[2] if len(arguments) > 2 else {}
            
            return anomaly.detect(entity_state, world_state)
        
        def report_anomaly_builtin(interpreter, arguments):
            """Report an anomaly detection."""
            if len(arguments) < 3:
                raise RuntimeError("report_anomaly expects at least 3 arguments (anomaly, entity, context)")
            
            anomaly = arguments[0]
            entity = arguments[1]
            context = arguments[2]
            
            return anomaly.report_detection(entity, context)
        
        def create_adaptive_anomaly_builtin(interpreter, arguments):
            """Create an adaptive anomaly."""
            if len(arguments) < 2:
                raise RuntimeError("create_adaptive_anomaly expects at least 2 arguments (name, properties)")
            
            from .anomalies import AdaptiveAnomaly
            name = arguments[0]
            properties = arguments[1]
            threshold_multiplier = arguments[2] if len(arguments) > 2 else 2.0
            min_samples = arguments[3] if len(arguments) > 3 else 10
            severity = arguments[4] if len(arguments) > 4 else 0.6
            description = arguments[5] if len(arguments) > 5 else ""
            
            return AdaptiveAnomaly(name, properties, threshold_multiplier, min_samples, severity, description)
        
        def create_composite_anomaly_builtin(interpreter, arguments):
            """Create a composite anomaly."""
            if len(arguments) < 2:
                raise RuntimeError("create_composite_anomaly expects at least 2 arguments (name, sub_anomalies)")
            
            from .anomalies import CompositeAnomaly
            name = arguments[0]
            sub_anomalies = arguments[1]
            threshold = arguments[2] if len(arguments) > 2 else None
            severity = arguments[3] if len(arguments) > 3 else 0.8
            description = arguments[4] if len(arguments) > 4 else ""
            
            return CompositeAnomaly(name, sub_anomalies, threshold, severity, description)
        
        def add_context_rule_builtin(interpreter, arguments):
            """Add a context rule to the anomaly registry."""
            if len(arguments) != 1:
                raise RuntimeError("add_context_rule expects 1 argument (rule_function)")
            
            from .anomalies import add_context_rule
            rule_func = arguments[0]
            add_context_rule(rule_func)
            return "Context rule added"
        
        def get_active_anomalies_builtin(interpreter, arguments):
            """Get active anomalies for a given context."""
            if len(arguments) != 1:
                raise RuntimeError("get_active_anomalies expects 1 argument (context)")
            
            from .anomalies import anomaly_registry
            context = arguments[0]
            return anomaly_registry.get_active_anomalies_for_context(context)
        
        def get_anomaly_registry_stats_builtin(interpreter, arguments):
            """Get anomaly registry statistics."""
            from .anomalies import anomaly_registry
            return anomaly_registry.get_registry_stats()
        
        def assign_anomalies_to_familiar_builtin(interpreter, arguments):
            """Assign anomalies to a familiar for monitoring."""
            if len(arguments) != 2:
                raise RuntimeError("assign_anomalies_to_familiar expects 2 arguments (familiar, anomalies)")
            
            familiar = arguments[0]
            anomalies = arguments[1]
            
            # Add anomalies to familiar's monitoring list
            if not hasattr(familiar, 'assigned_anomalies'):
                familiar.assigned_anomalies = []
            
            if isinstance(anomalies, list):
                familiar.assigned_anomalies.extend(anomalies)
            else:
                familiar.assigned_anomalies.append(anomalies)
            
            return f"Assigned {len(anomalies) if isinstance(anomalies, list) else 1} anomalies to {familiar.name}"
        
        def check_familiar_anomalies_builtin(interpreter, arguments):
            """Check for anomalies in a familiar's monitored entities."""
            if len(arguments) < 1:
                raise RuntimeError("check_familiar_anomalies expects at least 1 argument (familiar)")
            
            familiar = arguments[0]
            entity_state = arguments[1] if len(arguments) > 1 else {}
            world_state = arguments[2] if len(arguments) > 2 else {}
            
            if not hasattr(familiar, 'assigned_anomalies'):
                return []
            
            detected_anomalies = []
            for anomaly in familiar.assigned_anomalies:
                if anomaly.detect(entity_state, world_state):
                    report = anomaly.report_detection(familiar, {"check_time": __import__('time').time()})
                    detected_anomalies.append(report)
            
            return detected_anomalies
        
        # Register anomaly built-ins
        self.globals.define("register_anomaly", register_anomaly_builtin)
        self.globals.define("get_anomaly", get_anomaly_builtin)
        self.globals.define("create_anomaly_set", create_anomaly_set_builtin)
        self.globals.define("get_anomaly_set", get_anomaly_set_builtin)
        self.globals.define("detect_anomaly", detect_anomaly_builtin)
        self.globals.define("report_anomaly", report_anomaly_builtin)
        self.globals.define("create_adaptive_anomaly", create_adaptive_anomaly_builtin)
        self.globals.define("create_composite_anomaly", create_composite_anomaly_builtin)
        self.globals.define("add_context_rule", add_context_rule_builtin)
        self.globals.define("get_active_anomalies", get_active_anomalies_builtin)
        self.globals.define("get_anomaly_registry_stats", get_anomaly_registry_stats_builtin)
        self.globals.define("assign_anomalies_to_familiar", assign_anomalies_to_familiar_builtin)
        self.globals.define("check_familiar_anomalies", check_familiar_anomalies_builtin)
    
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
        elif isinstance(value, GrimoireSpirit):
            return f"<spirit {value.name} ({value.spirit_type}) domain:{value.domain}>"
        elif isinstance(value, GrimoireArchon):
            return f"<archon {value.name} domain:{value.domain}>"
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
        
        elif isinstance(statement, PlaneStatement):
            # Handle plane definitions
            plane_properties = PlaneProperties(PlaneType.MATERIAL)  # Default to material plane
            plane = self.plane_manager.create_plane(statement.name, plane_properties)
            
            # Execute plane body in the plane context
            previous_plane = self.plane_manager.current_plane
            self.plane_manager.shift_to_plane(statement.name)
            try:
                self.execute(statement.body)
            finally:
                # Return to previous plane
                if previous_plane:
                    self.plane_manager.shift_to_plane(previous_plane)
        
        elif isinstance(statement, ShiftStatement):
            # Handle plane shifts
            success = self.plane_manager.shift_to_plane(statement.target_plane)
            if not success:
                raise RuntimeError(f"Failed to shift to plane '{statement.target_plane}'")
        
        elif isinstance(statement, AnomalyStatement):
            # Handle anomaly definitions
            from .anomalies import BaseAnomaly, AdaptiveAnomaly, CompositeAnomaly, register_anomaly
            
            # Create the appropriate anomaly type
            if statement.anomaly_type == "adaptive":
                anomaly = AdaptiveAnomaly(
                    name=statement.name,
                    properties=statement.properties,
                    threshold_multiplier=statement.threshold_multiplier or 2.0,
                    min_samples=statement.threshold or 10,
                    severity=statement.severity,
                    description=statement.description
                )
            elif statement.anomaly_type == "composite":
                # Get sub-anomalies from registry
                from .anomalies import get_anomaly
                sub_anomalies = []
                for sub_name in statement.sub_anomalies:
                    sub_anomaly = get_anomaly(sub_name)
                    if sub_anomaly:
                        sub_anomalies.append(sub_anomaly)
                    else:
                        raise RuntimeError(f"Sub-anomaly '{sub_name}' not found")
                
                anomaly = CompositeAnomaly(
                    name=statement.name,
                    sub_anomalies=sub_anomalies,
                    threshold=statement.threshold,
                    severity=statement.severity,
                    description=statement.description
                )
            else:
                # Create a custom base anomaly with body logic
                class CustomAnomaly(BaseAnomaly):
                    def __init__(self, name, severity, description, body_statements, interpreter_env):
                        super().__init__(name, severity, description)
                        self.body_statements = body_statements
                        self.interpreter_env = interpreter_env
                    
                    def detect(self, entity_state, world_state):
                        # For custom anomalies, always return False for now
                        # In a full implementation, you'd execute the body statements
                        # and evaluate the result
                        return False
                
                body_statements = statement.body.statements if statement.body else []
                anomaly = CustomAnomaly(
                    statement.name,
                    statement.severity,
                    statement.description,
                    body_statements,
                    self.environment
                )
            
            # Register the anomaly
            register_anomaly(anomaly)
            
            # Also define it in the current environment
            self.environment.define(statement.name, anomaly)
        
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
        
        elif isinstance(expression, TagLiteralExpression):
            # Handle tag literals ($TAG(category:value))
            from .tag_system import create_tag
            return create_tag(expression.category, expression.value)
        
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