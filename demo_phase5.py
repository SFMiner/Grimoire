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
Grimoire Phase 5 Demo: Developer Experience & Standard Library

This demo showcases the Phase 5 implementation featuring:
- Debugging and profiling tools for familiars
- Standard library familiars (Player, NPC, Monster, Timer, Logger, FileHandler)
- Performance monitoring and analysis
- Comprehensive developer tooling
"""

import time
import threading
from typing import Dict, Any

# Import Grimoire components
from grimoire.interpreter import GrimoireInterpreter
from grimoire.world_state import get_world_state
from grimoire.standard_library import (
    PlayerFamiliar, NPCFamiliar, MonsterFamiliar, 
    TimerFamiliar, LoggerFamiliar, FileHandlerFamiliar
)

# Import profiling tools
try:
    from grimoire.profiler import get_profiler, get_ai_profiler, start_system_monitoring, stop_system_monitoring
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    print("Profiling tools not available")


def demo_standard_library():
    """Demonstrate standard library familiars."""
    print("\n" + "="*50)
    print("STANDARD LIBRARY FAMILIARS DEMO")
    print("="*50)
    
    # Create Player Familiar
    print("\n[DEMO] Creating Player Familiar...")
    player_data = {
        "class": "warrior",
        "background": "soldier"
    }
    player = PlayerFamiliar("hero", player_data)
    
    # Test player functionality
    print(f"Player created: {player.name}")
    print(f"Initial level: {player.get_property('level')}")
    print(f"Initial health: {player.get_property('health')}")
    
    # Add items and test inventory
    player.add_item("sword", 1)
    player.add_item("potion", 3)
    print(f"Inventory: {player.get_property('inventory')}")
    
    # Test experience and leveling
    leveled_up = player.gain_experience(150)
    print(f"Gained experience, leveled up: {leveled_up}")
    print(f"New level: {player.get_property('level')}")
    
    # Create NPC Familiar
    print("\n[DEMO] Creating NPC Familiar...")
    npc_data = {
        "personality": "friendly",
        "faction": "town_guard",
        "dialogue": {
            "greeting": {
                "text": "Welcome to our town, traveler!",
                "options": ["Thank you", "Where is the inn?", "Goodbye"]
            }
        },
        "quests": [
            {
                "id": "rat_problem",
                "title": "Rat Infestation",
                "description": "Clear the rats from the cellar",
                "rewards": ["50 gold", "town favor"]
            }
        ]
    }
    npc = NPCFamiliar("town_guard", npc_data)
    
    # Test NPC dialogue
    dialogue = npc.start_dialogue("hero", "greeting")
    print(f"NPC dialogue: {dialogue['text']}")
    print(f"Options: {dialogue['options']}")
    
    # Test quest offering
    quest = npc.offer_quest("hero", "rat_problem")
    if quest:
        print(f"Quest offered: {quest['title']}")
    else:
        print("No quest available")
    
    # Create Monster Familiar
    print("\n[DEMO] Creating Monster Familiar...")
    monster_data = {
        "aggression": 0.8,
        "territory": {"x": 100, "y": 100},
        "territory_radius": 20,
        "combat_stats": {
            "attack": 15,
            "defense": 8,
            "health": 75,
            "speed": 6
        }
    }
    monster = MonsterFamiliar("orc_warrior", monster_data)
    
    # Test monster threat detection
    threat_data = {
        "level": 0.7,
        "position": {"x": 105, "y": 105},
        "in_range": True
    }
    monster.detect_threat(threat_data)
    print(f"Monster detected threat: {threat_data['level']}")
    
    # Create Timer Familiar
    print("\n[DEMO] Creating Timer Familiar...")
    timer = TimerFamiliar("game_timer")
    
    # Set some timers
    timer_id1 = timer.set_timer("combat_round", 5.0, False, combat_phase="attack")
    timer_id2 = timer.set_timer("health_regen", 2.0, True, amount=5)
    
    print(f"Set timers: {timer_id1}, {timer_id2}")
    print(f"Active timers: {len(timer.list_timers())}")
    
    # Create Logger Familiar
    print("\n[DEMO] Creating Logger Familiar...")
    logger = LoggerFamiliar("game_logger", "DEBUG", "game.log")
    
    # Test logging
    logger.info("Game started", player=player.name, level=player.get_property('level'))
    logger.warning("Player health low", health=player.get_property('health'))
    logger.debug("NPC interaction", npc=npc.name, player=player.name)
    
    # Analyze logs
    log_analysis = logger.analyze_logs(60)  # Last minute
    print(f"Log analysis: {log_analysis['total_logs']} logs in last minute")
    
    # Create File Handler Familiar
    print("\n[DEMO] Creating File Handler Familiar...")
    file_handler = FileHandlerFamiliar("game_files", "./game_data")
    
    # Test file operations
    save_data = {
        "player": {
            "name": player.name,
            "level": player.get_property('level'),
            "inventory": player.get_property('inventory')
        },
        "world": {
            "time": time.time(),
            "location": "town_square"
        }
    }
    
    file_handler.write_json("save_game.json", save_data)
    print("Game saved to save_game.json")
    
    # Read it back
    loaded_data = file_handler.read_json("save_game.json")
    print(f"Loaded player level: {loaded_data['player']['level']}")
    
    return {
        "player": player,
        "npc": npc,
        "monster": monster,
        "timer": timer,
        "logger": logger,
        "file_handler": file_handler
    }


def demo_debugging_tools(familiars: Dict[str, Any]):
    """Demonstrate debugging and profiling tools."""
    print("\n" + "="*50)
    print("DEBUGGING & PROFILING TOOLS DEMO")
    print("="*50)
    
    # Create interpreter to test built-ins
    interpreter = GrimoireInterpreter()
    
    # Add familiars to interpreter
    for name, familiar in familiars.items():
        interpreter.familiars[name] = familiar
    
    # Test debug_familiar built-in
    print("\n[DEMO] Testing debug_familiar built-in...")
    try:
        debug_info = interpreter.globals.get("debug_familiar")(interpreter, ["player"])
        print(f"Player debug info:")
        print(f"  - Name: {debug_info['name']}")
        print(f"  - Type: {debug_info['familiar_type']}")
        print(f"  - State: {debug_info['state']}")
        print(f"  - Sockets: {len(debug_info['sockets'])}")
        if 'properties' in debug_info:
            print(f"  - Properties: {len(debug_info['properties'])}")
    except Exception as e:
        print(f"Debug familiar error: {e}")
    
    # Test AI profiling
    print("\n[DEMO] Testing AI profiling...")
    try:
        ai_insights = interpreter.globals.get("profile_ai")(interpreter, ["npc"])
        print(f"NPC AI insights:")
        if "error" not in ai_insights:
            print(f"  - Efficiency: {ai_insights.get('efficiency', {})}")
            print(f"  - Effectiveness: {ai_insights.get('effectiveness', {})}")
            print(f"  - Recommendations: {ai_insights.get('recommendations', [])}")
        else:
            print(f"  - {ai_insights['error']}")
    except Exception as e:
        print(f"AI profiling error: {e}")
    
    # Test performance monitoring
    if PROFILING_AVAILABLE:
        print("\n[DEMO] Testing performance monitoring...")
        
        # Start system monitoring
        start_system_monitoring(0.5)  # Every 0.5 seconds
        
        # Simulate some work
        print("Simulating game activities...")
        for i in range(5):
            # Simulate AI updates
            familiars["npc"].autonomous_update()
            familiars["monster"].autonomous_update()
            
            # Simulate player actions
            familiars["player"].add_item(f"item_{i}", 1)
            
            # Simulate timer events
            time.sleep(0.2)
        
        # Get performance report
        profiler = get_profiler()
        report = profiler.get_report(limit=20)
        
        print(f"Performance report:")
        print(f"  - Total samples: {report['overall_stats']['total_samples']}")
        print(f"  - Average duration: {report['overall_stats']['average_duration']:.4f}s")
        print(f"  - Categories: {list(report['category_stats'].keys())}")
        
        # Get AI-specific insights
        ai_profiler = get_ai_profiler()
        ai_report = ai_profiler.get_ai_report()
        
        if ai_report:
            print(f"AI profiling report:")
            for ai_name, stats in ai_report.items():
                print(f"  - {ai_name}: {stats['decision_count']} decisions")
        
        # Stop monitoring
        stop_system_monitoring()
    
    # Test timer functionality
    print("\n[DEMO] Testing timer events...")
    timer = familiars["timer"]
    
    # Wait for some timer events
    print("Waiting for timer events...")
    time.sleep(3.0)
    
    # Check timer status
    active_timers = timer.list_timers()
    print(f"Active timers: {len(active_timers)}")
    for timer_info in active_timers:
        print(f"  - {timer_info['name']}: {timer_info['remaining']:.1f}s remaining")


def demo_socket_communication(familiars: Dict[str, Any]):
    """Demonstrate socket communication between familiars."""
    print("\n" + "="*50)
    print("SOCKET COMMUNICATION DEMO")
    print("="*50)
    
    player = familiars["player"]
    npc = familiars["npc"]
    logger = familiars["logger"]
    
    # Set up socket connections
    print("\n[DEMO] Setting up socket connections...")
    
    # Connect player status output to logger input
    try:
        # This would require actual socket implementation
        print("Socket connections would be established here")
        print("- Player status -> Logger input")
        print("- NPC dialogue -> Logger input")
        print("- Monster combat -> Logger input")
    except Exception as e:
        print(f"Socket connection error: {e}")
    
    # Simulate some activities that would generate socket messages
    print("\n[DEMO] Simulating socket communications...")
    
    # Player gains experience (would send status update)
    player.gain_experience(50)
    logger.info("Player gained experience", amount=50)
    
    # NPC starts dialogue (would send dialogue message)
    dialogue = npc.start_dialogue("hero")
    logger.info("NPC dialogue started", npc=npc.name, player="hero")
    
    # Monster detects threat (would send threat message)
    monster = familiars["monster"]
    threat = {"level": 0.9, "position": {"x": 95, "y": 95}, "in_range": True}
    monster.detect_threat(threat)
    logger.warning("Monster threat detected", monster=monster.name, threat_level=threat["level"])


def demo_world_state_integration(familiars: Dict[str, Any]):
    """Demonstrate world state integration."""
    print("\n" + "="*50)
    print("WORLD STATE INTEGRATION DEMO")
    print("="*50)
    
    world_state = get_world_state()
    
    # Set up world state
    print("\n[DEMO] Setting up world state...")
    world_state.set("game_time", 0)
    world_state.set("weather", "sunny")
    world_state.set("location", "town_square")
    world_state.set("player_count", 1)
    
    # Subscribe to world state changes
    def on_time_change(key, old_value, new_value):
        print(f"[WORLD] Time changed: {old_value} -> {new_value}")
    
    def on_weather_change(key, old_value, new_value):
        print(f"[WORLD] Weather changed: {old_value} -> {new_value}")
    
    world_state.subscribe("game_time", on_time_change)
    world_state.subscribe("weather", on_weather_change)
    
    # Simulate world changes
    print("\n[DEMO] Simulating world state changes...")
    for i in range(3):
        world_state.set("game_time", i * 100)
        time.sleep(0.5)
    
    world_state.set("weather", "rainy")
    time.sleep(0.5)
    world_state.set("weather", "stormy")
    
    # Show final world state
    final_state = world_state.to_dict()
    print(f"\n[DEMO] Final world state: {final_state}")


def main():
    """Run the Phase 5 demo."""
    print("=" * 70)
    print("GRIMOIRE PHASE 5 DEMO: DEVELOPER EXPERIENCE & STANDARD LIBRARY")
    print("=" * 70)
    
    try:
        # Demo standard library familiars
        familiars = demo_standard_library()
        
        # Demo debugging and profiling tools
        demo_debugging_tools(familiars)
        
        # Demo socket communication
        demo_socket_communication(familiars)
        
        # Demo world state integration
        demo_world_state_integration(familiars)
        
        print("\n" + "="*70)
        print("PHASE 5 DEMO COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        # Show summary
        print(f"\nDemo Summary:")
        print(f"- Standard Library Familiars: {len(familiars)} created")
        print(f"- Player Level: {familiars['player'].get_property('level')}")
        print(f"- Active Timers: {len(familiars['timer'].list_timers())}")
        print(f"- Log Entries: {len(familiars['logger'].get_logs())}")
        print(f"- File Operations: {len(familiars['file_handler'].get_operation_history())}")
        
        if PROFILING_AVAILABLE:
            profiler = get_profiler()
            stats = profiler.get_report()
            print(f"- Performance Samples: {stats['overall_stats']['total_samples']}")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if PROFILING_AVAILABLE:
            try:
                stop_system_monitoring()
            except:
                pass
        
        # Stop timer threads
        try:
            if 'familiars' in locals() and 'timer' in familiars:
                familiars['timer'].stop_timer_thread()
        except:
            pass


if __name__ == "__main__":
    main()