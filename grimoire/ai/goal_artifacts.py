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

"""Goal artifact system for AI agents.

This module provides artifact-based goals that can be programmed using Grimoire's
artifact system, allowing for flexible and programmable AI behavior.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import time

__all__ = ["BaseGoalArtifact", "GoalArtifactMeta", "SurvivalGoal", "ExplorationGoal", "ResourceGoal"]


class GoalArtifactMeta(type):
    """Metaclass to register goal artifacts with interpreter."""
    
    def __new__(cls, name, bases, attrs):
        goal_class = super().__new__(cls, name, bases, attrs)
        # Register with Grimoire's artifact system
        # This would be integrated with the interpreter's artifact registry
        return goal_class


# Combine the metaclasses properly
from abc import ABCMeta
class CombinedMeta(GoalArtifactMeta, ABCMeta):
    pass


class BaseGoalArtifact(ABC, metaclass=CombinedMeta):
    """Base class for all programmable goal artifacts."""
    
    def __init__(self, name: str, priority: float = 0.5):
        self.name = name
        self.priority = priority  # 0.0 to 1.0
        self.satisfaction_history = []
        self.creation_time = time.time()
        self.last_evaluation = 0.0
        
    @abstractmethod
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Override in subclasses - returns 0.0 to 1.0"""
        raise NotImplementedError("Goals must implement evaluate_satisfaction")
        
    def suggest_action(self, world_state: Dict[str, Any], available_actions: List[Any]) -> Optional[Any]:
        """Override in subclasses - returns best action for this goal"""
        return None
        
    def is_satisfied(self, world_state: Dict[str, Any], threshold: float = 0.9) -> bool:
        """Check if goal is satisfied above threshold."""
        satisfaction = self.evaluate_satisfaction(world_state)
        return satisfaction >= threshold
    
    def get_urgency(self, world_state: Dict[str, Any]) -> float:
        """Calculate urgency based on satisfaction level and priority."""
        satisfaction = self.evaluate_satisfaction(world_state)
        return (1.0 - satisfaction) * self.priority
    
    def update_satisfaction_history(self, world_state: Dict[str, Any]):
        """Update satisfaction history for tracking."""
        satisfaction = self.evaluate_satisfaction(world_state)
        self.satisfaction_history.append({
            'timestamp': time.time(),
            'satisfaction': satisfaction
        })
        
        # Keep only last 100 entries
        if len(self.satisfaction_history) > 100:
            self.satisfaction_history = self.satisfaction_history[-100:]
    
    def get_satisfaction_trend(self) -> float:
        """Get trend in satisfaction over time (positive = improving)."""
        if len(self.satisfaction_history) < 2:
            return 0.0
        
        recent = self.satisfaction_history[-5:]  # Last 5 measurements
        older = self.satisfaction_history[-10:-5]  # Previous 5 measurements
        
        if not older:
            return 0.0
        
        recent_avg = sum(h['satisfaction'] for h in recent) / len(recent)
        older_avg = sum(h['satisfaction'] for h in older) / len(older)
        
        return recent_avg - older_avg


class SurvivalGoal(BaseGoalArtifact):
    """Goal to maintain entity survival/health."""
    
    def __init__(self, name: str, priority: float = 0.9, health_threshold: float = 0.3):
        super().__init__(name, priority)
        self.health_threshold = health_threshold
        
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Satisfaction based on health level."""
        health = world_state.get('health', 1.0)
        max_health = world_state.get('max_health', 1.0)
        
        if max_health <= 0:
            return 0.0
        
        health_ratio = health / max_health
        
        if health_ratio < self.health_threshold:
            return 0.0  # Critical - needs immediate attention
        elif health_ratio < 0.7:
            return 0.3  # Moderate concern
        else:
            return min(1.0, health_ratio)  # Satisfied when healthy
    
    def suggest_action(self, world_state: Dict[str, Any], available_actions: List[Any]) -> Optional[Any]:
        """Suggest healing or defensive actions."""
        health = world_state.get('health', 1.0)
        max_health = world_state.get('max_health', 1.0)
        
        if max_health <= 0:
            return None
        
        health_ratio = health / max_health
        
        if health_ratio < self.health_threshold:
            # Critical - look for healing or retreat actions
            for action in available_actions:
                if hasattr(action, 'name'):
                    if 'heal' in action.name.lower() or 'retreat' in action.name.lower():
                        return action
        
        return None


class ExplorationGoal(BaseGoalArtifact):
    """Goal to explore unknown areas."""
    
    def __init__(self, name: str, priority: float = 0.6, exploration_target: float = 0.8):
        super().__init__(name, priority)
        self.exploration_target = exploration_target
        
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Satisfaction based on exploration coverage."""
        explored_areas = world_state.get('explored_areas', 0)
        total_areas = world_state.get('total_areas', 1)
        
        if total_areas <= 0:
            return 1.0  # Nothing to explore
        
        exploration_ratio = explored_areas / total_areas
        return min(1.0, exploration_ratio / self.exploration_target)
    
    def suggest_action(self, world_state: Dict[str, Any], available_actions: List[Any]) -> Optional[Any]:
        """Suggest exploration actions."""
        for action in available_actions:
            if hasattr(action, 'name'):
                if 'explore' in action.name.lower() or 'move' in action.name.lower():
                    return action
        return None


class ResourceGoal(BaseGoalArtifact):
    """Goal to collect or maintain resources."""
    
    def __init__(self, name: str, priority: float = 0.7, resource_type: str = 'generic', 
                 target_amount: float = 100.0):
        super().__init__(name, priority)
        self.resource_type = resource_type
        self.target_amount = target_amount
        
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Satisfaction based on resource levels."""
        resources = world_state.get('resources', {})
        current_amount = resources.get(self.resource_type, 0.0)
        
        if self.target_amount <= 0:
            return 1.0
        
        resource_ratio = current_amount / self.target_amount
        return min(1.0, resource_ratio)
    
    def suggest_action(self, world_state: Dict[str, Any], available_actions: List[Any]) -> Optional[Any]:
        """Suggest resource collection actions."""
        for action in available_actions:
            if hasattr(action, 'name'):
                if 'collect' in action.name.lower() or 'gather' in action.name.lower():
                    return action
        return None


class TerritorialGoal(BaseGoalArtifact):
    """Goal to control territory or area."""
    
    def __init__(self, name: str, priority: float = 0.8, target_area: float = 100.0):
        super().__init__(name, priority)
        self.target_area = target_area
        
    def evaluate_satisfaction(self, world_state: Dict[str, Any]) -> float:
        """Satisfaction based on controlled territory."""
        controlled_area = world_state.get('controlled_territory', 0.0)
        
        if self.target_area <= 0:
            return 1.0
        
        return min(1.0, controlled_area / self.target_area)
    
    def suggest_action(self, world_state: Dict[str, Any], available_actions: List[Any]) -> Optional[Any]:
        """Suggest territorial expansion actions."""
        for action in available_actions:
            if hasattr(action, 'name'):
                if 'expand' in action.name.lower() or 'claim' in action.name.lower():
                    return action
        return None