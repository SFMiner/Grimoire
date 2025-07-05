#!/usr/bin/env python3
"""
Grimoire Performance Optimization Module

This module provides performance optimizations for the Grimoire programming language,
including familiar pooling, message passing optimization, lazy evaluation,
and AI planning algorithm optimizations.
"""

import time
import threading
import weakref
from typing import Dict, List, Any, Optional, Set, Callable, Union, Type, TYPE_CHECKING
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
import functools
import gc

# Import Grimoire components
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import GrimoireFamiliar
    from .familiars.ai_familiar import AIFamiliar
    from .familiars.messaging import FamiliarMessage, MessageRouter
else:
    try:
        from .interpreter import GrimoireFamiliar
        from .familiars.ai_familiar import AIFamiliar
        from .familiars.messaging import FamiliarMessage, MessageRouter
        from .profiler import get_profiler, profile
        IMPORTS_AVAILABLE = True
    except ImportError:
        # Create stub classes for runtime
        class GrimoireFamiliar:
            def __init__(self, name: str):
                self.name = name
                self.true_name = name
                self.state = "inactive"
        
        class AIFamiliar(GrimoireFamiliar):
            def __init__(self, name: str):
                super().__init__(name)
                self.goals = []
                self.actions = []
                self.decision_history = []
                self.world_model = {}
        
        class FamiliarMessage:
            def __init__(self):
                self.sender_name = ""
                self.recipient_name = ""
                self.route_history = []
        
        class MessageRouter:
            def route_message(self, message): 
                return True
        
        def profile(name): 
            from contextlib import nullcontext
            return nullcontext()
        
        def get_profiler(): 
            return None
        
        IMPORTS_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for optimization decisions."""
    creation_time: float = 0.0
    usage_count: int = 0
    last_used: float = 0.0
    memory_usage: int = 0
    cpu_time: float = 0.0
    message_count: int = 0
    
    def update_usage(self):
        """Update usage statistics."""
        self.usage_count += 1
        self.last_used = time.time()
    
    def is_stale(self, max_idle_time: float = 300.0) -> bool:
        """Check if object has been idle too long."""
        return time.time() - self.last_used > max_idle_time


class FamiliarPool:
    """
    Object pool for familiars to reduce creation/destruction overhead.
    
    Provides efficient reuse of familiar instances with automatic cleanup
    and memory management.
    """
    
    def __init__(self, max_pool_size: int = 100, cleanup_interval: float = 60.0):
        self.max_pool_size = max_pool_size
        self.cleanup_interval = cleanup_interval
        
        # Pool storage by familiar type
        self.pools: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_pool_size))
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.active_familiars: Set[str] = set()
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_active = True
        self.cleanup_thread.start()
    
    def acquire(self, familiar_type: str, name: str, *args, **kwargs) -> GrimoireFamiliar:
        """
        Acquire a familiar from the pool or create a new one.
        
        Args:
            familiar_type: Type of familiar to acquire
            name: Name for the familiar
            *args, **kwargs: Arguments for familiar creation
            
        Returns:
            Configured familiar instance
        """
        with self.lock:
            pool = self.pools[familiar_type]
            
            # Try to reuse from pool
            if pool:
                familiar = pool.popleft()
                
                # Reset familiar state
                self._reset_familiar(familiar, name, *args, **kwargs)
                
                # Update metrics
                if familiar.true_name in self.metrics:
                    self.metrics[familiar.true_name].update_usage()
                
                self.active_familiars.add(familiar.true_name)
                return familiar
            
            # Create new familiar if pool is empty
            familiar = self._create_familiar(familiar_type, name, *args, **kwargs)
            
            # Track metrics
            self.metrics[familiar.true_name] = PerformanceMetrics(
                creation_time=time.time(),
                usage_count=1,
                last_used=time.time()
            )
            
            self.active_familiars.add(familiar.true_name)
            return familiar
    
    def release(self, familiar: GrimoireFamiliar) -> None:
        """
        Release a familiar back to the pool.
        
        Args:
            familiar: Familiar to release
        """
        with self.lock:
            if familiar.true_name not in self.active_familiars:
                return  # Already released
            
            familiar_type = self._get_familiar_type(familiar)
            pool = self.pools[familiar_type]
            
            # Clean up familiar state
            self._cleanup_familiar(familiar)
            
            # Return to pool if there's space
            if len(pool) < self.max_pool_size:
                pool.append(familiar)
            
            self.active_familiars.discard(familiar.true_name)
    
    def _create_familiar(self, familiar_type: str, name: str, *args, **kwargs) -> GrimoireFamiliar:
        """Create a new familiar instance."""
        # This would need to be integrated with the actual familiar creation system
        # For now, return a placeholder
        from grimoire.familiars.entity_familiar import EntityFamiliar
        
        if familiar_type == "entity":
            return EntityFamiliar(name)
        elif familiar_type == "ai":
            from grimoire.familiars.ai_familiar import AIFamiliar
            return AIFamiliar(name)
        else:
            # Default to entity familiar
            return EntityFamiliar(name)
    
    def _get_familiar_type(self, familiar: GrimoireFamiliar) -> str:
        """Get the type string for a familiar."""
        return familiar.__class__.__name__.lower().replace("familiar", "")
    
    def _reset_familiar(self, familiar: GrimoireFamiliar, name: str, *args, **kwargs) -> None:
        """Reset a familiar to initial state for reuse."""
        # Reset basic properties
        familiar.name = name
        familiar.state = "inactive"
        
        # Clear activity log if it exists
        if hasattr(familiar, 'activity_log'):
            familiar.activity_log.clear()
        
        # Reset AI-specific state
        if isinstance(familiar, AIFamiliar):
            familiar.goals.clear()
            familiar.actions.clear()
            familiar.decision_history.clear()
            familiar.world_model.clear()
        
        # Clear sockets
        if hasattr(familiar, 'sockets'):
            familiar.sockets.clear()
    
    def _cleanup_familiar(self, familiar: GrimoireFamiliar) -> None:
        """Clean up familiar state before returning to pool."""
        # Disconnect all sockets
        if hasattr(familiar, 'sockets'):
            for socket_name in list(familiar.sockets.keys()):
                try:
                    familiar.sockets[socket_name].disconnect()
                except:
                    pass
        
        # Clear any references
        if hasattr(familiar, 'world_model'):
            familiar.world_model.clear()
        
        # Force garbage collection for this familiar
        gc.collect()
    
    def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self.cleanup_active:
            try:
                self._perform_cleanup()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"Pool cleanup error: {e}")
                time.sleep(self.cleanup_interval)
    
    def _perform_cleanup(self) -> None:
        """Perform periodic cleanup of stale objects."""
        with self.lock:
            # Clean up stale metrics
            stale_keys = []
            for key, metrics in self.metrics.items():
                if metrics.is_stale() and key not in self.active_familiars:
                    stale_keys.append(key)
            
            for key in stale_keys:
                del self.metrics[key]
            
            # Clean up empty pools
            empty_pools = []
            for pool_type, pool in self.pools.items():
                if not pool:
                    empty_pools.append(pool_type)
            
            for pool_type in empty_pools:
                del self.pools[pool_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self.lock:
            return {
                "total_pools": len(self.pools),
                "active_familiars": len(self.active_familiars),
                "pool_sizes": {k: len(v) for k, v in self.pools.items()},
                "total_metrics": len(self.metrics),
                "memory_usage": sum(m.memory_usage for m in self.metrics.values())
            }
    
    def shutdown(self) -> None:
        """Shutdown the pool and cleanup resources."""
        self.cleanup_active = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=1.0)


class OptimizedMessageRouter:
    """
    Optimized message router with caching and batching capabilities.
    
    Provides significant performance improvements for high-frequency
    message passing scenarios.
    """
    
    def __init__(self, base_router: MessageRouter):
        self.base_router = base_router
        
        # Caching
        self.route_cache: Dict[str, List[str]] = {}
        self.cache_max_size = 1000
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Batching
        self.message_queue: deque = deque()
        self.batch_size = 10
        self.batch_timeout = 0.01  # 10ms
        self.last_batch_time = time.time()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Background processing
        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_active = True
        self.processing_thread.start()
    
    def route_message(self, message: FamiliarMessage) -> bool:
        """
        Route a message with optimization.
        
        Args:
            message: Message to route
            
        Returns:
            True if routing was successful
        """
        # Check cache for routing path
        cache_key = f"{message.sender_name}->{message.recipient_name}"
        
        with self.lock:
            if cache_key in self.route_cache:
                self.cache_hits += 1
                # Use cached route
                cached_route = self.route_cache[cache_key]
                message.route_history.extend(cached_route)
            else:
                self.cache_misses += 1
        
        # Add to batch queue for processing
        with self.lock:
            self.message_queue.append(message)
        
        return True
    
    def route_message_immediate(self, message: FamiliarMessage) -> bool:
        """Route a message immediately without batching."""
        result = self.base_router.route_message(message)
        
        # Cache the successful route
        if result:
            cache_key = f"{message.sender_name}->{message.recipient_name}"
            with self.lock:
                if len(self.route_cache) < self.cache_max_size:
                    self.route_cache[cache_key] = message.route_history.copy()
        
        return result
    
    def _process_loop(self) -> None:
        """Background message processing loop."""
        while self.processing_active:
            try:
                self._process_batch()
                time.sleep(0.001)  # 1ms sleep
            except Exception as e:
                print(f"Message processing error: {e}")
                time.sleep(0.01)
    
    def _process_batch(self) -> None:
        """Process a batch of messages."""
        current_time = time.time()
        
        with self.lock:
            queue_size = len(self.message_queue)
            should_process = (
                queue_size >= self.batch_size or
                (queue_size > 0 and current_time - self.last_batch_time > self.batch_timeout)
            )
        
        if not should_process:
            return
        
        # Extract batch
        batch = []
        with self.lock:
            batch_size = min(self.batch_size, len(self.message_queue))
            for _ in range(batch_size):
                if self.message_queue:
                    batch.append(self.message_queue.popleft())
            self.last_batch_time = current_time
        
        # Process batch
        for message in batch:
            try:
                self.route_message_immediate(message)
            except Exception as e:
                print(f"Error routing message {message.message_id}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics."""
        with self.lock:
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0
            
            return {
                "cache_size": len(self.route_cache),
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_rate": hit_rate,
                "queue_size": len(self.message_queue)
            }
    
    def clear_cache(self) -> None:
        """Clear the routing cache."""
        with self.lock:
            self.route_cache.clear()
            self.cache_hits = 0
            self.cache_misses = 0
    
    def shutdown(self) -> None:
        """Shutdown the optimized router."""
        self.processing_active = False
        if self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)


class LazyEvaluator:
    """
    Provides lazy evaluation capabilities for expensive operations.
    
    Defers computation until results are actually needed,
    improving performance for complex AI planning scenarios.
    """
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.max_cache_age = 60.0  # 1 minute
        self.lock = threading.Lock()
    
    def lazy_property(self, dependencies: List[str] = None):
        """Decorator for creating lazy properties."""
        dependencies = dependencies or []
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self_obj, *args, **kwargs):
                # Create cache key
                cache_key = f"{func.__name__}_{id(self_obj)}_{hash(str(args) + str(sorted(kwargs.items())))}"
                
                with self.lock:
                    # Check if cached value is still valid
                    if cache_key in self.cache:
                        cache_time = self.cache_timestamps.get(cache_key, 0)
                        if time.time() - cache_time < self.max_cache_age:
                            # Check dependencies
                            deps = self.cache_dependencies[cache_key]
                            if not any(self._is_dependency_stale(dep) for dep in deps):
                                return self.cache[cache_key]
                    
                    # Compute value
                    result = func(self_obj, *args, **kwargs)
                    
                    # Cache result
                    self.cache[cache_key] = result
                    self.cache_timestamps[cache_key] = time.time()
                    self.cache_dependencies[cache_key] = set(dependencies)
                    
                    return result
            
            return wrapper
        return decorator
    
    def invalidate_dependency(self, dependency: str) -> None:
        """Invalidate all cached values that depend on a specific dependency."""
        with self.lock:
            keys_to_remove = []
            for cache_key, deps in self.cache_dependencies.items():
                if dependency in deps:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                self.cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
                self.cache_dependencies.pop(key, None)
    
    def _is_dependency_stale(self, dependency: str) -> bool:
        """Check if a dependency is stale."""
        # This would be implemented based on specific dependency tracking needs
        return False
    
    def clear_cache(self) -> None:
        """Clear all cached values."""
        with self.lock:
            self.cache.clear()
            self.cache_timestamps.clear()
            self.cache_dependencies.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                "cached_items": len(self.cache),
                "dependencies": len(self.cache_dependencies),
                "memory_usage": sum(len(str(v)) for v in self.cache.values())
            }


class AIOptimizer:
    """
    Optimizations specifically for AI planning algorithms.
    
    Provides caching, pruning, and heuristic optimizations
    for AI decision making and goal evaluation.
    """
    
    def __init__(self):
        self.goal_cache: Dict[str, float] = {}
        self.action_cache: Dict[str, Dict[str, Any]] = {}
        self.decision_tree_cache: Dict[str, List[str]] = {}
        self.pruning_threshold = 0.1
        self.max_search_depth = 5
        self.lock = threading.Lock()
    
    def optimize_goal_evaluation(self, goals: List[Any], world_state: Dict[str, Any]) -> List[Any]:
        """
        Optimize goal evaluation by caching and pruning.
        
        Args:
            goals: List of goals to evaluate
            world_state: Current world state
            
        Returns:
            Optimized list of goals to consider
        """
        with profile("ai_goal_optimization"):
            world_hash = hash(str(sorted(world_state.items())))
            
            optimized_goals = []
            
            for goal in goals:
                cache_key = f"{goal.name}_{world_hash}"
                
                with self.lock:
                    if cache_key in self.goal_cache:
                        cached_satisfaction = self.goal_cache[cache_key]
                        if cached_satisfaction > self.pruning_threshold:
                            optimized_goals.append(goal)
                    else:
                        # Evaluate goal
                        try:
                            satisfaction = goal.evaluate(world_state) if hasattr(goal, 'evaluate') else 0.0
                            self.goal_cache[cache_key] = satisfaction
                            
                            if satisfaction > self.pruning_threshold:
                                optimized_goals.append(goal)
                        except Exception as e:
                            print(f"Goal evaluation error for {goal.name}: {e}")
            
            return optimized_goals
    
    def optimize_action_selection(self, actions: List[Any], world_state: Dict[str, Any]) -> List[Any]:
        """
        Optimize action selection using precondition caching.
        
        Args:
            actions: Available actions
            world_state: Current world state
            
        Returns:
            List of viable actions
        """
        with profile("ai_action_optimization"):
            world_hash = hash(str(sorted(world_state.items())))
            viable_actions = []
            
            for action in actions:
                cache_key = f"{action.name}_{world_hash}"
                
                with self.lock:
                    if cache_key in self.action_cache:
                        cached_result = self.action_cache[cache_key]
                        if cached_result.get("viable", False):
                            viable_actions.append(action)
                    else:
                        # Check preconditions
                        try:
                            viable = True
                            if hasattr(action, 'precondition') and action.precondition:
                                viable = action.precondition(world_state)
                            
                            result = {"viable": viable, "timestamp": time.time()}
                            self.action_cache[cache_key] = result
                            
                            if viable:
                                viable_actions.append(action)
                        except Exception as e:
                            print(f"Action precondition error for {action.name}: {e}")
            
            return viable_actions
    
    def optimize_decision_tree(self, goals: List[Any], actions: List[Any], max_depth: int = None) -> List[str]:
        """
        Generate optimized decision tree for AI planning.
        
        Args:
            goals: Available goals
            actions: Available actions
            max_depth: Maximum search depth
            
        Returns:
            Optimized action sequence
        """
        max_depth = max_depth or self.max_search_depth
        
        # Create cache key
        goal_names = sorted([g.name for g in goals])
        action_names = sorted([a.name for a in actions])
        cache_key = f"{hash(str(goal_names))}_{hash(str(action_names))}_{max_depth}"
        
        with self.lock:
            if cache_key in self.decision_tree_cache:
                return self.decision_tree_cache[cache_key]
        
        # Generate decision tree (simplified)
        decision_sequence = []
        
        # Sort goals by priority/urgency
        sorted_goals = sorted(goals, key=lambda g: getattr(g, 'priority', 0), reverse=True)
        
        for goal in sorted_goals[:3]:  # Limit to top 3 goals for performance
            # Find actions that contribute to this goal
            relevant_actions = [a for a in actions if self._action_contributes_to_goal(a, goal)]
            
            if relevant_actions:
                # Select best action (simplified heuristic)
                best_action = max(relevant_actions, key=lambda a: getattr(a, 'utility', 0))
                decision_sequence.append(best_action.name)
        
        # Cache result
        with self.lock:
            self.decision_tree_cache[cache_key] = decision_sequence
        
        return decision_sequence
    
    def _action_contributes_to_goal(self, action: Any, goal: Any) -> bool:
        """Check if an action contributes to a goal."""
        # Simplified check - would be more sophisticated in practice
        action_name = getattr(action, 'name', '').lower()
        goal_name = getattr(goal, 'name', '').lower()
        
        # Simple keyword matching
        return any(word in action_name for word in goal_name.split('_'))
    
    def clear_caches(self) -> None:
        """Clear all optimization caches."""
        with self.lock:
            self.goal_cache.clear()
            self.action_cache.clear()
            self.decision_tree_cache.clear()
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        with self.lock:
            return {
                "goal_cache_size": len(self.goal_cache),
                "action_cache_size": len(self.action_cache),
                "decision_tree_cache_size": len(self.decision_tree_cache),
                "pruning_threshold": self.pruning_threshold,
                "max_search_depth": self.max_search_depth
            }


# Global optimization instances
_familiar_pool = FamiliarPool()
_lazy_evaluator = LazyEvaluator()
_ai_optimizer = AIOptimizer()


def get_familiar_pool() -> FamiliarPool:
    """Get the global familiar pool."""
    return _familiar_pool


def get_lazy_evaluator() -> LazyEvaluator:
    """Get the global lazy evaluator."""
    return _lazy_evaluator


def get_ai_optimizer() -> AIOptimizer:
    """Get the global AI optimizer."""
    return _ai_optimizer


def optimize_message_router(router: MessageRouter) -> OptimizedMessageRouter:
    """Create an optimized version of a message router."""
    return OptimizedMessageRouter(router)


@contextmanager
def optimized_familiar_context():
    """Context manager for optimized familiar operations."""
    pool = get_familiar_pool()
    try:
        yield pool
    finally:
        # Cleanup is handled by the pool itself
        pass


def performance_critical(func):
    """Decorator to mark functions as performance critical."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with profile(f"critical_{func.__name__}"):
            return func(*args, **kwargs)
    return wrapper


def shutdown_optimizations():
    """Shutdown all optimization systems."""
    _familiar_pool.shutdown()
    _lazy_evaluator.clear_cache()
    _ai_optimizer.clear_caches()