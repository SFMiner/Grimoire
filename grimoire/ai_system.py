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
Grimoire AI System - Core Intelligence Components

This module implements sophisticated AI behaviors for Grimoire agents including:
- Utility-based decision making with GOAP elements
- Spatial world modeling with agent-specific views
- Objective goal evaluation and satisfaction measurement
- Experience-based learning and adaptation
"""

from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import time
import random
import heapq
import math
from collections import defaultdict, deque
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor


# =============================================================================
# Core Action and Utility System
# =============================================================================

@dataclass
class Action:
    """Represents an action an agent can take with preconditions and effects."""
    name: str
    cost: float = 1.0
    duration: float = 1.0
    preconditions: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def can_execute(self, world_state: Dict[str, Any]) -> bool:
        """Check if preconditions are met."""
        for key, value in self.preconditions.items():
            if key not in world_state:
                return False
            
            # Handle different comparison types
            if isinstance(value, dict) and 'min' in value:
                if world_state[key] < value['min']:
                    return False
            elif isinstance(value, dict) and 'max' in value:
                if world_state[key] > value['max']:
                    return False
            elif world_state[key] != value:
                return False
                
        return True
    
    def apply_effects(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply action effects to world state."""
        new_state = world_state.copy()
        
        for key, value in self.effects.items():
            if isinstance(value, dict):
                if 'add' in value:
                    new_state[key] = new_state.get(key, 0) + value['add']
                elif 'multiply' in value:
                    new_state[key] = new_state.get(key, 1) * value['multiply']
                elif 'set' in value:
                    new_state[key] = value['set']
            else:
                new_state[key] = value
                
        return new_state
    
    def get_priority(self, world_state: Dict[str, Any]) -> float:
        """Calculate dynamic priority based on world state."""
        base_priority = 1.0 / max(0.1, self.cost)
        
        # Boost priority if conditions are urgent
        urgency_bonus = 0.0
        for key, value in self.preconditions.items():
            if key in world_state:
                if isinstance(value, dict) and 'min' in value:
                    ratio = world_state[key] / max(1, value['min'])
                    if ratio < 1.2:  # Close to threshold
                        urgency_bonus += 0.5
                        
        return base_priority + urgency_bonus


class UtilityFunction:
    """Evaluates utility of a world state for a specific goal."""
    
    def __init__(self, goal_name: str, factors: Dict[str, float]):
        self.goal_name = goal_name
        self.factors = factors  # state_key -> weight
        self.normalization_ranges = {
            # Common factor ranges for normalization
            "resources": (0, 1000),
            "territory": (0, 100),
            "health": (0, 100),
            "allies": (0, 10),
            "enemies": (0, 20),
            "exploration": (0, 100),
            "defense": (0, 100),
            "position_x": (0, 100),
            "position_y": (0, 100),
            "energy": (0, 100),
            "reputation": (-100, 100)
        }
        
    def evaluate(self, world_state: Dict[str, Any]) -> float:
        """Calculate utility score for current state."""
        utility = 0.0
        total_weight = 0.0
        
        for factor, weight in self.factors.items():
            if factor in world_state:
                normalized = self._normalize_value(factor, world_state[factor])
                utility += normalized * weight
                total_weight += abs(weight)
                
        # Return weighted average
        return utility / max(1.0, total_weight)
    
    def _normalize_value(self, factor: str, value: Any) -> float:
        """Normalize different value types to 0-1 range."""
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            if factor in self.normalization_ranges:
                min_val, max_val = self.normalization_ranges[factor]
                return max(0, min(1, (value - min_val) / (max_val - min_val)))
            else:
                # Auto-detect reasonable range
                return max(0, min(1, value / 100))
        elif isinstance(value, str):
            # String values get simple hash-based scoring
            return (hash(value) % 100) / 100.0
        else:
            return 0.5  # Default for unknown types


# =============================================================================
# World Model and Spatial Representation
# =============================================================================

@dataclass
class Entity:
    """Represents an entity in the world."""
    id: str
    type: str
    position: Tuple[int, int]
    properties: Dict[str, Any] = field(default_factory=dict)
    last_seen: float = field(default_factory=time.time)


@dataclass
class ResourceNode:
    """Represents a resource in the world."""
    type: str
    amount: int
    regeneration_rate: float = 0.0
    position: Tuple[int, int] = (0, 0)


@dataclass
class Territory:
    """Represents a controlled territory."""
    name: str
    controller: Optional[str]
    bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    size: int
    strategic_value: float = 1.0


class CellType(Enum):
    """Types of world cells."""
    EMPTY = "empty"
    OBSTACLE = "obstacle"
    RESOURCE = "resource"
    TERRITORY = "territory"
    AGENT = "agent"


@dataclass
class WorldCell:
    """Represents a cell in the world grid."""
    type: CellType = CellType.EMPTY
    entities: List[Entity] = field(default_factory=list)
    resources: List[ResourceNode] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)


class WorldModel:
    """Shared environmental model with spatial representation."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[WorldCell() for _ in range(width)] for _ in range(height)]
        self.entities: Dict[str, Entity] = {}
        self.resources: Dict[Tuple[int, int], List[ResourceNode]] = {}
        self.territories: Dict[str, Territory] = {}
        self.global_state = {
            "time": 0,
            "weather": "clear",
            "season": "spring",
            "day_night": "day"
        }
        self.update_lock = threading.Lock()
        
    def add_entity(self, entity: Entity) -> bool:
        """Add an entity to the world."""
        with self.update_lock:
            if not self._is_valid_position(entity.position):
                return False
                
            self.entities[entity.id] = entity
            x, y = entity.position
            self.grid[y][x].entities.append(entity)
            self.grid[y][x].last_updated = time.time()
            return True
    
    def move_entity(self, entity_id: str, new_position: Tuple[int, int]) -> bool:
        """Move an entity to a new position."""
        with self.update_lock:
            if entity_id not in self.entities:
                return False
                
            if not self._is_valid_position(new_position):
                return False
                
            entity = self.entities[entity_id]
            old_x, old_y = entity.position
            new_x, new_y = new_position
            
            # Remove from old position
            self.grid[old_y][old_x].entities.remove(entity)
            
            # Add to new position
            entity.position = new_position
            self.grid[new_y][new_x].entities.append(entity)
            self.grid[new_y][new_x].last_updated = time.time()
            
            return True
    
    def add_resource(self, resource: ResourceNode) -> bool:
        """Add a resource node to the world."""
        with self.update_lock:
            if not self._is_valid_position(resource.position):
                return False
                
            x, y = resource.position
            if (x, y) not in self.resources:
                self.resources[(x, y)] = []
            
            self.resources[(x, y)].append(resource)
            self.grid[y][x].resources.append(resource)
            self.grid[y][x].type = CellType.RESOURCE
            self.grid[y][x].last_updated = time.time()
            
            return True
    
    def get_agent_view(self, agent_id: str, vision_range: int) -> 'AgentWorldView':
        """Get limited world view for specific agent."""
        view = AgentWorldView(agent_id)
        
        if agent_id not in self.entities:
            return view
            
        agent = self.entities[agent_id]
        x, y = agent.position
        
        # Copy visible portion of world
        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                nx, ny = x + dx, y + dy
                if self._is_valid_position((nx, ny)):
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= vision_range:
                        if self._has_line_of_sight((x, y), (nx, ny)):
                            view.update_cell(nx, ny, self.grid[ny][nx])
                            
        # Add known global state
        view.global_knowledge.update(self.global_state)
        
        return view
    
    def get_neighbors(self, position: Tuple[int, int], radius: int = 1) -> List[Tuple[int, int]]:
        """Get neighboring positions within radius."""
        x, y = position
        neighbors = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self._is_valid_position((nx, ny)):
                    neighbors.append((nx, ny))
                    
        return neighbors
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find shortest path between two points using A*."""
        if not self._is_valid_position(start) or not self._is_valid_position(goal):
            return []
            
        # Simple A* implementation
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._manhattan_distance(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            for neighbor in self.get_neighbors(current):
                if not self._is_passable(neighbor):
                    continue
                    
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No path found
    
    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if position is within world bounds."""
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _is_passable(self, position: Tuple[int, int]) -> bool:
        """Check if position can be moved through."""
        if not self._is_valid_position(position):
            return False
        x, y = position
        cell = self.grid[y][x]
        return cell.type != CellType.OBSTACLE
    
    def _has_line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if there's a clear line of sight between two points."""
        # Simplified line of sight - just check for obstacles
        x1, y1 = start
        x2, y2 = end
        
        # Bresenham's line algorithm (simplified)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if not self._is_passable((x, y)):
                return False
                
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
        return True
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class AgentWorldView:
    """Agent's personal view of the world (may be incomplete/outdated)."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.known_cells: Dict[Tuple[int, int], WorldCell] = {}
        self.last_updated: Dict[Tuple[int, int], float] = {}
        self.entity_positions: Dict[str, Tuple[int, int]] = {}
        self.resource_locations: List[Tuple[int, int]] = []
        self.territory_knowledge: Dict[str, Territory] = {}
        self.global_knowledge: Dict[str, Any] = {}
        
    def update_cell(self, x: int, y: int, cell: WorldCell):
        """Update knowledge about a world cell."""
        position = (x, y)
        self.known_cells[position] = cell
        self.last_updated[position] = time.time()
        
        # Update entity tracking
        for entity in cell.entities:
            self.entity_positions[entity.id] = position
            
        # Update resource tracking
        if cell.resources:
            if position not in self.resource_locations:
                self.resource_locations.append(position)
        elif position in self.resource_locations:
            self.resource_locations.remove(position)
    
    def find_nearest_resource(self, position: Tuple[int, int], resource_type: str) -> Optional[Tuple[int, int]]:
        """Find nearest known resource of given type."""
        nearest = None
        min_distance = float('inf')
        
        for loc in self.resource_locations:
            if loc in self.known_cells:
                cell = self.known_cells[loc]
                for resource in cell.resources:
                    if resource.type == resource_type:
                        dist = self._manhattan_distance(position, loc)
                        if dist < min_distance:
                            min_distance = dist
                            nearest = loc
                            
        return nearest
    
    def find_nearest_entity(self, position: Tuple[int, int], entity_type: str) -> Optional[Tuple[int, int]]:
        """Find nearest known entity of given type."""
        nearest = None
        min_distance = float('inf')
        
        for entity_id, entity_pos in self.entity_positions.items():
            if entity_pos in self.known_cells:
                cell = self.known_cells[entity_pos]
                for entity in cell.entities:
                    if entity.type == entity_type:
                        dist = self._manhattan_distance(position, entity_pos)
                        if dist < min_distance:
                            min_distance = dist
                            nearest = entity_pos
                            
        return nearest
    
    def get_knowledge_completeness(self) -> float:
        """Estimate how complete the agent's world knowledge is."""
        if not self.known_cells:
            return 0.0
            
        # Simple metric based on knowledge freshness
        current_time = time.time()
        total_freshness = 0.0
        
        for pos, timestamp in self.last_updated.items():
            age = current_time - timestamp
            freshness = max(0.0, 1.0 - age / 300.0)  # 5 minute decay
            total_freshness += freshness
            
        return total_freshness / len(self.known_cells)
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# =============================================================================
# Enhanced Decision Making System
# =============================================================================

@dataclass
class Experience:
    """Represents a learning experience."""
    state: Dict[str, Any]
    action: str
    outcome: Dict[str, Any]
    utility: float
    timestamp: float


class ExperienceMemory:
    """Tracks agent experiences for learning."""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.experiences: deque = deque(maxlen=capacity)
        self.action_outcomes: Dict[str, List[float]] = defaultdict(list)
        self.context_memories: Dict[str, List[Experience]] = defaultdict(list)
        
    def record_experience(self, state: Dict, action: Action, 
                         outcome: Dict, utility_gained: float):
        """Record an experience for learning."""
        exp = Experience(
            state=state.copy(),
            action=action.name,
            outcome=outcome.copy(),
            utility=utility_gained,
            timestamp=time.time()
        )
        
        self.experiences.append(exp)
        
        # Track action effectiveness
        self.action_outcomes[action.name].append(utility_gained)
        if len(self.action_outcomes[action.name]) > 100:  # Keep recent history
            self.action_outcomes[action.name].pop(0)
            
        # Store by context for pattern recognition
        context_key = self._get_context_key(state)
        self.context_memories[context_key].append(exp)
        if len(self.context_memories[context_key]) > 50:
            self.context_memories[context_key].pop(0)
            
    def get_action_effectiveness(self, action_name: str) -> float:
        """Get average effectiveness of an action."""
        if action_name not in self.action_outcomes:
            return 0.5  # Neutral/unknown
            
        outcomes = self.action_outcomes[action_name]
        if not outcomes:
            return 0.5
            
        # Recent outcomes weighted more heavily
        weights = [0.9 ** i for i in range(len(outcomes) - 1, -1, -1)]
        weighted_sum = sum(o * w for o, w in zip(outcomes, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.5
    
    def get_context_effectiveness(self, context_state: Dict[str, Any], action_name: str) -> float:
        """Get effectiveness of action in similar contexts."""
        context_key = self._get_context_key(context_state)
        
        if context_key not in self.context_memories:
            return self.get_action_effectiveness(action_name)
            
        relevant_experiences = [
            exp for exp in self.context_memories[context_key] 
            if exp.action == action_name
        ]
        
        if not relevant_experiences:
            return self.get_action_effectiveness(action_name)
            
        utilities = [exp.utility for exp in relevant_experiences]
        return sum(utilities) / len(utilities)
    
    def _get_context_key(self, state: Dict[str, Any]) -> str:
        """Generate a context key for state pattern recognition."""
        # Create a simplified state signature for pattern matching
        key_factors = []
        
        # Include key environmental factors
        for key in ['territory', 'resources', 'enemies', 'allies', 'health']:
            if key in state:
                value = state[key]
                if isinstance(value, (int, float)):
                    # Bucket numeric values
                    bucket = int(value / 25) * 25
                    key_factors.append(f"{key}:{bucket}")
                else:
                    key_factors.append(f"{key}:{value}")
                    
        return "|".join(sorted(key_factors))


class DecisionEngine:
    """Enhanced decision-making system for agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.available_actions: List[Action] = []
        self.utility_functions: Dict[str, UtilityFunction] = {}
        self.world_state: Dict[str, Any] = {}
        self.planning_horizon = 3  # Look ahead steps
        self.exploration_rate = 0.1  # Probability of trying new things
        self.memory = ExperienceMemory()
        
    def add_action(self, action: Action):
        """Add an available action."""
        self.available_actions.append(action)
        
    def add_utility_function(self, goal_name: str, utility_fn: UtilityFunction):
        """Add a utility function for a specific goal."""
        self.utility_functions[goal_name] = utility_fn
        
    def update_world_state(self, new_state: Dict[str, Any]):
        """Update the agent's perception of world state."""
        self.world_state.update(new_state)
        
    def decide_action(self, current_goal: Optional[str] = None) -> Optional[Action]:
        """Select best action using utility evaluation and planning."""
        if not self.available_actions:
            return None
            
        # Exploration vs exploitation
        if random.random() < self.exploration_rate:
            valid_actions = [a for a in self.available_actions 
                           if a.can_execute(self.world_state)]
            if valid_actions:
                return random.choice(valid_actions)
        
        # Get utility function for current goal
        if not current_goal or current_goal not in self.utility_functions:
            return None
            
        utility_fn = self.utility_functions[current_goal]
        
        # Evaluate all possible actions
        best_action = None
        best_utility = -float('inf')
        
        for action in self.available_actions:
            if action.can_execute(self.world_state):
                # Simulate action effects
                future_state = action.apply_effects(self.world_state)
                
                # Look ahead with simple planning
                utility = self._evaluate_action_sequence(
                    [action], future_state, utility_fn, depth=0
                )
                
                # Factor in action cost and past experience
                cost_penalty = action.cost * 0.1
                experience_bonus = self.memory.get_context_effectiveness(
                    self.world_state, action.name
                ) * 0.2
                
                total_utility = utility - cost_penalty + experience_bonus
                
                if total_utility > best_utility:
                    best_utility = total_utility
                    best_action = action
                    
        return best_action
    
    def _evaluate_action_sequence(self, actions: List[Action], 
                                  state: Dict[str, Any], 
                                  utility_fn: UtilityFunction, 
                                  depth: int) -> float:
        """Recursively evaluate action sequences up to planning horizon."""
        if depth >= self.planning_horizon:
            return utility_fn.evaluate(state)
            
        current_utility = utility_fn.evaluate(state)
        best_future_utility = current_utility
        
        # Try each possible next action
        for next_action in self.available_actions:
            if next_action.can_execute(state):
                future_state = next_action.apply_effects(state)
                future_utility = self._evaluate_action_sequence(
                    actions + [next_action], future_state, utility_fn, depth + 1
                )
                best_future_utility = max(best_future_utility, future_utility)
                
        # Discount future utility
        discount_factor = 0.9 ** depth
        return current_utility + (best_future_utility - current_utility) * discount_factor


# =============================================================================
# Goal Evaluation System
# =============================================================================

class GoalEvaluator:
    """Evaluates goal satisfaction based on measurable world state."""
    
    def __init__(self):
        self.evaluation_functions = {
            "territorial_control": self._eval_territorial_control,
            "resource_maximization": self._eval_resources,
            "alliance_building": self._eval_alliances,
            "exploration_coverage": self._eval_exploration,
            "defensive_positioning": self._eval_defense,
            "economic_growth": self._eval_economic_growth,
            "military_strength": self._eval_military_strength,
            "diplomatic_influence": self._eval_diplomatic_influence
        }
        
    def evaluate_goal(self, goal_name: str, agent_state: Dict[str, Any], 
                     world_view: AgentWorldView) -> float:
        """Calculate objective satisfaction level for a goal."""
        eval_fn = self.evaluation_functions.get(goal_name)
        if not eval_fn:
            return 0.0
            
        return eval_fn(agent_state, world_view)
    
    def _eval_territorial_control(self, agent_state: Dict[str, Any], 
                                 world_view: AgentWorldView) -> float:
        """Measure territorial control as percentage of known area controlled."""
        controlled_cells = agent_state.get('controlled_territory', 0)
        total_known = len(world_view.known_cells)
        
        if total_known == 0:
            return 0.0
            
        return min(1.0, controlled_cells / total_known)
    
    def _eval_resources(self, agent_state: Dict[str, Any], 
                       world_view: AgentWorldView) -> float:
        """Measure resource accumulation."""
        total_resources = agent_state.get('total_resources', 0)
        max_possible = 1000  # Domain-specific maximum
        
        return min(1.0, total_resources / max_possible)
    
    def _eval_alliances(self, agent_state: Dict[str, Any], 
                       world_view: AgentWorldView) -> float:
        """Measure alliance strength and count."""
        ally_count = agent_state.get('ally_count', 0)
        ally_strength = agent_state.get('ally_strength', 0)
        max_allies = 5  # Reasonable maximum
        
        count_score = min(1.0, ally_count / max_allies)
        strength_score = min(1.0, ally_strength / 100)
        
        return (count_score + strength_score) / 2
    
    def _eval_exploration(self, agent_state: Dict[str, Any], 
                         world_view: AgentWorldView) -> float:
        """Measure exploration coverage."""
        return world_view.get_knowledge_completeness()
    
    def _eval_defense(self, agent_state: Dict[str, Any], 
                     world_view: AgentWorldView) -> float:
        """Measure defensive positioning and strength."""
        defensive_strength = agent_state.get('defensive_strength', 0)
        position_score = agent_state.get('position_defensibility', 0.5)
        
        strength_score = min(1.0, defensive_strength / 100)
        
        return (strength_score + position_score) / 2
    
    def _eval_economic_growth(self, agent_state: Dict[str, Any], 
                             world_view: AgentWorldView) -> float:
        """Measure economic growth and resource production."""
        production_rate = agent_state.get('resource_production_rate', 0)
        economic_efficiency = agent_state.get('economic_efficiency', 0.5)
        
        production_score = min(1.0, production_rate / 50)
        
        return (production_score + economic_efficiency) / 2
    
    def _eval_military_strength(self, agent_state: Dict[str, Any], 
                               world_view: AgentWorldView) -> float:
        """Measure military capabilities."""
        military_units = agent_state.get('military_units', 0)
        military_effectiveness = agent_state.get('military_effectiveness', 0.5)
        
        unit_score = min(1.0, military_units / 20)
        
        return (unit_score + military_effectiveness) / 2
    
    def _eval_diplomatic_influence(self, agent_state: Dict[str, Any], 
                                  world_view: AgentWorldView) -> float:
        """Measure diplomatic influence and reputation."""
        reputation = agent_state.get('reputation', 0)
        diplomatic_relations = agent_state.get('diplomatic_relations', 0)
        
        reputation_score = (reputation + 100) / 200  # Normalize -100 to 100 range
        relations_score = min(1.0, diplomatic_relations / 10)
        
        return (reputation_score + relations_score) / 2


# =============================================================================
# Action Library for Different Agent Types
# =============================================================================

def create_archon_actions() -> List[Action]:
    """Create action library for Archon agents."""
    actions = []
    
    # Strategic actions
    actions.append(Action(
        name="expand_territory",
        cost=5.0,
        duration=10.0,
        preconditions={"military_strength": {"min": 20}, "resources": {"min": 100}},
        effects={"controlled_territory": {"add": 10}, "resources": {"add": -50}},
        tags={"strategic", "territorial"}
    ))
    
    actions.append(Action(
        name="form_alliance",
        cost=3.0,
        duration=5.0,
        preconditions={"reputation": {"min": 0}, "diplomatic_power": {"min": 10}},
        effects={"ally_count": {"add": 1}, "diplomatic_power": {"add": -5}},
        tags={"diplomatic", "strategic"}
    ))
    
    actions.append(Action(
        name="build_infrastructure",
        cost=8.0,
        duration=15.0,
        preconditions={"resources": {"min": 200}, "controlled_territory": {"min": 20}},
        effects={"economic_efficiency": {"add": 0.1}, "resources": {"add": -150}},
        tags={"economic", "strategic"}
    ))
    
    actions.append(Action(
        name="recruit_spirits",
        cost=4.0,
        duration=3.0,
        preconditions={"resources": {"min": 50}, "reputation": {"min": 10}},
        effects={"spirit_count": {"add": 1}, "resources": {"add": -30}},
        tags={"management", "strategic"}
    ))
    
    return actions


def create_spirit_actions() -> List[Action]:
    """Create action library for Spirit agents."""
    actions = []
    
    # Tactical actions
    actions.append(Action(
        name="patrol_area",
        cost=2.0,
        duration=3.0,
        preconditions={"energy": {"min": 20}},
        effects={"area_knowledge": {"add": 5}, "energy": {"add": -10}},
        tags={"exploration", "tactical"}
    ))
    
    actions.append(Action(
        name="gather_resources",
        cost=3.0,
        duration=5.0,
        preconditions={"energy": {"min": 30}, "known_resources": {"min": 1}},
        effects={"resources": {"add": 25}, "energy": {"add": -20}},
        tags={"economic", "tactical"}
    ))
    
    actions.append(Action(
        name="coordinate_familiars",
        cost=2.0,
        duration=2.0,
        preconditions={"familiar_count": {"min": 2}},
        effects={"coordination_bonus": {"add": 0.1}},
        tags={"management", "tactical"}
    ))
    
    actions.append(Action(
        name="establish_outpost",
        cost=5.0,
        duration=8.0,
        preconditions={"resources": {"min": 75}, "area_knowledge": {"min": 20}},
        effects={"outpost_count": {"add": 1}, "defensive_strength": {"add": 15}},
        tags={"defensive", "tactical"}
    ))
    
    return actions


def create_familiar_actions() -> List[Action]:
    """Create action library for Familiar agents."""
    actions = []
    
    # Operational actions
    actions.append(Action(
        name="move_to_position",
        cost=1.0,
        duration=1.0,
        preconditions={"energy": {"min": 5}},
        effects={"position_updated": {"set": True}, "energy": {"add": -5}},
        tags={"movement", "operational"}
    ))
    
    actions.append(Action(
        name="collect_resource",
        cost=2.0,
        duration=2.0,
        preconditions={"energy": {"min": 10}, "at_resource": True},
        effects={"carried_resources": {"add": 10}, "energy": {"add": -10}},
        tags={"economic", "operational"}
    ))
    
    actions.append(Action(
        name="scout_area",
        cost=1.5,
        duration=2.0,
        preconditions={"energy": {"min": 15}},
        effects={"scouted_cells": {"add": 3}, "energy": {"add": -10}},
        tags={"exploration", "operational"}
    ))
    
    actions.append(Action(
        name="defend_position",
        cost=2.0,
        duration=4.0,
        preconditions={"energy": {"min": 20}},
        effects={"defensive_bonus": {"add": 5}, "energy": {"add": -15}},
        tags={"defensive", "operational"}
    ))
    
    actions.append(Action(
        name="report_to_spirit",
        cost=0.5,
        duration=1.0,
        preconditions={},
        effects={"last_report_time": {"set": "current"}},
        tags={"communication", "operational"}
    ))
    
    return actions


# =============================================================================
# Integration Helper Functions
# =============================================================================

def create_utility_functions_for_agent(agent_type: str, domain: str) -> Dict[str, UtilityFunction]:
    """Create appropriate utility functions for different agent types and domains."""
    utility_functions = {}
    
    if agent_type == "archon":
        if domain == "Combat":
            utility_functions["territorial_control"] = UtilityFunction(
                "territorial_control",
                {"controlled_territory": 0.4, "military_strength": 0.3, "defensive_strength": 0.3}
            )
            utility_functions["military_strength"] = UtilityFunction(
                "military_strength", 
                {"military_units": 0.5, "military_effectiveness": 0.3, "ally_count": 0.2}
            )
        elif domain == "Economy":
            utility_functions["resource_maximization"] = UtilityFunction(
                "resource_maximization",
                {"total_resources": 0.4, "resource_production_rate": 0.4, "economic_efficiency": 0.2}
            )
            utility_functions["economic_growth"] = UtilityFunction(
                "economic_growth",
                {"economic_efficiency": 0.5, "resource_production_rate": 0.3, "controlled_territory": 0.2}
            )
        elif domain == "Diplomacy":
            utility_functions["alliance_building"] = UtilityFunction(
                "alliance_building",
                {"ally_count": 0.4, "reputation": 0.4, "diplomatic_influence": 0.2}
            )
            utility_functions["diplomatic_influence"] = UtilityFunction(
                "diplomatic_influence",
                {"reputation": 0.5, "diplomatic_relations": 0.3, "ally_strength": 0.2}
            )
    
    elif agent_type == "spirit":
        if domain == "Combat":
            utility_functions["defensive_positioning"] = UtilityFunction(
                "defensive_positioning",
                {"defensive_strength": 0.4, "position_defensibility": 0.3, "area_control": 0.3}
            )
        elif domain == "Economy":
            utility_functions["resource_maximization"] = UtilityFunction(
                "resource_maximization",
                {"resources": 0.5, "resource_production_rate": 0.3, "economic_efficiency": 0.2}
            )
        else:  # General
            utility_functions["exploration_coverage"] = UtilityFunction(
                "exploration_coverage",
                {"area_knowledge": 0.5, "scouted_cells": 0.3, "position_updated": 0.2}
            )
    
    elif agent_type == "familiar":
        utility_functions["task_completion"] = UtilityFunction(
            "task_completion",
            {"carried_resources": 0.3, "scouted_cells": 0.3, "defensive_bonus": 0.2, "energy": 0.2}
        )
    
    return utility_functions