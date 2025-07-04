#!/usr/bin/env python3
"""
Grimoire AI Familiar

This module implements the AIFamiliar class, which specializes in
decision making, goal evaluation, world modeling, and autonomous behavior.
"""

import time
import random
from typing import Any, Dict, Optional, Set, List, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from ..interpreter import GrimoireFamiliar
except ImportError:
    # Fallback for testing
    from grimoire.interpreter import GrimoireFamiliar

from .types import FamiliarType, FamiliarCapability, get_familiar_spec, FamiliarCapabilityError
from . import register_familiar_class


@dataclass
class Goal:
    """Represents a programmable goal artifact."""
    name: str
    priority: float  # 0.0 to 1.0
    domain: str
    current_satisfaction: float = 0.0
    target_satisfaction: float = 1.0
    evaluation_function: Optional[Callable] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Evaluate current satisfaction level (0.0 to 1.0)."""
        if self.evaluation_function:
            return self.evaluation_function(world_state)
        return self.current_satisfaction
    
    def is_satisfied(self, world_state: Dict[str, Any]) -> bool:
        """Check if goal is satisfied."""
        return self.evaluate_satisfaction(world_state) >= self.target_satisfaction
    
    def get_urgency(self) -> float:
        """Calculate urgency based on satisfaction and priority."""
        return (1.0 - self.current_satisfaction) * self.priority


@dataclass
class Action:
    """Represents an action that can be taken by the AI."""
    name: str
    precondition: Callable[[Dict[str, Any]], bool]
    effect: Callable[[Dict[str, Any]], Dict[str, Any]]
    cost: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def can_execute(self, world_state: Dict[str, Any]) -> bool:
        """Check if action can be executed in current state."""
        return self.precondition(world_state)
    
    def execute(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action and return new world state."""
        if self.can_execute(world_state):
            return self.effect(world_state)
        return world_state
    
    def predict_outcome(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Predict action outcome without executing."""
        return self.execute(world_state.copy())


@dataclass
class Decision:
    """Represents a decision made by the AI."""
    action: Action
    confidence: float  # 0.0 to 1.0
    reasoning: str
    expected_utility: float
    timestamp: float
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@register_familiar_class("AI")
class AIFamiliar(GrimoireFamiliar):
    """
    Familiar specialized for AI decision making and goal evaluation.
    
    AIFamiliars excel at:
    - Autonomous decision making based on goals
    - World state modeling and prediction
    - Goal evaluation and satisfaction tracking
    - Action planning and execution
    - Learning from experience
    """
    
    def __init__(self, name: str, ai_config: Optional[Dict[str, Any]] = None, 
                 true_name: Optional[str] = None):
        # Initialize base familiar
        super().__init__(name, FamiliarType.AI.name, {}, true_name)
        
        # Set familiar type and validate capabilities
        self.familiar_type = FamiliarType.AI
        # Note: capabilities should be a dict for the base class, but we track our type capabilities separately
        self.capability_types = {
            FamiliarCapability.GOAL_EVALUATION,
            FamiliarCapability.DECISION_MAKING,
            FamiliarCapability.SOCKET_MANAGEMENT,
            FamiliarCapability.WORLD_MODELING
        }
        
        # Validate we have required capabilities
        spec = get_familiar_spec(self.familiar_type)
        missing = spec.required_capabilities - self.capability_types
        if missing:
            raise FamiliarCapabilityError(f"AIFamiliar missing required capabilities: {missing}")
        
        # Initialize AI-specific attributes
        self.goals: List[Goal] = []
        self.actions: List[Action] = []
        self.world_model: Dict[str, Any] = {}
        self.decision_history: List[Decision] = []
        self.max_decision_history = 100
        
        # AI configuration
        config = ai_config or {}
        self.decision_threshold = config.get('decision_threshold', 0.7)
        self.exploration_rate = config.get('exploration_rate', 0.1)
        self.learning_rate = config.get('learning_rate', 0.05)
        self.planning_horizon = config.get('planning_horizon', 5)
        
        # Auto-create standard sockets based on specification
        self._setup_default_sockets()
        
        # Initialize AI system
        self._setup_ai_system()
    
    def has_socket(self, name: str) -> bool:
        """Check if familiar has a socket with the given name."""
        return name in self.sockets
    
    def _setup_default_sockets(self):
        """Set up default sockets for AI familiar."""
        spec = get_familiar_spec(self.familiar_type)
        
        for socket_name, direction in spec.default_sockets.items():
            try:
                self.add_socket(socket_name, direction=direction)
            except Exception as e:
                # Socket might already exist, that's OK
                pass
    
    def _setup_ai_system(self):
        """Set up AI decision-making system."""
        # Set up socket handlers for AI operations
        if self.has_socket("goal_input"):
            # Goal input socket can receive new goals
            pass  # Socket handling would be implemented in socket system
        
        if self.has_socket("world_state_input"):
            # World state input socket receives world updates
            pass  # Socket handling would be implemented in socket system
        
        # Initialize default goals and actions
        self._initialize_default_goals()
        self._initialize_default_actions()
    
    def _initialize_default_goals(self):
        """Initialize default goals for AI familiar."""
        # Survival goal
        survival_goal = Goal(
            name="survival",
            priority=0.9,
            domain="self",
            evaluation_function=lambda world_state: world_state.get("health", 1.0)
        )
        self.goals.append(survival_goal)
        
        # Efficiency goal
        efficiency_goal = Goal(
            name="efficiency",
            priority=0.6,
            domain="operational",
            evaluation_function=lambda world_state: world_state.get("efficiency", 0.5)
        )
        self.goals.append(efficiency_goal)
    
    def _initialize_default_actions(self):
        """Initialize default actions for AI familiar."""
        # Wait action
        wait_action = Action(
            name="wait",
            precondition=lambda world_state: True,
            effect=lambda world_state: {**world_state, "time": world_state.get("time", 0) + 1},
            cost=0.1
        )
        self.actions.append(wait_action)
        
        # Explore action
        explore_action = Action(
            name="explore",
            precondition=lambda world_state: world_state.get("energy", 1.0) > 0.2,
            effect=lambda world_state: {
                **world_state, 
                "knowledge": world_state.get("knowledge", 0) + 0.1,
                "energy": world_state.get("energy", 1.0) - 0.1
            },
            cost=0.2
        )
        self.actions.append(explore_action)
    
    def add_goal(self, goal: Goal) -> None:
        """Add a new goal to the AI system."""
        self.goals.append(goal)
        self.log_activity(
            "self",
            f"Goal added: {goal.name}",
            {"priority": goal.priority, "domain": goal.domain}
        )
    
    def remove_goal(self, goal_name: str) -> bool:
        """Remove a goal by name."""
        for i, goal in enumerate(self.goals):
            if goal.name == goal_name:
                removed_goal = self.goals.pop(i)
                self.log_activity(
                    "self",
                    f"Goal removed: {goal_name}",
                    {"priority": removed_goal.priority}
                )
                return True
        return False
    
    def get_goal(self, goal_name: str) -> Optional[Goal]:
        """Get a goal by name."""
        for goal in self.goals:
            if goal.name == goal_name:
                return goal
        return None
    
    def add_action(self, action: Action) -> None:
        """Add a new action to the AI system."""
        self.actions.append(action)
        self.log_activity(
            "self",
            f"Action added: {action.name}",
            {"cost": action.cost}
        )
    
    def remove_action(self, action_name: str) -> bool:
        """Remove an action by name."""
        for i, action in enumerate(self.actions):
            if action.name == action_name:
                removed_action = self.actions.pop(i)
                self.log_activity(
                    "self",
                    f"Action removed: {action_name}",
                    {"cost": removed_action.cost}
                )
                return True
        return False
    
    def get_action(self, action_name: str) -> Optional[Action]:
        """Get an action by name."""
        for action in self.actions:
            if action.name == action_name:
                return action
        return None
    
    def update_world_model(self, world_state: Dict[str, Any]) -> None:
        """Update internal world model."""
        self.world_model.update(world_state)
        self.log_activity(
            "self",
            "World model updated",
            {"state_keys": list(world_state.keys())}
        )
    
    def evaluate_goals(self, world_state: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Evaluate all goals and return satisfaction levels."""
        if world_state is None:
            world_state = self.world_model
        
        satisfactions = {}
        for goal in self.goals:
            satisfaction = goal.evaluate_satisfaction(world_state)
            goal.current_satisfaction = satisfaction
            satisfactions[goal.name] = satisfaction
        
        return satisfactions
    
    def get_priority_goal(self, world_state: Optional[Dict[str, Any]] = None) -> Optional[Goal]:
        """Get the highest priority unsatisfied goal."""
        if world_state is None:
            world_state = self.world_model
        
        unsatisfied_goals = [
            goal for goal in self.goals 
            if not goal.is_satisfied(world_state)
        ]
        
        if not unsatisfied_goals:
            return None
        
        # Sort by urgency (combination of priority and satisfaction)
        return max(unsatisfied_goals, key=lambda g: g.get_urgency())
    
    def get_available_actions(self, world_state: Optional[Dict[str, Any]] = None) -> List[Action]:
        """Get actions that can be executed in current state."""
        if world_state is None:
            world_state = self.world_model
        
        return [action for action in self.actions if action.can_execute(world_state)]
    
    def evaluate_action_utility(self, action: Action, world_state: Optional[Dict[str, Any]] = None) -> float:
        """Evaluate the utility of an action for achieving goals."""
        if world_state is None:
            world_state = self.world_model
        
        if not action.can_execute(world_state):
            return -float('inf')
        
        # Predict outcome
        predicted_state = action.predict_outcome(world_state)
        
        # Calculate utility based on goal satisfaction improvement
        total_utility = 0.0
        for goal in self.goals:
            current_satisfaction = goal.evaluate_satisfaction(world_state)
            predicted_satisfaction = goal.evaluate_satisfaction(predicted_state)
            improvement = predicted_satisfaction - current_satisfaction
            weighted_improvement = improvement * goal.priority
            total_utility += weighted_improvement
        
        # Subtract action cost
        total_utility -= action.cost
        
        return total_utility
    
    def make_decision(self, world_state: Optional[Dict[str, Any]] = None) -> Optional[Decision]:
        """Make a decision about which action to take."""
        if world_state is None:
            world_state = self.world_model
        
        available_actions = self.get_available_actions(world_state)
        if not available_actions:
            return None
        
        # Evaluate utility of each action
        action_utilities = []
        for action in available_actions:
            utility = self.evaluate_action_utility(action, world_state)
            action_utilities.append((action, utility))
        
        # Sort by utility
        action_utilities.sort(key=lambda x: x[1], reverse=True)
        
        # Epsilon-greedy exploration
        if random.random() < self.exploration_rate:
            # Explore: choose random action
            chosen_action = random.choice(available_actions)
            confidence = 0.5
            reasoning = "Exploration choice"
        else:
            # Exploit: choose best action
            chosen_action, best_utility = action_utilities[0]
            confidence = min(1.0, max(0.0, (best_utility + 1.0) / 2.0))  # Normalize to 0-1
            reasoning = f"Best utility: {best_utility:.3f}"
        
        decision = Decision(
            action=chosen_action,
            confidence=confidence,
            reasoning=reasoning,
            expected_utility=self.evaluate_action_utility(chosen_action, world_state),
            timestamp=time.time()
        )
        
        # Record decision
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_decision_history:
            self.decision_history = self.decision_history[-self.max_decision_history:]
        
        self.log_activity(
            "self",
            f"Decision made: {chosen_action.name}",
            {
                "confidence": confidence,
                "reasoning": reasoning,
                "expected_utility": decision.expected_utility
            }
        )
        
        return decision
    
    def execute_decision(self, decision: Decision, world_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a decision and return the new world state."""
        if world_state is None:
            world_state = self.world_model
        
        new_state = decision.action.execute(world_state)
        
        # Send decision through output socket
        if self.has_socket("decision_output"):
            try:
                self.send_to_socket("decision_output", {
                    "action": decision.action.name,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "timestamp": decision.timestamp
                })
            except Exception as e:
                self.log_activity(
                    "self",
                    f"Failed to send decision: {e}",
                    {"error": str(e)}
                )
        
        # Send action through action output socket
        if self.has_socket("action_output"):
            try:
                self.send_to_socket("action_output", {
                    "action_name": decision.action.name,
                    "metadata": decision.action.metadata,
                    "cost": decision.action.cost,
                    "timestamp": decision.timestamp
                })
            except Exception as e:
                self.log_activity(
                    "self",
                    f"Failed to send action: {e}",
                    {"error": str(e)}
                )
        
        self.log_activity(
            "self",
            f"Decision executed: {decision.action.name}",
            {"outcome": "success"}
        )
        
        return new_state
    
    def autonomous_update(self) -> None:
        """Perform autonomous AI update cycle."""
        if self.state != "active":
            return
        
        self.log_activity("self", "Starting AI autonomous update", {})
        
        # Receive world state updates from socket
        if self.has_socket("world_state_input"):
            try:
                world_update = self.receive_from_socket("world_state_input")
                if world_update:
                    self.update_world_model(world_update)
            except Exception as e:
                self.log_activity(
                    "self",
                    f"Failed to receive world state: {e}",
                    {"error": str(e)}
                )
        
        # Receive new goals from socket
        if self.has_socket("goal_input"):
            try:
                new_goal_data = self.receive_from_socket("goal_input")
                if new_goal_data:
                    # Process new goal (this would be more sophisticated in practice)
                    self.log_activity(
                        "self",
                        "New goal received via socket",
                        {"goal_data": new_goal_data}
                    )
            except Exception as e:
                self.log_activity(
                    "self",
                    f"Failed to receive goal: {e}",
                    {"error": str(e)}
                )
        
        # Evaluate current goals
        goal_satisfactions = self.evaluate_goals()
        
        # Make decision
        decision = self.make_decision()
        
        if decision:
            # Execute decision
            new_world_state = self.execute_decision(decision)
            self.update_world_model(new_world_state)
        
        self.log_activity(
            "self",
            "AI autonomous update completed",
            {"goals_evaluated": len(self.goals), "decision_made": decision is not None}
        )
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get current AI status and metrics."""
        return {
            "goals": len(self.goals),
            "actions": len(self.actions),
            "decisions_made": len(self.decision_history),
            "world_model_size": len(self.world_model),
            "recent_decisions": [
                {
                    "action": d.action.name,
                    "confidence": d.confidence,
                    "timestamp": d.timestamp
                }
                for d in self.decision_history[-5:]  # Last 5 decisions
            ],
            "goal_satisfactions": {
                goal.name: goal.current_satisfaction 
                for goal in self.goals
            }
        }
    
    def clear_decision_history(self) -> None:
        """Clear the decision history."""
        old_count = len(self.decision_history)
        self.decision_history.clear()
        self.log_activity(
            "self",
            f"Decision history cleared ({old_count} entries removed)",
            {"cleared_count": old_count}
        )
    
    def set_exploration_rate(self, rate: float) -> None:
        """Set the exploration rate for decision making."""
        self.exploration_rate = max(0.0, min(1.0, rate))
        self.log_activity(
            "self",
            f"Exploration rate set to {self.exploration_rate}",
            {"previous_rate": getattr(self, '_prev_exploration_rate', 0.1)}
        )
    
    def get_current_time(self) -> float:
        """Get current timestamp (can be overridden for testing)."""
        return time.time()
    
    # Override inquire to handle AI-specific queries
    def inquire(self, query: str) -> Any:
        """Handle AI-specific inquiries."""
        # Handle basic familiar properties
        if query == "name":
            return self.name
        elif query == "true_name":
            return self.true_name
        elif query == "state":
            return self.state
        elif query == "familiar_type":
            return self.familiar_type.name if hasattr(self.familiar_type, 'name') else str(self.familiar_type)
        elif query.startswith("goal."):
            goal_name = query[5:]  # Remove "goal." prefix
            goal = self.get_goal(goal_name)
            return goal.current_satisfaction if goal else None
        elif query == "all_goals":
            return {goal.name: goal.current_satisfaction for goal in self.goals}
        elif query == "priority_goal":
            priority_goal = self.get_priority_goal()
            return priority_goal.name if priority_goal else None
        elif query == "available_actions":
            return [action.name for action in self.get_available_actions()]
        elif query == "decision_history":
            return len(self.decision_history)
        elif query == "world_model":
            return self.world_model.copy()
        elif query == "ai_status":
            return self.get_ai_status()
        elif query.startswith("action."):
            action_name = query[7:]  # Remove "action." prefix
            action = self.get_action(action_name)
            return action.name if action else None
        else:
            # Fall back to base familiar inquire
            return super().inquire(query)
    
    def __str__(self) -> str:
        return f"<AIFamiliar {self.name} ({len(self.goals)} goals, {len(self.actions)} actions)>"
    
    def __repr__(self) -> str:
        return f"AIFamiliar(name='{self.name}', goals={len(self.goals)}, actions={len(self.actions)})"