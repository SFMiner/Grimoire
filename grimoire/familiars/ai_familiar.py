from __future__ import annotations

from typing import Optional, List, Any
import time

from grimoire.familiars import register_familiar_class
from grimoire.familiars.types import FamiliarType, FamiliarCapability

import importlib

def _base_cls():
    interpreter = importlib.import_module("grimoire.interpreter")  # type: ignore
    return getattr(interpreter, "GrimoireFamiliar")


@register_familiar_class("AI")
class AIFamiliar(_base_cls()):
    """Familiar equipped with goal/action planning and decision making."""

    def __init__(self, name: str, *, true_name: Optional[str] = None):
        super().__init__(name, "AI", capabilities={}, true_name=true_name)
        self.familiar_type = FamiliarType.AI
        self.capabilities = {FamiliarCapability.GOAL_EVALUATION, FamiliarCapability.DECISION_MAKING}
        self.goals = []  # Store goal artifacts
        self.current_action = None
        self.latest_perception = []
        
        # Initialize AI planner if available
        try:
            from grimoire.ai import AIPlanner
            self.planner = AIPlanner()
        except ImportError:
            self.planner = None

        # AI-specific sockets
        self.add_socket("goal_input", direction="input")
        self.add_socket("decision_output", direction="output")
        self.add_socket("world_state_input", direction="input")
        
        # Position handling
        try:
            from grimoire.game.spatial import get_global_grid
            self.position = (0, 0)
            get_global_grid().add_entity(self, self.position)
        except ImportError:
            self.position = (0, 0)

    def set_position(self, x: int, y: int):
        try:
            from grimoire.game.spatial import get_global_grid
            self.position = (x, y)
            get_global_grid().move_entity(self, self.position)
        except ImportError:
            self.position = (x, y)

    def get_current_time(self):
        """Get current timestamp for messages."""
        return time.time()

    # ------------------------------------------------------------------
    # Goal management - artifact-based goals
    # ------------------------------------------------------------------
    def add_goal(self, goal_artifact):
        """Add a programmable goal artifact."""
        self.goals.append(goal_artifact)
        
        # Also add to planner if available (for backwards compatibility)
        if self.planner and hasattr(goal_artifact, 'name'):
            try:
                from grimoire.ai.goals import Goal
                from grimoire.ai.conditions import CallableCondition
                
                # Convert goal artifact to planner goal
                planner_goal = Goal(
                    goal_artifact.name, 
                    int(getattr(goal_artifact, 'priority', 0.5) * 10),  # Convert to int
                    CallableCondition(lambda f: goal_artifact.is_satisfied(self._get_world_state(), 0.9))
                )
                self.planner.add_goal(planner_goal)
            except (ImportError, AttributeError):
                pass

    def add_legacy_goal(self, name: str, priority: int, condition):
        """Add goal using legacy planner system."""
        if self.planner:
            try:
                from grimoire.ai.goals import Goal
                from grimoire.ai.conditions import CallableCondition
                self.planner.add_goal(Goal(name, priority, CallableCondition(condition)))
            except ImportError:
                pass

    def add_action(self, goal_name: str, action_name: str, effect, precondition=lambda _: True):
        """Add action to goal (legacy support)."""
        if self.planner:
            try:
                from grimoire.ai.actions import Action
                from grimoire.ai.conditions import CallableCondition
                
                # find goal
                for g in self.planner.goals:
                    if g.name == goal_name:
                        g.add_action(Action(action_name, effect, precondition=CallableCondition(precondition)))
                        break
            except ImportError:
                pass

    def evaluate_goals(self, world_state):
        """Evaluate all goals and return highest priority action."""
        if not self.goals:
            return None
            
        best_action = None
        best_score = 0.0
        
        for goal in self.goals:
            if hasattr(goal, 'suggest_action'):
                try:
                    # Get available actions (simplified)
                    available_actions = self._get_available_actions()
                    action = goal.suggest_action(world_state, available_actions)
                    
                    if action and hasattr(goal, 'evaluate_satisfaction'):
                        satisfaction = goal.evaluate_satisfaction(world_state)
                        priority = getattr(goal, 'priority', 0.5)
                        score = satisfaction * priority
                        
                        if score > best_score:
                            best_score = score
                            best_action = action
                except Exception:
                    continue
                    
        return best_action

    def _get_available_actions(self):
        """Get available actions for this AI."""
        # Simplified action list - could be enhanced
        actions = []
        try:
            from grimoire.ai.actions import Action
            # Use wrapper functions to ensure None return type
            def explore_wrapper(f):
                self._explore_action()
                return None
            
            def communicate_wrapper(f):
                self._communicate_action()
                return None
            
            actions = [
                Action("wait", lambda f: None),
                Action("explore", explore_wrapper),
                Action("communicate", communicate_wrapper),
            ]
        except ImportError:
            pass
        return actions

    def _explore_action(self):
        """Simple exploration action."""
        # Move to a random nearby position
        import random
        x, y = self.position
        new_x = x + random.randint(-1, 1)
        new_y = y + random.randint(-1, 1)
        self.set_position(new_x, new_y)
        return f"Explored to position ({new_x}, {new_y})"

    def _communicate_action(self):
        """Simple communication action."""
        if hasattr(self, 'sockets') and "decision_output" in self.sockets:
            self.send_to_socket("decision_output", {
                "message": "AI status update",
                "timestamp": self.get_current_time(),
                "goals": len(self.goals)
            })
        return "Sent communication"

    def _get_world_state(self):
        """Get current world state for goal evaluation."""
        # Simplified world state - could be enhanced with proper world state system
        world_state = {
            "position": self.position,
            "goals": len(self.goals),
            "timestamp": self.get_current_time(),
            "perception": self.latest_perception
        }
        return world_state

    def plan(self):
        """Plan and execute actions."""
        # Update internal perception before planning
        try:
            if hasattr(self, 'sockets') and "world_state_input" in self.sockets:
                data = self.receive_from_socket('world_state_input')
                if isinstance(data, list):
                    self.latest_perception = data
        except RuntimeError:
            pass
        
        # Use new goal system if available
        world_state = self._get_world_state()
        action = self.evaluate_goals(world_state)
        
        if action:
            self.current_action = action
            # Execute action if it has an execute method
            if hasattr(action, 'execute'):
                try:
                    action.execute(self)
                except Exception:
                    pass
            
            # Log activity
            self.log_activity("self", "AI executed action", {
                "action": str(action),
                "world_state": world_state
            })
        else:
            # Fall back to legacy planner
            if self.planner:
                try:
                    legacy_action = self.planner.plan(self)
                    if legacy_action:
                        legacy_action.execute(self)
                        self.log_activity("self", "AI executed legacy action", {"action": legacy_action.name})
                except Exception:
                    pass
            
            if not action:
                self.log_activity("self", "AI idle", {"reason": "no viable actions"})

    def autonomous_update(self):
        """Enhanced autonomous update with goal-based planning."""
        if hasattr(super(), 'autonomous_update'):
            super().autonomous_update()
        self.plan()

    def receive_message(self, message):
        """Handle incoming messages from other familiars."""
        if hasattr(message, 'message_type'):
            if message.message_type == "world_state_update":
                # Update world state from incoming message
                self.latest_perception = message.payload
            elif message.message_type == "goal_request":
                # Handle goal requests
                response = self.evaluate_goals(self._get_world_state())
                return {"suggested_action": str(response) if response else None}
        return None