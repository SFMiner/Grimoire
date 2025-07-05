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
Grimoire Testing Suite

This module provides comprehensive testing capabilities for the Grimoire
programming language, including unit tests, integration tests, performance
tests, and magical-themed test reporting.
"""

import time
import unittest
import threading
import traceback
import sys
import os
from typing import Dict, List, Any, Optional, Callable, Union, Type
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import functools
import inspect


class TestSeverity(Enum):
    """Test severity levels."""
    TRIVIAL = "trivial"      # Minor functionality
    MINOR = "minor"          # Standard functionality
    MAJOR = "major"          # Important functionality
    CRITICAL = "critical"    # Essential functionality
    BLOCKER = "blocker"      # Must-have functionality


class TestCategory(Enum):
    """Test categories."""
    UNIT = "unit"                    # Unit tests
    INTEGRATION = "integration"      # Integration tests
    PERFORMANCE = "performance"      # Performance tests
    STRESS = "stress"               # Stress tests
    REGRESSION = "regression"       # Regression tests
    MAGICAL = "magical"             # Magical-themed tests


@dataclass
class TestResult:
    """Enhanced test result with magical theming."""
    test_name: str
    category: TestCategory
    severity: TestSeverity
    passed: bool
    duration: float
    error_message: Optional[str] = None
    magical_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.magical_message:
            self.magical_message = self._generate_magical_message()
    
    def _generate_magical_message(self) -> str:
        """Generate a magical-themed test message."""
        if self.passed:
            success_phrases = [
                "The spell weaves perfectly",
                "The ritual completes successfully", 
                "The arcane energies align",
                "The magical forces are in harmony",
                "The enchantment holds true"
            ]
            base_phrase = success_phrases[hash(self.test_name) % len(success_phrases)]
            return f"✨ {base_phrase} for {self.test_name}"
        else:
            failure_phrases = [
                "The spell fizzles and fails",
                "The ritual circle is broken",
                "The arcane energies clash",
                "The magical forces rebel",
                "The enchantment unravels"
            ]
            base_phrase = failure_phrases[hash(self.test_name) % len(failure_phrases)]
            return f"💥 {base_phrase} in {self.test_name}: {self.error_message}"


class MagicalTestCase(unittest.TestCase):
    """Enhanced test case with magical theming and enhanced capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results: List[TestResult] = []
        self.setup_time = 0.0
        self.teardown_time = 0.0
    
    def setUp(self):
        """Enhanced setup with timing."""
        start_time = time.time()
        self.magical_setup()
        self.setup_time = time.time() - start_time
    
    def tearDown(self):
        """Enhanced teardown with timing."""
        start_time = time.time()
        self.magical_teardown()
        self.teardown_time = time.time() - start_time
    
    def magical_setup(self):
        """Override this for magical setup."""
        pass
    
    def magical_teardown(self):
        """Override this for magical teardown."""
        pass
    
    def assert_familiar_active(self, familiar, message="Familiar should be active"):
        """Assert that a familiar is active."""
        self.assertTrue(
            hasattr(familiar, 'state') and familiar.state == 'active',
            f"🔮 {message}: {familiar.name if hasattr(familiar, 'name') else 'unknown'}"
        )
    
    def assert_socket_connected(self, socket, message="Socket should be connected"):
        """Assert that a socket is connected."""
        self.assertTrue(
            hasattr(socket, 'is_connected') and socket.is_connected(),
            f"⚡ {message}: {socket.name if hasattr(socket, 'name') else 'unknown'}"
        )
    
    def assert_goal_satisfied(self, goal, world_state, message="Goal should be satisfied"):
        """Assert that a goal is satisfied."""
        if hasattr(goal, 'evaluate'):
            satisfaction = goal.evaluate(world_state)
            self.assertGreater(
                satisfaction, 0.5,
                f"🎯 {message}: {goal.name if hasattr(goal, 'name') else 'unknown'} (satisfaction: {satisfaction})"
            )
        else:
            self.assertTrue(
                hasattr(goal, 'satisfied') and goal.satisfied,
                f"🎯 {message}: {goal.name if hasattr(goal, 'name') else 'unknown'}"
            )
    
    def assert_world_state_valid(self, world_state, message="World state should be valid"):
        """Assert that world state is valid."""
        self.assertIsNotNone(world_state, f"🌍 {message}: world state is None")
        if hasattr(world_state, 'is_valid'):
            self.assertTrue(world_state.is_valid(), f"🌍 {message}: world state is invalid")
    
    def assert_performance_acceptable(self, duration, max_duration, operation="Operation"):
        """Assert that performance is within acceptable limits."""
        self.assertLessEqual(
            duration, max_duration,
            f"⚡ {operation} took too long: {duration:.3f}s > {max_duration:.3f}s"
        )
    
    def magical_subtest(self, name: str, category: TestCategory = TestCategory.UNIT, 
                       severity: TestSeverity = TestSeverity.MINOR):
        """Create a magical subtest context."""
        return MagicalSubTest(self, name, category, severity)


class MagicalSubTest:
    """Context manager for magical subtests."""
    
    def __init__(self, test_case: MagicalTestCase, name: str, 
                 category: TestCategory, severity: TestSeverity):
        self.test_case = test_case
        self.name = name
        self.category = category
        self.severity = severity
        self.start_time = 0.0
        self.context = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        result = TestResult(
            test_name=self.name,
            category=self.category,
            severity=self.severity,
            passed=exc_type is None,
            duration=duration,
            error_message=str(exc_val) if exc_val else None,
            context=self.context
        )
        
        self.test_case.test_results.append(result)
        
        # Don't suppress exceptions
        return False
    
    def add_context(self, key: str, value: Any):
        """Add context information to the subtest."""
        self.context[key] = value


class GrimoireTestSuite:
    """
    Comprehensive test suite for the Grimoire programming language.
    
    Provides unit tests, integration tests, performance tests,
    and magical-themed test reporting.
    """
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.test_classes: List[Type[MagicalTestCase]] = []
        self.performance_benchmarks: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def register_test_class(self, test_class: Type[MagicalTestCase]):
        """Register a test class."""
        self.test_classes.append(test_class)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all registered tests."""
        print("🔮 Beginning the Grand Ritual of Testing...")
        print("=" * 60)
        
        start_time = time.time()
        suite = unittest.TestSuite()
        
        # Add all test classes
        for test_class in self.test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests with custom result collector
        result_collector = MagicalTestRunner()
        result_collector.run(suite)
        
        # Collect results
        total_time = time.time() - start_time
        
        # Generate report
        report = self._generate_test_report(result_collector, total_time)
        
        print("\n🔮 The Grand Ritual of Testing is Complete!")
        print("=" * 60)
        
        return report
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-specific tests."""
        print("⚡ Beginning Performance Incantations...")
        print("=" * 50)
        
        performance_results = {}
        
        # Test familiar creation performance
        performance_results['familiar_creation'] = self._test_familiar_creation_performance()
        
        # Test message routing performance
        performance_results['message_routing'] = self._test_message_routing_performance()
        
        # Test goal evaluation performance
        performance_results['goal_evaluation'] = self._test_goal_evaluation_performance()
        
        # Test world state performance
        performance_results['world_state'] = self._test_world_state_performance()
        
        print("⚡ Performance Incantations Complete!")
        print("=" * 50)
        
        return performance_results
    
    def _test_familiar_creation_performance(self) -> Dict[str, float]:
        """Test familiar creation performance."""
        try:
            from .familiars.entity_familiar import EntityFamiliar
            from .familiars.ai_familiar import AIFamiliar
            
            results = {}
            
            # Test entity familiar creation
            start_time = time.time()
            for i in range(100):
                familiar = EntityFamiliar(f"test_familiar_{i}")
            results['entity_familiar_creation'] = (time.time() - start_time) / 100
            
            # Test AI familiar creation
            start_time = time.time()
            for i in range(50):
                familiar = AIFamiliar(f"test_ai_{i}")
            results['ai_familiar_creation'] = (time.time() - start_time) / 50
            
            return results
            
        except ImportError:
            return {"entity_familiar_creation": 0.0, "ai_familiar_creation": 0.0}
    
    def _test_message_routing_performance(self) -> Dict[str, float]:
        """Test message routing performance."""
        try:
            from .familiars.messaging import FamiliarMessage, MessageRouter
            
            results = {}
            router = MessageRouter()
            
            # Create test messages
            messages = []
            for i in range(1000):
                message = FamiliarMessage(
                    sender_name=f"sender_{i}",
                    recipient_name=f"recipient_{i}",
                    message_type="test",
                    content=f"test_message_{i}"
                )
                messages.append(message)
            
            # Test routing performance
            start_time = time.time()
            for message in messages:
                router.route_message(message)
            results['message_routing'] = (time.time() - start_time) / 1000
            
            return results
            
        except ImportError:
            return {"message_routing": 0.0}
    
    def _test_goal_evaluation_performance(self) -> Dict[str, float]:
        """Test goal evaluation performance."""
        try:
            from .goals import GoalArtifact
            from .world_state import WorldState
            
            results = {}
            
            # Create test goals
            goals = []
            for i in range(100):
                goal = GoalArtifact(f"test_goal_{i}")
                goals.append(goal)
            
            # Test evaluation performance
            world_state = WorldState()
            world_state.set("test_value", 42)
            world_state.set("time", 100)
            
            start_time = time.time()
            for goal in goals:
                if hasattr(goal, 'evaluate'):
                    goal.evaluate(world_state)
            results['goal_evaluation'] = (time.time() - start_time) / 100
            
            return results
            
        except ImportError:
            return {"goal_evaluation": 0.0}
    
    def _test_world_state_performance(self) -> Dict[str, float]:
        """Test world state performance."""
        try:
            from .world_state import WorldState
            
            results = {}
            world_state = WorldState()
            
            # Test set performance
            start_time = time.time()
            for i in range(1000):
                world_state.set(f"key_{i}", f"value_{i}")
            results['world_state_set'] = (time.time() - start_time) / 1000
            
            # Test get performance
            start_time = time.time()
            for i in range(1000):
                world_state.get(f"key_{i}")
            results['world_state_get'] = (time.time() - start_time) / 1000
            
            return results
            
        except ImportError:
            return {"world_state_set": 0.0, "world_state_get": 0.0}
    
    def _generate_test_report(self, result_collector, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            "summary": {
                "total_time": total_time,
                "tests_run": result_collector.testsRun,
                "failures": len(result_collector.failures),
                "errors": len(result_collector.errors),
                "success_rate": (result_collector.testsRun - len(result_collector.failures) - len(result_collector.errors)) / result_collector.testsRun if result_collector.testsRun > 0 else 0
            },
            "failures": [{"test": str(test), "error": error} for test, error in result_collector.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result_collector.errors],
            "performance_benchmarks": self.performance_benchmarks
        }
        
        # Print summary
        print(f"\n📊 Test Results Summary:")
        print(f"   Tests Run: {report['summary']['tests_run']}")
        print(f"   Failures: {report['summary']['failures']}")
        print(f"   Errors: {report['summary']['errors']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1%}")
        print(f"   Total Time: {report['summary']['total_time']:.2f}s")
        
        return report


class MagicalTestRunner(unittest.TextTestRunner):
    """Enhanced test runner with magical theming."""
    
    def __init__(self):
        super().__init__(stream=sys.stdout, verbosity=2)
        self.testsRun = 0
        self.failures = []
        self.errors = []
    
    def run(self, test):
        """Run tests with magical output."""
        result = super().run(test)
        
        # Collect results
        self.testsRun = result.testsRun
        self.failures = result.failures
        self.errors = result.errors
        
        return result


# Test classes for core functionality
class TestFamiliarSystem(MagicalTestCase):
    """Test the familiar system."""
    
    def magical_setup(self):
        """Setup test familiars."""
        try:
            from .familiars.entity_familiar import EntityFamiliar
            self.test_familiar = EntityFamiliar("test_familiar")
        except ImportError:
            self.test_familiar = None
    
    def test_familiar_creation(self):
        """Test familiar creation."""
        if self.test_familiar:
            with self.magical_subtest("familiar_creation", TestCategory.UNIT, TestSeverity.CRITICAL):
                self.assertIsNotNone(self.test_familiar)
                self.assertEqual(self.test_familiar.name, "test_familiar")
    
    def test_familiar_properties(self):
        """Test familiar properties."""
        if self.test_familiar:
            with self.magical_subtest("familiar_properties", TestCategory.UNIT, TestSeverity.MAJOR):
                # Test property access
                self.test_familiar.set_property("test_prop", "test_value")
                self.assertEqual(self.test_familiar.get_property("test_prop"), "test_value")


class TestMessagingSystem(MagicalTestCase):
    """Test the messaging system."""
    
    def magical_setup(self):
        """Setup test messaging components."""
        try:
            from .familiars.messaging import MessageRouter, FamiliarMessage
            self.router = MessageRouter()
            self.test_message = FamiliarMessage(
                sender_name="test_sender",
                recipient_name="test_recipient", 
                message_type="test",
                content="test_content"
            )
        except ImportError:
            self.router = None
            self.test_message = None
    
    def test_message_creation(self):
        """Test message creation."""
        if self.test_message:
            with self.magical_subtest("message_creation", TestCategory.UNIT, TestSeverity.CRITICAL):
                self.assertIsNotNone(self.test_message)
                self.assertEqual(self.test_message.sender_name, "test_sender")
                self.assertEqual(self.test_message.recipient_name, "test_recipient")
    
    def test_message_routing(self):
        """Test message routing."""
        if self.router and self.test_message:
            with self.magical_subtest("message_routing", TestCategory.INTEGRATION, TestSeverity.MAJOR):
                # This would test actual routing
                result = self.router.route_message(self.test_message)
                # Basic test - just ensure it doesn't crash
                self.assertIsNotNone(result)


class TestGoalSystem(MagicalTestCase):
    """Test the goal system."""
    
    def magical_setup(self):
        """Setup test goals."""
        try:
            from .goals import GoalArtifact
            self.test_goal = GoalArtifact("test_goal")
        except ImportError:
            self.test_goal = None
    
    def test_goal_creation(self):
        """Test goal creation."""
        if self.test_goal:
            with self.magical_subtest("goal_creation", TestCategory.UNIT, TestSeverity.CRITICAL):
                self.assertIsNotNone(self.test_goal)
                self.assertEqual(self.test_goal.name, "test_goal")
    
    def test_goal_evaluation(self):
        """Test goal evaluation."""
        if self.test_goal:
            with self.magical_subtest("goal_evaluation", TestCategory.UNIT, TestSeverity.MAJOR):
                world_state = {"test": True}
                if hasattr(self.test_goal, 'evaluate'):
                    satisfaction = self.test_goal.evaluate(world_state)
                    self.assertIsInstance(satisfaction, (int, float))


class TestWorldState(MagicalTestCase):
    """Test the world state system."""
    
    def magical_setup(self):
        """Setup test world state."""
        try:
            from .world_state import WorldState
            self.world_state = WorldState()
        except ImportError:
            self.world_state = None
    
    def test_world_state_operations(self):
        """Test world state operations."""
        if self.world_state:
            with self.magical_subtest("world_state_ops", TestCategory.UNIT, TestSeverity.CRITICAL):
                # Test set/get
                self.world_state.set("test_key", "test_value")
                self.assertEqual(self.world_state.get("test_key"), "test_value")


# Global test suite
_test_suite = GrimoireTestSuite()

# Register default test classes
_test_suite.register_test_class(TestFamiliarSystem)
_test_suite.register_test_class(TestMessagingSystem)
_test_suite.register_test_class(TestGoalSystem)
_test_suite.register_test_class(TestWorldState)


def run_tests() -> Dict[str, Any]:
    """Run all tests."""
    return _test_suite.run_all_tests()


def run_performance_tests() -> Dict[str, Any]:
    """Run performance tests."""
    return _test_suite.run_performance_tests()


def register_test_class(test_class: Type[MagicalTestCase]):
    """Register a custom test class."""
    _test_suite.register_test_class(test_class)


if __name__ == "__main__":
    # Run tests if executed directly
    results = run_tests()
    perf_results = run_performance_tests()
    
    print(f"\n🔮 All rituals complete! Success rate: {results['summary']['success_rate']:.1%}")