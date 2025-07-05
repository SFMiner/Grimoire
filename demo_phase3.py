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
Grimoire Phase 3 Demo: Goal Artifacts and Autonomous AI

This demo showcases the Phase 3 implementation featuring:
- Goal artifacts as programmable Grimoire objects
- World state management with subscriptions
- Autonomous AI familiar with goal evaluation loops
- Integration between legacy goals and new goal artifacts
- Mixed evaluation systems for backward compatibility
"""

import time
import threading
from typing import Dict, Any

# Import Grimoire components
from grimoire.interpreter import GrimoireInterpreter
from grimoire.world_state import WorldState, get_world_state
from grimoire.goals import GoalArtifact, register_goal_artifact
from grimoire.familiars.ai_familiar import AIFamiliar, Goal, Action


# =============================================================================
# Custom Goal Artifacts
# =============================================================================

class SurvivalGoal(GoalArtifact):
    """Goal artifact focused on survival needs."""
    
    def __init__(self):
        super().__init__(
            name="survival_artifact",
            priority=0.9,
            target_satisfaction=0.8
        )
    
    def is_satisfied(self, ws: WorldState) -> float:
        """Evaluate survival based on health and energy."""
        health = ws.get("health", 1.0)
        energy = ws.get("energy", 1.0)
        food = ws.get("food", 1.0)
        
        # Survival is the minimum of critical resources
        survival_score = min(health, energy, food)
        return survival_score
    
    def on_achieved(self, ws: WorldState) -> None:
        """Called when survival goal is achieved."""
        print(f"[{self.name}] Survival needs satisfied!")


class ExplorationGoal(GoalArtifact):
    """Goal artifact focused on exploration and knowledge gathering."""
    
    def __init__(self):
        super().__init__(
            name="exploration_artifact",
            priority=0.6,
            target_satisfaction=0.7
        )
    
    def is_satisfied(self, ws: WorldState) -> float:
        """Evaluate exploration based on knowledge and areas explored."""
        knowledge = ws.get("knowledge", 0.0)
        areas_explored = ws.get("areas_explored", 0)
        
        # Exploration satisfaction based on knowledge gained
        exploration_score = min(1.0, knowledge + (areas_explored * 0.1))
        return exploration_score
    
    def on_achieved(self, ws: WorldState) -> None:
        """Called when exploration goal is achieved."""
        print(f"[{self.name}] Exploration goal achieved!")


class ResourceGoal(GoalArtifact):
    """Goal artifact focused on resource gathering."""
    
    def __init__(self):
        super().__init__(
            name="resource_artifact",
            priority=0.7,
            target_satisfaction=0.6
        )
    
    def is_satisfied(self, ws: WorldState) -> float:
        """Evaluate resource gathering based on collected resources."""
        food = ws.get("food", 0.0)
        materials = ws.get("materials", 0.0)
        energy = ws.get("energy", 0.0)
        
        # Resource satisfaction based on total resources
        resource_score = min(1.0, (food + materials + energy) / 3.0)
        return resource_score
    
    def on_achieved(self, ws: WorldState) -> None:
        """Called when resource goal is achieved."""
        print(f"[{self.name}] Resource gathering goal achieved!")


# =============================================================================
# World State Monitoring
# =============================================================================

class WorldStateMonitor:
    """Monitors world state changes and provides feedback."""
    
    def __init__(self):
        self.world_state = get_world_state()
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        """Subscribe to important world state changes."""
        self.world_state.subscribe("health", self.on_health_change)
        self.world_state.subscribe("energy", self.on_energy_change)
        self.world_state.subscribe("food", self.on_food_change)
        self.world_state.subscribe("knowledge", self.on_knowledge_change)
    
    def on_health_change(self, key: str, old_value: Any, new_value: Any):
        """Handle health changes."""
        if new_value < 0.3:
            print(f"[MONITOR] WARNING: Health critically low ({new_value:.2f})")
        elif new_value > old_value:
            print(f"[MONITOR] Health improved: {old_value:.2f} -> {new_value:.2f}")
    
    def on_energy_change(self, key: str, old_value: Any, new_value: Any):
        """Handle energy changes."""
        if new_value < 0.2:
            print(f"[MONITOR] WARNING: Energy critically low ({new_value:.2f})")
        elif new_value > old_value:
            print(f"[MONITOR] Energy restored: {old_value:.2f} -> {new_value:.2f}")
    
    def on_food_change(self, key: str, old_value: Any, new_value: Any):
        """Handle food changes."""
        if new_value < 0.3:
            print(f"[MONITOR] WARNING: Food supplies low ({new_value:.2f})")
        elif new_value > old_value:
            print(f"[MONITOR] Food supplies increased: {old_value:.2f} -> {new_value:.2f}")
    
    def on_knowledge_change(self, key: str, old_value: Any, new_value: Any):
        """Handle knowledge changes."""
        if new_value > old_value:
            print(f"[MONITOR] Knowledge gained: {old_value:.2f} -> {new_value:.2f}")


# =============================================================================
# Demo Environment Simulation
# =============================================================================

class EnvironmentSimulator:
    """Simulates environmental changes that affect world state."""
    
    def __init__(self):
        self.world_state = get_world_state()
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the environment simulation."""
        self.running = True
        self.thread = threading.Thread(target=self._simulate_loop, daemon=True)
        self.thread.start()
        print("[ENVIRONMENT] Simulation started")
    
    def stop(self):
        """Stop the environment simulation."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[ENVIRONMENT] Simulation stopped")
    
    def _simulate_loop(self):
        """Main simulation loop."""
        while self.running:
            # Simulate resource depletion over time
            current_health = self.world_state.get("health", 1.0)
            current_energy = self.world_state.get("energy", 1.0)
            current_food = self.world_state.get("food", 1.0)
            
            # Gradual resource depletion
            new_health = max(0.0, current_health - 0.02)
            new_energy = max(0.0, current_energy - 0.03)
            new_food = max(0.0, current_food - 0.025)
            
            # Update world state
            self.world_state.set("health", new_health)
            self.world_state.set("energy", new_energy)
            self.world_state.set("food", new_food)
            
            # Simulate random events
            import random
            if random.random() < 0.1:  # 10% chance of random event
                event_type = random.choice(["knowledge", "materials", "hazard"])
                if event_type == "knowledge":
                    current_knowledge = self.world_state.get("knowledge", 0.0)
                    self.world_state.set("knowledge", current_knowledge + 0.1)
                elif event_type == "materials":
                    current_materials = self.world_state.get("materials", 0.0)
                    self.world_state.set("materials", current_materials + 0.15)
                elif event_type == "hazard":
                    # Environmental hazard reduces health
                    self.world_state.set("health", max(0.0, new_health - 0.1))
                    print("[ENVIRONMENT] Environmental hazard encountered!")
            
            time.sleep(2.0)  # Update every 2 seconds


# =============================================================================
# Demo Actions for AI Familiar
# =============================================================================

def create_demo_actions():
    """Create demo actions for the AI familiar."""
    actions = []
    
    # Rest action - restores health and energy
    rest_action = Action(
        name="rest",
        precondition=lambda ws: ws.get("energy", 1.0) < 0.8,
        effect=lambda ws: {
            **ws,
            "health": min(1.0, ws.get("health", 1.0) + 0.15),
            "energy": min(1.0, ws.get("energy", 1.0) + 0.2)
        },
        cost=0.1
    )
    actions.append(rest_action)
    
    # Forage action - gathers food
    forage_action = Action(
        name="forage",
        precondition=lambda ws: ws.get("energy", 1.0) > 0.3,
        effect=lambda ws: {
            **ws,
            "food": min(1.0, ws.get("food", 1.0) + 0.25),
            "energy": ws.get("energy", 1.0) - 0.1
        },
        cost=0.2
    )
    actions.append(forage_action)
    
    # Explore action - gains knowledge
    explore_action = Action(
        name="explore",
        precondition=lambda ws: ws.get("energy", 1.0) > 0.2,
        effect=lambda ws: {
            **ws,
            "knowledge": ws.get("knowledge", 0.0) + 0.1,
            "areas_explored": ws.get("areas_explored", 0) + 1,
            "energy": ws.get("energy", 1.0) - 0.15
        },
        cost=0.3
    )
    actions.append(explore_action)
    
    # Craft action - converts materials to useful items
    craft_action = Action(
        name="craft",
        precondition=lambda ws: ws.get("materials", 0.0) > 0.2,
        effect=lambda ws: {
            **ws,
            "materials": ws.get("materials", 0.0) - 0.2,
            "tools": ws.get("tools", 0.0) + 0.1,
            "energy": ws.get("energy", 1.0) - 0.05
        },
        cost=0.15
    )
    actions.append(craft_action)
    
    return actions


# =============================================================================
# Main Demo
# =============================================================================

def main():
    """Run the Phase 3 demo."""
    print("=" * 70)
    print("GRIMOIRE PHASE 3 DEMO: GOAL ARTIFACTS & AUTONOMOUS AI")
    print("=" * 70)
    
    # Initialize world state
    world_state = get_world_state()
    world_state.set("health", 1.0)
    world_state.set("energy", 1.0)
    world_state.set("food", 1.0)
    world_state.set("knowledge", 0.0)
    world_state.set("materials", 0.5)
    world_state.set("tools", 0.0)
    world_state.set("areas_explored", 0)
    
    print(f"[DEMO] Initial world state: {world_state.to_dict()}")
    
    # Create and register goal artifacts
    print("\n[DEMO] Creating goal artifacts...")
    survival_goal = SurvivalGoal()
    exploration_goal = ExplorationGoal()
    resource_goal = ResourceGoal()
    
    register_goal_artifact("survival_artifact", survival_goal)
    register_goal_artifact("exploration_artifact", exploration_goal)
    register_goal_artifact("resource_artifact", resource_goal)
    
    print(f"[DEMO] Registered goals: {list(world_state.to_dict().keys())}")
    
    # Create AI familiar
    print("\n[DEMO] Creating AI familiar...")
    ai_config = {
        "autonomous_enabled": True,
        "autonomous_interval": 3.0,  # Update every 3 seconds
        "exploration_rate": 0.2,
        "decision_threshold": 0.6
    }
    
    ai_familiar = AIFamiliar("demo_ai", ai_config)
    
    # Add demo actions
    demo_actions = create_demo_actions()
    for action in demo_actions:
        ai_familiar.add_action(action)
    
    print(f"[DEMO] AI familiar created with {len(ai_familiar.goals)} goals and {len(ai_familiar.actions)} actions")
    
    # Start monitoring
    print("\n[DEMO] Starting world state monitoring...")
    monitor = WorldStateMonitor()
    
    # Start environment simulation
    print("[DEMO] Starting environment simulation...")
    simulator = EnvironmentSimulator()
    simulator.start()
    
    # Create interpreter for testing built-ins
    print("\n[DEMO] Testing Grimoire built-ins...")
    interpreter = GrimoireInterpreter()
    
    # Test built-in functions
    try:
        # Test get_world_state
        current_state = interpreter.globals.get("get_world_state")(interpreter, [])
        print(f"[DEMO] get_world_state() returned: {len(current_state)} keys")
        
        # Test list_goals
        goals = interpreter.globals.get("list_goals")(interpreter, [])
        print(f"[DEMO] list_goals() returned: {goals}")
        
        # Test evaluate_goal
        survival_satisfaction = interpreter.globals.get("evaluate_goal")(interpreter, ["survival_artifact"])
        print(f"[DEMO] evaluate_goal('survival_artifact') returned: {survival_satisfaction}")
        
    except Exception as e:
        print(f"[DEMO] Error testing built-ins: {e}")
    
    # Run autonomous AI loop
    print("\n[DEMO] Starting autonomous AI loop...")
    print("Press Ctrl+C to stop the demo")
    
    try:
        for i in range(20):  # Run for 20 cycles
            print(f"\n--- Cycle {i+1} ---")
            
            # Trigger autonomous update
            ai_familiar.autonomous_update()
            
            # Show AI status
            status = ai_familiar.get_ai_status()
            print(f"[AI] Goals: {status['goals']}, Decisions: {status['decisions_made']}")
            print(f"[AI] Goal satisfactions: {status['goal_satisfactions']}")
            
            # Show world state
            current_world = world_state.to_dict()
            print(f"[WORLD] Health: {current_world['health']:.2f}, Energy: {current_world['energy']:.2f}, Food: {current_world['food']:.2f}")
            
            time.sleep(4.0)  # Wait between cycles
            
    except KeyboardInterrupt:
        print("\n[DEMO] Stopping demo...")
    
    finally:
        # Cleanup
        simulator.stop()
        ai_familiar.set_autonomous_enabled(False)
        
        print("\n[DEMO] Final AI status:")
        final_status = ai_familiar.get_ai_status()
        for key, value in final_status.items():
            if key != "recent_decisions":
                print(f"  {key}: {value}")
        
        print("\n[DEMO] Recent decisions:")
        for decision in final_status["recent_decisions"]:
            print(f"  - {decision['action']} (confidence: {decision['confidence']:.2f})")
        
        print("\n[DEMO] Demo completed!")


if __name__ == "__main__":
    main()