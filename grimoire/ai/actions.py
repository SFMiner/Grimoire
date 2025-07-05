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

from __future__ import annotations

"""Enhanced AI Action representation with preconditions and effects."""

from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
import copy

from .conditions import Condition, CallableCondition

__all__ = ["Action", "ActionLibrary", "ActionResult", "ActionEffect"]


@dataclass
class ActionEffect:
    """Represents the effect of an action."""
    target: str  # "actor", "world", "entity.{name}"
    property: str
    value: Any
    operation: str = "set"  # "set", "add", "multiply", "min", "max"
    
    def apply(self, world_state, actor, target_entity=None):
        """Apply this effect to the world state."""
        if self.target == "actor":
            if hasattr(actor, 'properties'):
                current = actor.properties.get(self.property, 0)
                new_value = self._calculate_new_value(current, self.value)
                actor.properties[self.property] = new_value
        elif self.target == "world":
            if hasattr(world_state, 'set_global_property'):
                current = world_state.get_global_property(self.property, 0)
                new_value = self._calculate_new_value(current, self.value)
                world_state.set_global_property(self.property, new_value)
        elif self.target.startswith("entity."):
            entity_name = self.target[7:]  # Remove "entity."
            if hasattr(world_state, 'set_entity_property'):
                current = world_state.get_entity_property(entity_name, self.property, 0)
                new_value = self._calculate_new_value(current, self.value)
                world_state.set_entity_property(entity_name, self.property, new_value)
    
    def _calculate_new_value(self, current, effect_value):
        """Calculate new value based on operation."""
        if self.operation == "set":
            return effect_value
        elif self.operation == "add":
            return current + effect_value
        elif self.operation == "multiply":
            return current * effect_value
        elif self.operation == "min":
            return min(current, effect_value)
        elif self.operation == "max":
            return max(current, effect_value)
        else:
            return effect_value


@dataclass
class ActionResult:
    """Represents the result of executing an action."""
    success: bool
    message: str
    effects_applied: List[ActionEffect]
    cost: float = 0.0
    
    def __str__(self):
        return f"ActionResult(success={self.success}, message='{self.message}', cost={self.cost})"


class Action:
    """Enhanced action with preconditions, effects, and cost."""
    
    def __init__(self, name: str, effect: Optional[Callable[[Any], None]] = None, *, 
                 precondition: Optional[Condition] = None,
                 preconditions: Optional[Dict[str, Any]] = None,
                 effects: Optional[List[ActionEffect]] = None,
                 cost: float = 1.0,
                 description: str = ""):
        self.name = name
        self.effect = effect  # Legacy callable effect
        self.precondition: Condition = precondition or CallableCondition(lambda _: True)
        self.preconditions = preconditions or {}  # Dict-based preconditions
        self.effects = effects or []  # List of ActionEffect objects
        self.cost = cost
        self.description = description
        
    def is_applicable(self, familiar) -> bool:
        """Check if action can be applied (legacy method)."""
        return self.precondition(familiar)
    
    def can_execute(self, world_state, actor) -> bool:
        """Check if preconditions are met."""
        # Check legacy precondition
        if not self.precondition(actor):
            return False
        
        # Check dict-based preconditions
        for condition, required_value in self.preconditions.items():
            if not self.check_condition(world_state, actor, condition, required_value):
                return False
        
        return True
    
    def check_condition(self, world_state, actor, condition: str, required_value: Any) -> bool:
        """Check specific precondition."""
        if condition.startswith("actor."):
            property_name = condition[6:]  # Remove "actor."
            if hasattr(actor, 'get_property'):
                actual_value = actor.get_property(property_name, 0)
            else:
                actual_value = getattr(actor, property_name, 0)
            
            # Handle different comparison types
            if isinstance(required_value, (int, float)):
                return actual_value >= required_value
            else:
                return actual_value == required_value
                
        elif condition.startswith("world."):
            property_name = condition[6:]  # Remove "world."
            if hasattr(world_state, 'get_global_property'):
                actual_value = world_state.get_global_property(property_name, 0)
            else:
                actual_value = 0
            
            if isinstance(required_value, (int, float)):
                return actual_value >= required_value
            else:
                return actual_value == required_value
                
        elif condition.startswith("entity."):
            parts = condition[7:].split('.')  # Remove "entity."
            if len(parts) >= 2:
                entity_name, property_name = parts[0], parts[1]
                if hasattr(world_state, 'get_entity_property'):
                    actual_value = world_state.get_entity_property(entity_name, property_name, 0)
                else:
                    actual_value = 0
                
                if isinstance(required_value, (int, float)):
                    return actual_value >= required_value
                else:
                    return actual_value == required_value
        
        return True
    
    def execute(self, familiar, world_state=None) -> ActionResult:
        """Execute the action with enhanced result tracking."""
        effects_applied = []
        
        try:
            # Execute legacy effect if present
            if self.effect:
                self.effect(familiar)
            
            # Apply new-style effects
            if world_state and self.effects:
                for effect in self.effects:
                    effect.apply(world_state, familiar)
                    effects_applied.append(effect)
            
            return ActionResult(
                success=True,
                message=f"Action '{self.name}' executed successfully",
                effects_applied=effects_applied,
                cost=self.cost
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Action '{self.name}' failed: {str(e)}",
                effects_applied=effects_applied,
                cost=self.cost
            )
    
    def predict_outcome(self, world_state, actor) -> Dict[str, Any]:
        """Predict world state after action execution."""
        if not world_state:
            return {}
        
        # Create copy of world state and apply effects
        predicted_state = copy.deepcopy(world_state)
        
        for effect in self.effects:
            effect.apply(predicted_state, actor)
        
        return {
            'predicted_world_state': predicted_state,
            'effects': self.effects,
            'cost': self.cost
        }
    
    def __repr__(self):  # pragma: no cover
        return f"<Action {self.name} (cost={self.cost})>"


class ActionLibrary:
    """Library of common game actions."""
    
    @staticmethod
    def create_move_action(target_location: tuple) -> Action:
        """Create a movement action."""
        return Action(
            name=f"move_to_{target_location}",
            preconditions={"actor.can_move": True},
            effects=[
                ActionEffect("actor", "position", target_location, "set")
            ],
            cost=1.0,
            description=f"Move to location {target_location}"
        )
    
    @staticmethod
    def create_attack_action(target: str, damage: float) -> Action:
        """Create an attack action."""
        def attack_effect(actor):
            # Legacy effect function
            if hasattr(actor, 'log_activity'):
                actor.log_activity("combat", f"Attacked {target} for {damage} damage", {})
        
        return Action(
            name=f"attack_{target}",
            effect=attack_effect,
            preconditions={"actor.can_attack": True, "actor.weapon": 1},
            effects=[
                ActionEffect(f"entity.{target}", "health", -damage, "add")
            ],
            cost=2.0,
            description=f"Attack {target} for {damage} damage"
        )
    
    @staticmethod
    def create_heal_action(target: str, healing: float) -> Action:
        """Create a healing action."""
        return Action(
            name=f"heal_{target}",
            preconditions={"actor.can_heal": True, "actor.mana": 10},
            effects=[
                ActionEffect(f"entity.{target}", "health", healing, "add"),
                ActionEffect("actor", "mana", -10, "add")
            ],
            cost=1.5,
            description=f"Heal {target} for {healing} health"
        )
    
    @staticmethod
    def create_collect_resource_action(resource_type: str, amount: float) -> Action:
        """Create a resource collection action."""
        return Action(
            name=f"collect_{resource_type}",
            preconditions={"actor.can_collect": True},
            effects=[
                ActionEffect("actor", f"resources.{resource_type}", amount, "add")
            ],
            cost=1.0,
            description=f"Collect {amount} {resource_type}"
        )
    
    @staticmethod
    def create_build_action(structure_type: str, cost_resources: Dict[str, float]) -> Action:
        """Create a building action."""
        effects = []
        preconditions = {}
        
        # Add resource costs as preconditions and effects
        for resource, amount in cost_resources.items():
            preconditions[f"actor.resources.{resource}"] = amount
            effects.append(ActionEffect("actor", f"resources.{resource}", -amount, "add"))
        
        # Add the structure
        effects.append(ActionEffect("world", f"structures.{structure_type}", 1, "add"))
        
        return Action(
            name=f"build_{structure_type}",
            preconditions=preconditions,
            effects=effects,
            cost=3.0,
            description=f"Build {structure_type}"
        )
    
    @staticmethod
    def create_wait_action(duration: float = 1.0) -> Action:
        """Create a wait/idle action."""
        return Action(
            name="wait",
            effects=[],
            cost=0.1,
            description=f"Wait for {duration} time units"
        )
    
    @staticmethod
    def create_explore_action() -> Action:
        """Create an exploration action."""
        return Action(
            name="explore",
            preconditions={"actor.can_move": True},
            effects=[
                ActionEffect("world", "explored_areas", 1, "add")
            ],
            cost=1.5,
            description="Explore unknown areas"
        )
    
    @staticmethod
    def get_basic_action_set() -> List[Action]:
        """Get a basic set of actions for testing."""
        return [
            ActionLibrary.create_wait_action(),
            ActionLibrary.create_explore_action(),
            ActionLibrary.create_move_action((0, 0)),
            ActionLibrary.create_collect_resource_action("wood", 5.0),
            ActionLibrary.create_collect_resource_action("stone", 3.0),
        ]