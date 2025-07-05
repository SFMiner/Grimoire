#!/usr/bin/env python3
"""
Grimoire Standard Library

This module provides common familiar types and utilities for game development,
including Player, NPC, Monster entities, and utility familiars like Timer,
Logger, and FileHandler.
"""

import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path

from .familiars.entity_familiar import EntityFamiliar
from .familiars.ai_familiar import AIFamiliar, Goal, Action
from .familiars.types import FamiliarType, FamiliarCapability
from .world_state import get_world_state


# =============================================================================
# Game Entity Familiars
# =============================================================================

class PlayerFamiliar(EntityFamiliar):
    """
    Familiar representing a player character.
    
    Provides standard player functionality including inventory,
    stats, input handling, and interaction capabilities.
    """
    
    def __init__(self, name: str, player_data: Optional[Dict[str, Any]] = None):
        super().__init__(name)
        
        # Set player data after initialization
        if player_data:
            for key, value in player_data.items():
                self.set_property(key, value)
        
        # Default player properties
        self.set_property("level", 1)
        self.set_property("experience", 0)
        self.set_property("health", 100)
        self.set_property("max_health", 100)
        self.set_property("mana", 50)
        self.set_property("max_mana", 50)
        self.set_property("inventory", {})
        self.set_property("equipment", {})
        self.set_property("stats", {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        })
        
        # Player-specific sockets
        self.add_socket("input", direction="input")
        self.add_socket("action_output", direction="output")
        self.add_socket("status_output", direction="output")
        
        # Input command queue
        self.command_queue: List[str] = []
        self.command_lock = threading.Lock()
    
    def add_item(self, item_name: str, quantity: int = 1) -> bool:
        """Add item to player inventory."""
        inventory = self.get_property("inventory", {})
        if item_name in inventory:
            inventory[item_name] += quantity
        else:
            inventory[item_name] = quantity
        
        self.set_property("inventory", inventory)
        
        self.log_activity(
            "self",
            f"Added {quantity} {item_name} to inventory",
            {"item": item_name, "quantity": quantity}
        )
        
        # Notify through socket
        self.send_to_socket("status_output", {
            "type": "inventory_update",
            "item": item_name,
            "quantity": inventory[item_name]
        })
        
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from player inventory."""
        inventory = self.properties["inventory"]
        if item_name not in inventory or inventory[item_name] < quantity:
            return False
        
        inventory[item_name] -= quantity
        if inventory[item_name] <= 0:
            del inventory[item_name]
        
        self.log_activity(
            "self",
            f"Removed {quantity} {item_name} from inventory",
            {"item": item_name, "quantity": quantity}
        )
        
        return True
    
    def equip_item(self, item_name: str, slot: str) -> bool:
        """Equip item to specific slot."""
        if not self.remove_item(item_name, 1):
            return False
        
        # Unequip current item if any
        equipment = self.properties["equipment"]
        if slot in equipment:
            self.add_item(equipment[slot], 1)
        
        equipment[slot] = item_name
        
        self.log_activity(
            "self",
            f"Equipped {item_name} to {slot}",
            {"item": item_name, "slot": slot}
        )
        
        return True
    
    def gain_experience(self, amount: int) -> bool:
        """Gain experience points and check for level up."""
        self.properties["experience"] += amount
        
        # Simple level up calculation
        level = self.properties["level"]
        exp_needed = level * 100  # 100 exp per level
        
        leveled_up = False
        while self.properties["experience"] >= exp_needed:
            self.properties["experience"] -= exp_needed
            self.properties["level"] += 1
            level += 1
            exp_needed = level * 100
            leveled_up = True
            
            # Increase max health and mana on level up
            self.properties["max_health"] += 10
            self.properties["max_mana"] += 5
            self.properties["health"] = self.properties["max_health"]
            self.properties["mana"] = self.properties["max_mana"]
        
        if leveled_up:
            self.log_activity(
                "self",
                f"Leveled up to {self.properties['level']}!",
                {"new_level": self.properties["level"]}
            )
            
            self.send_to_socket("status_output", {
                "type": "level_up",
                "level": self.properties["level"]
            })
        
        return leveled_up
    
    def take_damage(self, amount: int) -> bool:
        """Take damage and check for death."""
        self.properties["health"] = max(0, self.properties["health"] - amount)
        
        self.log_activity(
            "self",
            f"Took {amount} damage",
            {"damage": amount, "remaining_health": self.properties["health"]}
        )
        
        if self.properties["health"] <= 0:
            self.log_activity("self", "Player died!", {"cause": "damage"})
            self.send_to_socket("status_output", {
                "type": "death",
                "cause": "damage"
            })
            return True  # Died
        
        return False  # Survived
    
    def heal(self, amount: int) -> None:
        """Heal the player."""
        max_health = self.properties["max_health"]
        old_health = self.properties["health"]
        self.properties["health"] = min(max_health, old_health + amount)
        
        actual_healing = self.properties["health"] - old_health
        
        if actual_healing > 0:
            self.log_activity(
                "self",
                f"Healed for {actual_healing} points",
                {"healing": actual_healing}
            )
    
    def queue_command(self, command: str) -> None:
        """Queue a command for processing."""
        with self.command_lock:
            self.command_queue.append(command)
    
    def process_commands(self) -> List[str]:
        """Process and return queued commands."""
        with self.command_lock:
            commands = self.command_queue.copy()
            self.command_queue.clear()
        
        return commands


class NPCFamiliar(AIFamiliar):
    """
    Familiar representing a non-player character.
    
    Combines AI decision making with NPC-specific behaviors
    like dialogue, quests, and interaction patterns.
    """
    
    def __init__(self, name: str, npc_data: Optional[Dict[str, Any]] = None):
        ai_config = {
            "autonomous_enabled": True,
            "autonomous_interval": 5.0,  # NPCs update every 5 seconds
            "exploration_rate": 0.1,     # NPCs are less exploratory
            "decision_threshold": 0.8    # NPCs are more conservative
        }
        
        super().__init__(name, ai_config)
        
        # NPC-specific properties
        self.npc_data = npc_data or {}
        self.dialogue_tree = self.npc_data.get("dialogue", {})
        self.quest_data = self.npc_data.get("quests", [])
        self.personality = self.npc_data.get("personality", "neutral")
        self.faction = self.npc_data.get("faction", "neutral")
        
        # NPC sockets
        self.add_socket("dialogue_input", direction="input")
        self.add_socket("dialogue_output", direction="output")
        self.add_socket("quest_output", direction="output")
        
        # Initialize NPC-specific goals
        self._initialize_npc_goals()
        self._initialize_npc_actions()
    
    def _initialize_npc_goals(self) -> None:
        """Initialize NPC-specific goals."""
        # Social goal - interact with players
        social_goal = Goal(
            name="social_interaction",
            priority=0.6,
            domain="social",
            evaluation_function=lambda ws: ws.get("recent_interactions", 0) / 10.0
        )
        self.add_goal(social_goal)
        
        # Routine goal - follow daily routine
        routine_goal = Goal(
            name="daily_routine",
            priority=0.8,
            domain="routine",
            evaluation_function=lambda ws: 1.0 if ws.get("time_of_day", 12) % 24 < 18 else 0.5
        )
        self.add_goal(routine_goal)
    
    def _initialize_npc_actions(self) -> None:
        """Initialize NPC-specific actions."""
        # Greet action
        greet_action = Action(
            name="greet_player",
            precondition=lambda ws: ws.get("player_nearby", False),
            effect=lambda ws: {**ws, "recent_interactions": ws.get("recent_interactions", 0) + 1},
            cost=0.1
        )
        self.add_action(greet_action)
        
        # Wander action
        wander_action = Action(
            name="wander",
            precondition=lambda ws: not ws.get("player_nearby", False),
            effect=lambda ws: {
                **ws,
                "position_x": ws.get("position_x", 0) + 1
            },
            cost=0.2
        )
        self.add_action(wander_action)
    
    def start_dialogue(self, player_name: str, topic: str = "greeting") -> Dict[str, Any]:
        """Start dialogue with a player."""
        if topic not in self.dialogue_tree:
            topic = "default"
        
        dialogue_entry = self.dialogue_tree.get(topic, {
            "text": "Hello there!",
            "options": ["Goodbye"]
        })
        
        self.log_activity(
            "inter_familiar",
            f"Started dialogue with {player_name}",
            {"topic": topic, "player": player_name}
        )
        
        # Send dialogue through socket
        dialogue_response = {
            "type": "dialogue",
            "npc_name": self.name,
            "text": dialogue_entry["text"],
            "options": dialogue_entry.get("options", []),
            "topic": topic
        }
        
        self.send_to_socket("dialogue_output", dialogue_response)
        
        return dialogue_response
    
    def offer_quest(self, player_name: str, quest_id: str) -> Optional[Dict[str, Any]]:
        """Offer a quest to a player."""
        quest = next((q for q in self.quest_data if q.get("id") == quest_id), None)
        
        if not quest:
            return None
        
        quest_offer = {
            "type": "quest_offer",
            "npc_name": self.name,
            "quest_id": quest_id,
            "title": quest.get("title", "Unknown Quest"),
            "description": quest.get("description", ""),
            "rewards": quest.get("rewards", []),
            "requirements": quest.get("requirements", [])
        }
        
        self.send_to_socket("quest_output", quest_offer)
        
        self.log_activity(
            "inter_familiar",
            f"Offered quest {quest_id} to {player_name}",
            {"quest_id": quest_id, "player": player_name}
        )
        
        return quest_offer


class MonsterFamiliar(AIFamiliar):
    """
    Familiar representing a hostile monster.
    
    Focused on combat AI with aggressive behaviors,
    territory defense, and combat tactics.
    """
    
    def __init__(self, name: str, monster_data: Optional[Dict[str, Any]] = None):
        ai_config = {
            "autonomous_enabled": True,
            "autonomous_interval": 2.0,  # Monsters react quickly
            "exploration_rate": 0.3,     # Monsters are more unpredictable
            "decision_threshold": 0.6    # Monsters are more aggressive
        }
        
        super().__init__(name, ai_config)
        
        # Monster-specific properties
        self.monster_data = monster_data or {}
        self.aggression_level = self.monster_data.get("aggression", 0.7)
        self.territory_center = self.monster_data.get("territory", {"x": 0, "y": 0})
        self.territory_radius = self.monster_data.get("territory_radius", 10)
        self.combat_stats = self.monster_data.get("combat_stats", {
            "attack": 10,
            "defense": 5,
            "health": 50,
            "speed": 5
        })
        
        # Combat sockets
        self.add_socket("combat_input", direction="input")
        self.add_socket("combat_output", direction="output")
        self.add_socket("threat_detection", direction="input")
        
        # Initialize monster goals and actions
        self._initialize_monster_goals()
        self._initialize_monster_actions()
    
    def _initialize_monster_goals(self) -> None:
        """Initialize monster-specific goals."""
        # Survival goal
        survival_goal = Goal(
            name="survival",
            priority=0.9,
            domain="survival",
            evaluation_function=lambda ws: ws.get("health", 100) / 100.0
        )
        self.add_goal(survival_goal)
        
        # Territory defense goal
        territory_goal = Goal(
            name="defend_territory",
            priority=0.8,
            domain="combat",
            evaluation_function=lambda ws: 1.0 if not ws.get("intruders_nearby", False) else 0.0
        )
        self.add_goal(territory_goal)
        
        # Hunt goal
        hunt_goal = Goal(
            name="hunt_prey",
            priority=0.6,
            domain="combat",
            evaluation_function=lambda ws: 1.0 if ws.get("prey_nearby", False) else 0.0
        )
        self.add_goal(hunt_goal)
    
    def _initialize_monster_actions(self) -> None:
        """Initialize monster-specific actions."""
        # Attack action
        attack_action = Action(
            name="attack",
            precondition=lambda ws: ws.get("target_in_range", False),
            effect=lambda ws: {
                **ws, 
                "last_attack_time": time.time(),
                "aggression": min(1.0, ws.get("aggression", 0.5) + 0.1)
            },
            cost=0.3
        )
        self.add_action(attack_action)
        
        # Patrol action
        patrol_action = Action(
            name="patrol",
            precondition=lambda ws: not ws.get("target_in_range", False),
            effect=lambda ws: {
                **ws,
                "patrol_progress": (ws.get("patrol_progress", 0) + 1) % 4
            },
            cost=0.2
        )
        self.add_action(patrol_action)
        
        # Flee action
        flee_action = Action(
            name="flee",
            precondition=lambda ws: ws.get("health", 100) < 20,
            effect=lambda ws: {
                **ws,
                "fleeing": True,
                "flee_start_time": time.time()
            },
            cost=0.4
        )
        self.add_action(flee_action)
    
    def detect_threat(self, threat_data: Dict[str, Any]) -> None:
        """Process threat detection."""
        threat_level = threat_data.get("level", 0.0)
        threat_position = threat_data.get("position", {"x": 0, "y": 0})
        
        # Update world model with threat information
        self.update_world_model({
            "threat_level": threat_level,
            "threat_position": threat_position,
            "target_in_range": threat_data.get("in_range", False),
            "intruders_nearby": threat_level > 0.3
        })
        
        self.log_activity(
            "environmental",
            f"Threat detected: level {threat_level}",
            {"threat_data": threat_data}
        )
    
    def execute_attack(self, target: str) -> Dict[str, Any]:
        """Execute attack on target."""
        attack_power = self.combat_stats["attack"]
        
        attack_result = {
            "type": "attack",
            "attacker": self.name,
            "target": target,
            "damage": attack_power,
            "timestamp": time.time()
        }
        
        self.send_to_socket("combat_output", attack_result)
        
        self.log_activity(
            "inter_familiar",
            f"Attacked {target} for {attack_power} damage",
            {"target": target, "damage": attack_power}
        )
        
        return attack_result


# =============================================================================
# Utility Familiars
# =============================================================================

class TimerFamiliar(EntityFamiliar):
    """
    Utility familiar for timing and scheduling operations.
    
    Provides countdown timers, intervals, scheduling,
    and time-based event triggering.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        
        # Timer state
        self.timers: Dict[str, Dict[str, Any]] = {}
        self.timer_lock = threading.Lock()
        self.timer_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Timer sockets
        self.add_socket("timer_commands", direction="input")
        self.add_socket("timer_events", direction="output")
        
        # Start timer thread
        self.start_timer_thread()
    
    def start_timer_thread(self) -> None:
        """Start the timer processing thread."""
        if self.running:
            return
        
        self.running = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
    
    def stop_timer_thread(self) -> None:
        """Stop the timer processing thread."""
        self.running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1.0)
    
    def _timer_loop(self) -> None:
        """Main timer processing loop."""
        while self.running:
            current_time = time.time()
            expired_timers = []
            
            with self.timer_lock:
                for timer_id, timer_data in self.timers.items():
                    if current_time >= timer_data["end_time"]:
                        expired_timers.append(timer_id)
            
            # Process expired timers
            for timer_id in expired_timers:
                self._trigger_timer(timer_id)
            
            time.sleep(0.1)  # Check every 100ms
    
    def _trigger_timer(self, timer_id: str) -> None:
        """Trigger an expired timer."""
        with self.timer_lock:
            if timer_id not in self.timers:
                return
            
            timer_data = self.timers[timer_id]
            
            # Send timer event
            event = {
                "type": "timer_expired",
                "timer_id": timer_id,
                "timer_name": timer_data["name"],
                "metadata": timer_data.get("metadata", {})
            }
            
            self.send_to_socket("timer_events", event)
            
            # Handle repeating timers
            if timer_data.get("repeat", False):
                timer_data["end_time"] = time.time() + timer_data["duration"]
            else:
                del self.timers[timer_id]
            
            self.log_activity(
                "self",
                f"Timer {timer_data['name']} expired",
                {"timer_id": timer_id}
            )
    
    def set_timer(self, name: str, duration: float, repeat: bool = False, **metadata) -> str:
        """Set a new timer."""
        timer_id = f"{name}_{time.time()}"
        
        timer_data = {
            "name": name,
            "duration": duration,
            "end_time": time.time() + duration,
            "repeat": repeat,
            "metadata": metadata
        }
        
        with self.timer_lock:
            self.timers[timer_id] = timer_data
        
        self.log_activity(
            "self",
            f"Set timer {name} for {duration} seconds",
            {"timer_id": timer_id, "duration": duration, "repeat": repeat}
        )
        
        return timer_id
    
    def cancel_timer(self, timer_id: str) -> bool:
        """Cancel a timer."""
        with self.timer_lock:
            if timer_id in self.timers:
                timer_name = self.timers[timer_id]["name"]
                del self.timers[timer_id]
                
                self.log_activity(
                    "self",
                    f"Cancelled timer {timer_name}",
                    {"timer_id": timer_id}
                )
                
                return True
        
        return False
    
    def get_timer_status(self, timer_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a timer."""
        with self.timer_lock:
            if timer_id not in self.timers:
                return None
            
            timer_data = self.timers[timer_id]
            current_time = time.time()
            
            return {
                "timer_id": timer_id,
                "name": timer_data["name"],
                "remaining": max(0, timer_data["end_time"] - current_time),
                "duration": timer_data["duration"],
                "repeat": timer_data["repeat"],
                "metadata": timer_data.get("metadata", {})
            }
    
    def list_timers(self) -> List[Dict[str, Any]]:
        """List all active timers."""
        with self.timer_lock:
            timers = []
            for timer_id in self.timers.keys():
                status = self.get_timer_status(timer_id)
                if status is not None:
                    timers.append(status)
            return timers


class LoggerFamiliar(EntityFamiliar):
    """
    Utility familiar for logging and debugging.
    
    Provides structured logging, log filtering,
    and log analysis capabilities.
    """
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        super().__init__(name)
        
        # Set up logging
        self.logger = logging.getLogger(f"grimoire.{name}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Logging sockets
        self.add_socket("log_input", direction="input")
        self.add_socket("log_output", direction="output")
        
        # Log storage for analysis
        self.log_entries: List[Dict[str, Any]] = []
        self.max_entries = 10000
        self.log_lock = threading.Lock()
    
    def log(self, level: str, message: str, **metadata) -> None:
        """Log a message with metadata."""
        level_upper = level.upper()
        
        # Log through Python logging
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{message} | {metadata}")
        
        # Store for analysis
        entry = {
            "timestamp": time.time(),
            "level": level_upper,
            "message": message,
            "metadata": metadata,
            "source": metadata.get("source", "unknown")
        }
        
        with self.log_lock:
            self.log_entries.append(entry)
            if len(self.log_entries) > self.max_entries:
                self.log_entries = self.log_entries[-self.max_entries//2:]
        
        # Send through socket
        self.send_to_socket("log_output", entry)
        
        # Log to familiar activity
        self.log_activity(
            "self",
            f"Logged {level}: {message}",
            {"log_level": level, "metadata": metadata}
        )
    
    def debug(self, message: str, **metadata) -> None:
        """Log debug message."""
        self.log("DEBUG", message, **metadata)
    
    def info(self, message: str, **metadata) -> None:
        """Log info message."""
        self.log("INFO", message, **metadata)
    
    def warning(self, message: str, **metadata) -> None:
        """Log warning message."""
        self.log("WARNING", message, **metadata)
    
    def error(self, message: str, **metadata) -> None:
        """Log error message."""
        self.log("ERROR", message, **metadata)
    
    def critical(self, message: str, **metadata) -> None:
        """Log critical message."""
        self.log("CRITICAL", message, **metadata)
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        with self.log_lock:
            logs = self.log_entries.copy()
        
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
        
        return logs[-limit:]
    
    def analyze_logs(self, time_window: float = 3600) -> Dict[str, Any]:
        """Analyze log patterns."""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        with self.log_lock:
            recent_logs = [
                log for log in self.log_entries
                if log["timestamp"] >= cutoff_time
            ]
        
        if not recent_logs:
            return {"error": "No logs in time window"}
        
        # Analyze patterns
        level_counts = {}
        source_counts = {}
        error_messages = []
        
        for log in recent_logs:
            level = log["level"]
            source = log.get("source", "unknown")
            
            level_counts[level] = level_counts.get(level, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            
            if level in ["ERROR", "CRITICAL"]:
                error_messages.append({
                    "timestamp": log["timestamp"],
                    "message": log["message"],
                    "source": source
                })
        
        return {
            "time_window": time_window,
            "total_logs": len(recent_logs),
            "level_distribution": level_counts,
            "source_distribution": source_counts,
            "error_count": len(error_messages),
            "recent_errors": error_messages[-10:],  # Last 10 errors
            "logs_per_minute": len(recent_logs) / (time_window / 60)
        }


class FileHandlerFamiliar(EntityFamiliar):
    """
    Utility familiar for file operations.
    
    Provides safe file reading, writing, JSON handling,
    and file system monitoring capabilities.
    """
    
    def __init__(self, name: str, base_directory: str = "."):
        super().__init__(name)
        
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(exist_ok=True)
        
        # File operation sockets
        self.add_socket("file_commands", direction="input")
        self.add_socket("file_events", direction="output")
        
        # File operation tracking
        self.file_operations: List[Dict[str, Any]] = []
        self.max_operations = 1000
        self.file_lock = threading.Lock()
    
    def _safe_path(self, filename: str) -> Path:
        """Ensure path is within base directory."""
        path = self.base_directory / filename
        
        # Resolve to prevent directory traversal
        try:
            path = path.resolve()
            if not str(path).startswith(str(self.base_directory.resolve())):
                raise ValueError(f"Path {filename} is outside base directory")
        except Exception as e:
            raise ValueError(f"Invalid path {filename}: {e}")
        
        return path
    
    def read_file(self, filename: str, encoding: str = "utf-8") -> str:
        """Read text file content."""
        path = self._safe_path(filename)
        
        try:
            content = path.read_text(encoding=encoding)
            
            self._log_operation("read", filename, {"size": len(content), "encoding": encoding})
            
            return content
            
        except Exception as e:
            self._log_operation("read", filename, {"error": str(e)})
            raise
    
    def write_file(self, filename: str, content: str, encoding: str = "utf-8") -> None:
        """Write text file content."""
        path = self._safe_path(filename)
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            path.write_text(content, encoding=encoding)
            
            self._log_operation("write", filename, {"size": len(content), "encoding": encoding})
            
        except Exception as e:
            self._log_operation("write", filename, {"error": str(e)})
            raise
    
    def read_json(self, filename: str) -> Any:
        """Read JSON file."""
        content = self.read_file(filename)
        
        try:
            data = json.loads(content)
            self._log_operation("read_json", filename, {"type": type(data).__name__})
            return data
            
        except Exception as e:
            self._log_operation("read_json", filename, {"error": str(e)})
            raise
    
    def write_json(self, filename: str, data: Any, indent: int = 2) -> None:
        """Write JSON file."""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            self.write_file(filename, content)
            
            self._log_operation("write_json", filename, {"type": type(data).__name__})
            
        except Exception as e:
            self._log_operation("write_json", filename, {"error": str(e)})
            raise
    
    def append_file(self, filename: str, content: str, encoding: str = "utf-8") -> None:
        """Append to text file."""
        path = self._safe_path(filename)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with path.open("a", encoding=encoding) as f:
                f.write(content)
            
            self._log_operation("append", filename, {"size": len(content), "encoding": encoding})
            
        except Exception as e:
            self._log_operation("append", filename, {"error": str(e)})
            raise
    
    def delete_file(self, filename: str) -> bool:
        """Delete a file."""
        path = self._safe_path(filename)
        
        try:
            if path.exists():
                path.unlink()
                self._log_operation("delete", filename, {"success": True})
                return True
            else:
                self._log_operation("delete", filename, {"error": "File not found"})
                return False
                
        except Exception as e:
            self._log_operation("delete", filename, {"error": str(e)})
            raise
    
    def list_files(self, pattern: str = "*") -> List[str]:
        """List files matching pattern."""
        try:
            files = [
                str(path.relative_to(self.base_directory))
                for path in self.base_directory.glob(pattern)
                if path.is_file()
            ]
            
            self._log_operation("list", pattern, {"count": len(files)})
            
            return files
            
        except Exception as e:
            self._log_operation("list", pattern, {"error": str(e)})
            raise
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists."""
        try:
            path = self._safe_path(filename)
            exists = path.exists()
            
            self._log_operation("exists", filename, {"exists": exists})
            
            return exists
            
        except Exception as e:
            self._log_operation("exists", filename, {"error": str(e)})
            return False
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get file information."""
        path = self._safe_path(filename)
        
        try:
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            
            info = {
                "exists": True,
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_file": path.is_file(),
                "is_directory": path.is_dir()
            }
            
            self._log_operation("info", filename, {"size": info["size"]})
            
            return info
            
        except Exception as e:
            self._log_operation("info", filename, {"error": str(e)})
            raise
    
    def _log_operation(self, operation: str, filename: str, metadata: Dict[str, Any]) -> None:
        """Log file operation."""
        entry = {
            "timestamp": time.time(),
            "operation": operation,
            "filename": filename,
            "metadata": metadata
        }
        
        with self.file_lock:
            self.file_operations.append(entry)
            if len(self.file_operations) > self.max_operations:
                self.file_operations = self.file_operations[-self.max_operations//2:]
        
        # Send event
        self.send_to_socket("file_events", entry)
        
        # Log activity
        self.log_activity(
            "self",
            f"File {operation}: {filename}",
            metadata
        )
    
    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent file operations."""
        with self.file_lock:
            return self.file_operations[-limit:]
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get file operation statistics."""
        with self.file_lock:
            operations = self.file_operations.copy()
        
        if not operations:
            return {"total_operations": 0}
        
        operation_counts = {}
        total_size = 0
        error_count = 0
        
        for op in operations:
            op_type = op["operation"]
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
            
            if "error" in op["metadata"]:
                error_count += 1
            
            if "size" in op["metadata"]:
                total_size += op["metadata"]["size"]
        
        return {
            "total_operations": len(operations),
            "operation_counts": operation_counts,
            "total_bytes_processed": total_size,
            "error_count": error_count,
            "error_rate": error_count / len(operations) if operations else 0.0
        }