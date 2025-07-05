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