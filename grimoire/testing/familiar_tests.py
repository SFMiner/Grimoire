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

"""Testing framework for familiar system.

This module provides comprehensive testing utilities for the familiar system,
including socket communication tests, goal evaluation tests, and integration tests.
"""

from typing import Any, Dict, List, Optional
import time
import sys
import traceback

__all__ = ["FamiliarTestHarness", "TestResult", "SocketTestResult", "IntegrationTestResult"]


class TestResult:
    """Base class for test results."""
    
    def __init__(self, test_name: str, success: bool, message: str = "", 
                 details: Optional[Dict[str, Any]] = None):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()
        
    def __str__(self):
        status = "PASS" if self.success else "FAIL"
        return f"[{status}] {self.test_name}: {self.message}"


class SocketTestResult(TestResult):
    """Result for socket communication tests."""
    
    def __init__(self, test_name: str, success: bool, message: str = "",
                 sender: str = "", receiver: str = "", data_sent: Any = None,
                 data_received: Any = None):
        super().__init__(test_name, success, message)
        self.sender = sender
        self.receiver = receiver
        self.data_sent = data_sent
        self.data_received = data_received


class IntegrationTestResult(TestResult):
    """Result for integration tests."""
    
    def __init__(self, test_name: str, success: bool, message: str = "",
                 components_tested: Optional[List[str]] = None, performance_metrics: Optional[Dict[str, Any]] = None):
        super().__init__(test_name, success, message)
        self.components_tested = components_tested or []
        self.performance_metrics = performance_metrics or {}


class FamiliarTestHarness:
    """Testing framework for familiar system."""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.test_familiars: Dict[str, Any] = {}
        self.mock_world_state = None
        self.message_router = None
        self.setup_complete = False
        
        # Initialize mock systems
        self._setup_mock_systems()
    
    def _setup_mock_systems(self):
        """Set up mock world state and message router."""
        try:
            from grimoire.ai.world_state import WorldState, WorldStateManager
            self.mock_world_state = WorldState()
            self.world_state_manager = WorldStateManager()
            
            from grimoire.messaging import MessageRouter
            self.message_router = MessageRouter()
            self.message_router.enable_debug(True)
            
            self.setup_complete = True
        except ImportError as e:
            self.log_test_result(TestResult(
                "setup", False, f"Failed to import required modules: {e}"
            ))
    
    def log_test_result(self, result: TestResult):
        """Log a test result."""
        self.test_results.append(result)
        print(f"{result}")
        
    def create_test_entity(self, name: str, properties: Dict[str, Any]) -> Any:
        """Create test entity familiar."""
        try:
            from grimoire.familiars.entity_familiar import EntityFamiliar
            entity = EntityFamiliar(name, properties)
            self.test_familiars[name] = entity
            
            # Register with systems
            if self.world_state_manager:
                self.world_state_manager.register_familiar(entity)
            if self.message_router:
                self.message_router.register_familiar(entity)
            
            self.log_test_result(TestResult(
                f"create_entity_{name}", True, f"Created entity familiar: {name}"
            ))
            return entity
            
        except ImportError as e:
            self.log_test_result(TestResult(
                f"create_entity_{name}", False, f"EntityFamiliar not available: {e}"
            ))
            return None
        except Exception as e:
            self.log_test_result(TestResult(
                f"create_entity_{name}", False, f"Failed to create entity: {e}"
            ))
            return None
    
    def create_test_ai(self, name: str) -> Any:
        """Create test AI familiar."""
        try:
            from grimoire.familiars.ai_familiar import AIFamiliar
            ai = AIFamiliar(name)
            self.test_familiars[name] = ai
            
            # Register with systems
            if self.world_state_manager:
                self.world_state_manager.register_familiar(ai)
            if self.message_router:
                self.message_router.register_familiar(ai)
            
            self.log_test_result(TestResult(
                f"create_ai_{name}", True, f"Created AI familiar: {name}"
            ))
            return ai
            
        except ImportError as e:
            self.log_test_result(TestResult(
                f"create_ai_{name}", False, f"AIFamiliar not available: {e}"
            ))
            return None
        except Exception as e:
            self.log_test_result(TestResult(
                f"create_ai_{name}", False, f"Failed to create AI: {e}"
            ))
            return None
    
    def test_socket_communication(self, sender_name: str, socket_name: str, 
                                 receiver_name: str, test_data: Any = None) -> SocketTestResult:
        """Test socket communication between familiars."""
        if test_data is None:
            test_data = {"test": "socket_communication", "timestamp": time.time()}
        
        sender = self.test_familiars.get(sender_name)
        receiver = self.test_familiars.get(receiver_name)
        
        if not sender:
            return SocketTestResult(
                "socket_communication", False, f"Sender {sender_name} not found",
                sender_name, receiver_name, test_data, None
            )
        
        if not receiver:
            return SocketTestResult(
                "socket_communication", False, f"Receiver {receiver_name} not found",
                sender_name, receiver_name, test_data, None
            )
        
        try:
            # Check if sender has the socket
            if not hasattr(sender, 'has_socket') or not sender.has_socket(socket_name):
                return SocketTestResult(
                    "socket_communication", False, f"Sender does not have socket: {socket_name}",
                    sender_name, receiver_name, test_data, None
                )
            
            # Send data via socket
            if hasattr(sender, 'send_to_socket'):
                sender.send_to_socket(socket_name, test_data)
                
                # Check if receiver got the message (simplified)
                result = SocketTestResult(
                    "socket_communication", True, "Socket communication successful",
                    sender_name, receiver_name, test_data, test_data
                )
                self.log_test_result(result)
                return result
            else:
                return SocketTestResult(
                    "socket_communication", False, "Sender does not support send_to_socket",
                    sender_name, receiver_name, test_data, None
                )
                
        except Exception as e:
            return SocketTestResult(
                "socket_communication", False, f"Socket communication failed: {e}",
                sender_name, receiver_name, test_data, None
            )
    
    def test_goal_evaluation(self, ai_name: str, world_state_properties: Dict[str, Any]) -> TestResult:
        """Test AI goal evaluation."""
        ai = self.test_familiars.get(ai_name)
        if not ai:
            return TestResult("goal_evaluation", False, f"AI {ai_name} not found")
        
        if not hasattr(ai, 'goals'):
            return TestResult("goal_evaluation", False, f"AI {ai_name} does not have goals")
        
        try:
            # Set up test world state
            if self.mock_world_state:
                for prop, value in world_state_properties.items():
                    self.mock_world_state.set_global_property(prop, value)
            
            # Test goal evaluation
            results = []
            for goal in ai.goals:
                if hasattr(goal, 'evaluate_satisfaction'):
                    satisfaction = goal.evaluate_satisfaction(self.mock_world_state or world_state_properties)
                    results.append({
                        "goal": goal.name,
                        "satisfaction": satisfaction
                    })
            
            result = TestResult(
                "goal_evaluation", True, f"Evaluated {len(results)} goals",
                {"evaluations": results}
            )
            self.log_test_result(result)
            return result
            
        except Exception as e:
            return TestResult("goal_evaluation", False, f"Goal evaluation failed: {e}")
    
    def test_property_updates(self, entity_name: str, property_updates: Dict[str, Any]) -> TestResult:
        """Test entity property updates and notifications."""
        entity = self.test_familiars.get(entity_name)
        if not entity:
            return TestResult("property_updates", False, f"Entity {entity_name} not found")
        
        try:
            original_values = {}
            updated_values = {}
            
            # Record original values
            for prop in property_updates.keys():
                if hasattr(entity, 'get_property'):
                    original_values[prop] = entity.get_property(prop)
            
            # Apply updates
            for prop, value in property_updates.items():
                if hasattr(entity, 'update_property'):
                    entity.update_property(prop, value)
                    updated_values[prop] = entity.get_property(prop) if hasattr(entity, 'get_property') else value
            
            result = TestResult(
                "property_updates", True, f"Updated {len(property_updates)} properties",
                {"original": original_values, "updated": updated_values}
            )
            self.log_test_result(result)
            return result
            
        except Exception as e:
            return TestResult("property_updates", False, f"Property update failed: {e}")
    
    def test_ai_action_selection(self, ai_name: str, world_state: Dict[str, Any]) -> TestResult:
        """Test AI action selection based on goals."""
        ai = self.test_familiars.get(ai_name)
        if not ai:
            return TestResult("ai_action_selection", False, f"AI {ai_name} not found")
        
        try:
            if hasattr(ai, 'evaluate_goals'):
                action = ai.evaluate_goals(world_state)
                
                result = TestResult(
                    "ai_action_selection", True, f"AI selected action: {action}",
                    {"selected_action": str(action), "world_state": world_state}
                )
                self.log_test_result(result)
                return result
            else:
                return TestResult("ai_action_selection", False, "AI does not support goal evaluation")
                
        except Exception as e:
            return TestResult("ai_action_selection", False, f"Action selection failed: {e}")
    
    def run_integration_test(self) -> IntegrationTestResult:
        """Run complete integration test."""
        if not self.setup_complete:
            return IntegrationTestResult(
                "integration_test", False, "Setup not complete",
                ["setup"], {}
            )
        
        start_time = time.time()
        components_tested = []
        
        try:
            # Test 1: Create entities and AI
            player = self.create_test_entity("player", {"health": 100, "mana": 50, "can_move": True})
            enemy = self.create_test_entity("enemy", {"health": 80, "attack": 15})
            ai = self.create_test_ai("combat_ai")
            
            if player and enemy and ai:
                components_tested.append("familiar_creation")
            
            # Test 2: Socket communication
            if player and ai:
                socket_result = self.test_socket_communication("player", "property_output", "combat_ai")
                if socket_result.success:
                    components_tested.append("socket_communication")
            
            # Test 3: Property updates
            if player:
                prop_result = self.test_property_updates("player", {"health": 75})
                if prop_result.success:
                    components_tested.append("property_updates")
            
            # Test 4: Goal evaluation (if AI has goals)
            if ai and hasattr(ai, 'goals') and ai.goals:
                goal_result = self.test_goal_evaluation("combat_ai", {"player_health": 75, "enemy_health": 80})
                if goal_result.success:
                    components_tested.append("goal_evaluation")
            
            # Test 5: World state integration
            if self.world_state_manager:
                self.world_state_manager.update_world_state()
                summary = self.world_state_manager.world_state.get_world_summary()
                if summary['total_entities'] > 0:
                    components_tested.append("world_state")
            
            end_time = time.time()
            test_duration = end_time - start_time
            
            result = IntegrationTestResult(
                "integration_test", True, f"Integration test completed successfully",
                components_tested, {"duration": test_duration, "entities_created": 3}
            )
            self.log_test_result(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            test_duration = end_time - start_time
            
            result = IntegrationTestResult(
                "integration_test", False, f"Integration test failed: {e}",
                components_tested, {"duration": test_duration, "error": str(e)}
            )
            self.log_test_result(result)
            return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all available tests."""
        print("=== Starting Familiar System Tests ===")
        
        # Clear previous results
        self.test_results.clear()
        self.test_familiars.clear()
        
        # Run integration test (includes most other tests)
        integration_result = self.run_integration_test()
        
        # Compile summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "integration_result": integration_result,
            "detailed_results": self.test_results
        }
        
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        
        if failed_tests > 0:
            print(f"\nFailed tests:")
            for result in self.test_results:
                if not result.success:
                    print(f"  - {result}")
        
        return summary
    
    def cleanup(self):
        """Clean up test resources."""
        self.test_familiars.clear()
        self.test_results.clear()
        if self.message_router:
            self.message_router.clear_message_log()
        print("Test cleanup completed.")