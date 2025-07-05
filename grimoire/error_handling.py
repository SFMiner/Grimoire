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
Grimoire Error Handling and Robustness Module

This module provides enhanced error handling with magical theming,
graceful familiar failure handling, socket connection recovery,
and comprehensive error reporting for the Grimoire programming language.
"""

import sys
import time
import traceback
import threading
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Type, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import functools


class ErrorSeverity(Enum):
    """Magical error severity levels."""
    WHISPER = "whisper"           # Minor warnings
    MURMUR = "murmur"            # Standard warnings  
    INCANTATION = "incantation"   # Errors
    CURSE = "curse"              # Critical errors
    VOID_TOUCH = "void_touch"    # Fatal errors


class ErrorDomain(Enum):
    """Magical error domains."""
    ARCANE = "arcane"            # Language/syntax errors
    FAMILIAR = "familiar"        # Familiar-related errors
    SOCKET = "socket"           # Communication errors
    RITUAL = "ritual"           # Function/method errors
    ARTIFACT = "artifact"       # Class/object errors
    PLANE = "plane"             # Planar system errors
    EFFECT = "effect"           # Effect system errors
    WORLD = "world"             # World state errors


@dataclass
class MagicalError:
    """Enhanced error with magical theming and context."""
    severity: ErrorSeverity
    domain: ErrorDomain
    message: str
    magical_message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    stack_trace: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.magical_message:
            self.magical_message = self._generate_magical_message()
        
        if not self.stack_trace:
            self.stack_trace = traceback.format_exc()
    
    def _generate_magical_message(self) -> str:
        """Generate a magical-themed error message."""
        severity_phrases = {
            ErrorSeverity.WHISPER: "The aether whispers of",
            ErrorSeverity.MURMUR: "The spirits murmur about", 
            ErrorSeverity.INCANTATION: "The ritual falters due to",
            ErrorSeverity.CURSE: "A curse has befallen your magic:",
            ErrorSeverity.VOID_TOUCH: "The void has consumed your spell:"
        }
        
        domain_phrases = {
            ErrorDomain.ARCANE: "a disturbance in the arcane weave",
            ErrorDomain.FAMILIAR: "a familiar's rebellion",
            ErrorDomain.SOCKET: "severed ethereal connections", 
            ErrorDomain.RITUAL: "a broken ritual circle",
            ErrorDomain.ARTIFACT: "a corrupted magical artifact",
            ErrorDomain.PLANE: "planar instability",
            ErrorDomain.EFFECT: "chaotic magical effects",
            ErrorDomain.WORLD: "a tear in the fabric of reality"
        }
        
        severity_phrase = severity_phrases.get(self.severity, "Unknown forces speak of")
        domain_phrase = domain_phrases.get(self.domain, "mysterious circumstances")
        
        return f"{severity_phrase} {domain_phrase}. {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "severity": self.severity.value,
            "domain": self.domain.value,
            "message": self.message,
            "magical_message": self.magical_message,
            "context": self.context,
            "timestamp": self.timestamp,
            "suggestions": self.suggestions,
            "recovery_actions": self.recovery_actions
        }


class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""
    
    def can_handle(self, error: MagicalError) -> bool:
        """Check if this strategy can handle the error."""
        raise NotImplementedError
    
    def recover(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover from the error."""
        raise NotImplementedError
    
    def get_priority(self) -> int:
        """Get the priority of this recovery strategy (higher = more important)."""
        return 0


class FamiliarRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for familiar-related errors."""
    
    def can_handle(self, error: MagicalError) -> bool:
        return error.domain == ErrorDomain.FAMILIAR
    
    def recover(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover familiar functionality."""
        familiar = context.get("familiar")
        if not familiar:
            return False
        
        try:
            # Reset familiar to safe state
            if hasattr(familiar, 'state'):
                familiar.state = "inactive"
            
            # Clear problematic data
            if hasattr(familiar, 'sockets'):
                for socket_name in list(familiar.sockets.keys()):
                    try:
                        socket = familiar.sockets[socket_name]
                        if hasattr(socket, 'disconnect'):
                            socket.disconnect()
                    except:
                        pass
                familiar.sockets.clear()
            
            # Clear AI state if applicable
            if hasattr(familiar, 'goals'):
                familiar.goals.clear()
            if hasattr(familiar, 'actions'):
                familiar.actions.clear()
            if hasattr(familiar, 'world_model'):
                familiar.world_model.clear()
            
            return True
            
        except Exception as e:
            print(f"Familiar recovery failed: {e}")
            return False
    
    def get_priority(self) -> int:
        return 80


class SocketRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for socket communication errors."""
    
    def can_handle(self, error: MagicalError) -> bool:
        return error.domain == ErrorDomain.SOCKET
    
    def recover(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover socket connections."""
        socket = context.get("socket")
        router = context.get("router")
        
        if socket:
            try:
                # Attempt reconnection
                if hasattr(socket, 'reconnect'):
                    socket.reconnect()
                elif hasattr(socket, 'connect'):
                    socket.connect()
                return True
            except:
                pass
        
        if router:
            try:
                # Reset router state
                if hasattr(router, 'clear_cache'):
                    router.clear_cache()
                if hasattr(router, 'reset_connections'):
                    router.reset_connections()
                return True
            except:
                pass
        
        return False
    
    def get_priority(self) -> int:
        return 70


class RitualRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for ritual (function) errors."""
    
    def can_handle(self, error: MagicalError) -> bool:
        return error.domain == ErrorDomain.RITUAL
    
    def recover(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover from ritual errors."""
        # For ritual errors, we typically can't recover automatically
        # but we can provide helpful suggestions
        error.suggestions.extend([
            "Check ritual parameters and their types",
            "Verify all required familiars are active",
            "Ensure proper ritual circle (scope) setup",
            "Review ritual incantation (syntax) for errors"
        ])
        
        return False  # Cannot auto-recover from ritual errors
    
    def get_priority(self) -> int:
        return 50


class WorldStateRecoveryStrategy(ErrorRecoveryStrategy):
    """Recovery strategy for world state errors."""
    
    def can_handle(self, error: MagicalError) -> bool:
        return error.domain == ErrorDomain.WORLD
    
    def recover(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover world state."""
        world_state = context.get("world_state")
        
        if world_state:
            try:
                # Reset to safe defaults
                if hasattr(world_state, 'reset_to_defaults'):
                    world_state.reset_to_defaults()
                elif hasattr(world_state, 'clear'):
                    world_state.clear()
                    # Set basic defaults
                    world_state.set("time", 0)
                    world_state.set("initialized", True)
                
                return True
            except:
                pass
        
        return False
    
    def get_priority(self) -> int:
        return 90


class ErrorHandler:
    """
    Enhanced error handler with magical theming and recovery capabilities.
    
    Provides comprehensive error handling, logging, and recovery
    for all Grimoire systems.
    """
    
    def __init__(self, log_file: Optional[str] = None):
        self.recovery_strategies: List[ErrorRecoveryStrategy] = []
        self.error_history: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.suppressed_errors: Set[str] = set()
        
        # Setup logging
        self.logger = self._setup_logger(log_file)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def _setup_logger(self, log_file: Optional[str]) -> logging.Logger:
        """Setup magical-themed logger."""
        logger = logging.getLogger("grimoire.error_handler")
        logger.setLevel(logging.DEBUG)
        
        # Create formatter with magical theming
        formatter = logging.Formatter(
            '🔮 %(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _register_default_strategies(self):
        """Register default recovery strategies."""
        self.register_recovery_strategy(FamiliarRecoveryStrategy())
        self.register_recovery_strategy(SocketRecoveryStrategy())
        self.register_recovery_strategy(RitualRecoveryStrategy())
        self.register_recovery_strategy(WorldStateRecoveryStrategy())
    
    def register_recovery_strategy(self, strategy: ErrorRecoveryStrategy):
        """Register a new error recovery strategy."""
        with self.lock:
            self.recovery_strategies.append(strategy)
            # Sort by priority (highest first)
            self.recovery_strategies.sort(key=lambda s: s.get_priority(), reverse=True)
    
    def handle_error(self, 
                    exception: Exception, 
                    severity: ErrorSeverity = ErrorSeverity.INCANTATION,
                    domain: ErrorDomain = ErrorDomain.ARCANE,
                    context: Optional[Dict[str, Any]] = None,
                    magical_message: Optional[str] = None) -> MagicalError:
        """
        Handle an error with magical theming and recovery attempts.
        
        Args:
            exception: The original exception
            severity: Error severity level
            domain: Error domain
            context: Additional context for recovery
            magical_message: Custom magical error message
            
        Returns:
            MagicalError instance with recovery information
        """
        context = context or {}
        
        # Create magical error
        magical_error = MagicalError(
            severity=severity,
            domain=domain,
            message=str(exception),
            magical_message=magical_message or "",
            context=context,
            stack_trace=traceback.format_exc()
        )
        
        # Add to history
        with self.lock:
            self.error_history.append(magical_error)
            error_key = f"{domain.value}:{type(exception).__name__}"
            self.error_counts[error_key] += 1
        
        # Log the error
        self._log_error(magical_error)
        
        # Attempt recovery
        recovery_attempted = self._attempt_recovery(magical_error, context)
        
        if recovery_attempted:
            magical_error.recovery_actions.append("Automatic recovery attempted")
        
        return magical_error
    
    def _log_error(self, error: MagicalError):
        """Log error with appropriate level."""
        log_level_map = {
            ErrorSeverity.WHISPER: logging.DEBUG,
            ErrorSeverity.MURMUR: logging.INFO,
            ErrorSeverity.INCANTATION: logging.WARNING,
            ErrorSeverity.CURSE: logging.ERROR,
            ErrorSeverity.VOID_TOUCH: logging.CRITICAL
        }
        
        level = log_level_map.get(error.severity, logging.ERROR)
        self.logger.log(level, error.magical_message)
        
        # Log stack trace for serious errors
        if error.severity in [ErrorSeverity.CURSE, ErrorSeverity.VOID_TOUCH]:
            self.logger.log(level, f"Stack trace:\n{error.stack_trace}")
    
    def _attempt_recovery(self, error: MagicalError, context: Dict[str, Any]) -> bool:
        """Attempt to recover from error using registered strategies."""
        for strategy in self.recovery_strategies:
            if strategy.can_handle(error):
                try:
                    if strategy.recover(error, context):
                        self.logger.info(f"Recovery successful using {strategy.__class__.__name__}")
                        return True
                except Exception as e:
                    self.logger.warning(f"Recovery strategy {strategy.__class__.__name__} failed: {e}")
        
        return False
    
    def suppress_error_type(self, error_type: str):
        """Suppress errors of a specific type."""
        with self.lock:
            self.suppressed_errors.add(error_type)
    
    def unsuppress_error_type(self, error_type: str):
        """Stop suppressing errors of a specific type."""
        with self.lock:
            self.suppressed_errors.discard(error_type)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self.lock:
            return {
                "total_errors": len(self.error_history),
                "error_counts": dict(self.error_counts),
                "suppressed_types": list(self.suppressed_errors),
                "recent_errors": [e.to_dict() for e in list(self.error_history)[-10:]]
            }
    
    def clear_error_history(self):
        """Clear error history."""
        with self.lock:
            self.error_history.clear()
            self.error_counts.clear()


def magical_exception_handler(error_handler: ErrorHandler):
    """Decorator to add magical error handling to functions."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Determine domain based on function name/module
                domain = ErrorDomain.ARCANE
                if 'familiar' in func.__name__.lower():
                    domain = ErrorDomain.FAMILIAR
                elif 'socket' in func.__name__.lower():
                    domain = ErrorDomain.SOCKET
                elif 'ritual' in func.__name__.lower():
                    domain = ErrorDomain.RITUAL
                
                magical_error = error_handler.handle_error(
                    e, 
                    domain=domain,
                    context={'function': func.__name__, 'args': args, 'kwargs': kwargs}
                )
                
                # Re-raise for serious errors
                if magical_error.severity in [ErrorSeverity.CURSE, ErrorSeverity.VOID_TOUCH]:
                    raise
                
                return None
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler."""
    return _global_error_handler


def handle_familiar_error(familiar, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Convenience function for handling familiar errors."""
    context = context or {}
    context['familiar'] = familiar
    
    return _global_error_handler.handle_error(
        exception,
        severity=ErrorSeverity.INCANTATION,
        domain=ErrorDomain.FAMILIAR,
        context=context
    )


def handle_socket_error(socket, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Convenience function for handling socket errors."""
    context = context or {}
    context['socket'] = socket
    
    return _global_error_handler.handle_error(
        exception,
        severity=ErrorSeverity.MURMUR,
        domain=ErrorDomain.SOCKET,
        context=context
    )


def handle_world_state_error(world_state, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Convenience function for handling world state errors."""
    context = context or {}
    context['world_state'] = world_state
    
    return _global_error_handler.handle_error(
        exception,
        severity=ErrorSeverity.CURSE,
        domain=ErrorDomain.WORLD,
        context=context
    )


@magical_exception_handler(_global_error_handler)
def safe_familiar_operation(func: Callable, *args, **kwargs):
    """Safely execute a familiar operation with error handling."""
    return func(*args, **kwargs)


def create_magical_traceback(exception: Exception) -> str:
    """Create a magical-themed traceback."""
    tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
    
    magical_tb = "🔮 MAGICAL TRACEBACK (most recent incantation last):\n"
    
    for line in tb_lines:
        # Replace technical terms with magical ones
        magical_line = line
        magical_line = magical_line.replace("File", "Grimoire")
        magical_line = magical_line.replace("line", "verse")
        magical_line = magical_line.replace("function", "ritual")
        magical_line = magical_line.replace("class", "artifact")
        magical_line = magical_line.replace("module", "tome")
        
        magical_tb += magical_line
    
    return magical_tb