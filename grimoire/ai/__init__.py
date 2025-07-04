"""Core AI components: goal/action definitions and planner."""

from .goals import Goal
from .actions import Action, ActionLibrary, ActionResult, ActionEffect
from .conditions import Condition, CallableCondition
from .planner import AIPlanner

# Import new components
try:
    from .goal_artifacts import BaseGoalArtifact, SurvivalGoal, ExplorationGoal, ResourceGoal, TerritorialGoal
    from .world_state import WorldState, WorldStateManager, EntityState
    __all__ = [
        'Goal', 'Action', 'ActionLibrary', 'ActionResult', 'ActionEffect', 
        'Condition', 'CallableCondition', 'AIPlanner',
        'BaseGoalArtifact', 'SurvivalGoal', 'ExplorationGoal', 'ResourceGoal', 'TerritorialGoal',
        'WorldState', 'WorldStateManager', 'EntityState'
    ]
except ImportError:
    # Fall back to legacy exports if new modules aren't available
    __all__ = [
        'Goal', 'Action', 'Condition', 'CallableCondition', 'AIPlanner'
    ]