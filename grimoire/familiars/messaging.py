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
Grimoire Familiar Messaging System

This module implements the communication protocols for inter-familiar messaging,
including standardized message formats, routing, and error handling.
"""

import time
import uuid
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
import threading
import queue
import logging


class MessageType(Enum):
    """Types of messages that can be sent between familiars."""
    PROPERTY_UPDATE = auto()    # Entity property changes
    GOAL_UPDATE = auto()        # AI goal state changes
    ACTION_REQUEST = auto()     # Request for action execution
    ACTION_RESPONSE = auto()    # Response to action request
    QUERY = auto()              # Information request
    QUERY_RESPONSE = auto()     # Response to query
    NOTIFICATION = auto()       # General notification
    ERROR = auto()              # Error message
    HEARTBEAT = auto()          # Keep-alive message
    BROADCAST = auto()          # Message to multiple recipients


class MessagePriority(Enum):
    """Priority levels for message routing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class FamiliarMessage:
    """
    Standardized message format for inter-familiar communication.
    
    This provides a consistent interface for all familiar-to-familiar
    communication, with routing information, type safety, and debugging support.
    """
    # Core message identification
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    # Routing information
    sender_name: str = ""
    sender_true_name: str = ""
    recipient_name: str = ""
    recipient_true_name: Optional[str] = None
    
    # Message content
    message_type: MessageType = MessageType.NOTIFICATION
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Message metadata
    priority: MessagePriority = MessagePriority.NORMAL
    requires_response: bool = False
    response_to: Optional[str] = None  # ID of message this responds to
    expires_at: Optional[float] = None
    
    # Routing metadata
    hop_count: int = 0
    max_hops: int = 10
    route_history: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate message after creation."""
        if not self.sender_name:
            raise ValueError("Message must have a sender_name")
        if not self.recipient_name:
            raise ValueError("Message must have a recipient_name")
        
        # Set default expiration (5 minutes from now)
        if self.expires_at is None:
            self.expires_at = time.time() + 300
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        return self.expires_at is not None and time.time() > self.expires_at
    
    def can_forward(self) -> bool:
        """Check if message can be forwarded (hasn't exceeded hop limit)."""
        return self.hop_count < self.max_hops
    
    def add_hop(self, router_name: str) -> bool:
        """
        Add a hop to the message route.
        
        Returns:
            True if hop was added, False if hop limit exceeded
        """
        if not self.can_forward():
            return False
        
        self.hop_count += 1
        self.route_history.append(router_name)
        return True
    
    def create_response(self, sender_name: str, sender_true_name: str, 
                       payload: Dict[str, Any]) -> 'FamiliarMessage':
        """Create a response message to this message."""
        return FamiliarMessage(
            sender_name=sender_name,
            sender_true_name=sender_true_name,
            recipient_name=self.sender_name,
            recipient_true_name=self.sender_true_name,
            message_type=MessageType.QUERY_RESPONSE if self.message_type == MessageType.QUERY else MessageType.ACTION_RESPONSE,
            payload=payload,
            priority=self.priority,
            response_to=self.message_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender_name": self.sender_name,
            "sender_true_name": self.sender_true_name,
            "recipient_name": self.recipient_name,
            "recipient_true_name": self.recipient_true_name,
            "message_type": self.message_type.name,
            "payload": self.payload,
            "priority": self.priority.name,
            "requires_response": self.requires_response,
            "response_to": self.response_to,
            "expires_at": self.expires_at,
            "hop_count": self.hop_count,
            "max_hops": self.max_hops,
            "route_history": self.route_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FamiliarMessage':
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            timestamp=data["timestamp"],
            sender_name=data["sender_name"],
            sender_true_name=data["sender_true_name"],
            recipient_name=data["recipient_name"],
            recipient_true_name=data.get("recipient_true_name"),
            message_type=MessageType[data["message_type"]],
            payload=data["payload"],
            priority=MessagePriority[data["priority"]],
            requires_response=data["requires_response"],
            response_to=data.get("response_to"),
            expires_at=data.get("expires_at"),
            hop_count=data["hop_count"],
            max_hops=data["max_hops"],
            route_history=data["route_history"]
        )
    
    def __str__(self) -> str:
        return f"FamiliarMessage({self.message_type.name}: {self.sender_name} → {self.recipient_name})"
    
    def __repr__(self) -> str:
        return f"FamiliarMessage(id={self.message_id[:8]}, type={self.message_type.name}, from={self.sender_name}, to={self.recipient_name})"


class MessageRouterError(Exception):
    """Base exception for message routing errors."""
    pass


class FamiliarNotFoundError(MessageRouterError):
    """Raised when a message recipient cannot be found."""
    pass


class MessageExpiredError(MessageRouterError):
    """Raised when attempting to route an expired message."""
    pass


class RoutingLoopError(MessageRouterError):
    """Raised when a routing loop is detected."""
    pass


@dataclass
class RoutingRule:
    """Rule for message routing decisions."""
    condition: Callable[[FamiliarMessage], bool]
    action: Callable[[FamiliarMessage], str]  # Returns next hop
    description: str
    priority: int = 0  # Higher priority rules are checked first


class MessageRouter:
    """
    Central message routing system for inter-familiar communication.
    
    Handles message delivery, routing, error recovery, and debugging.
    Integrates with the socket system for actual message transport.
    """
    
    def __init__(self, name: str = "MessageRouter"):
        self.name = name
        self.familiars: Dict[str, Any] = {}  # name -> familiar object
        self.true_name_lookup: Dict[str, str] = {}  # true_name -> name
        self.message_queue = queue.PriorityQueue()
        self.routing_rules: List[RoutingRule] = []
        self.message_history: List[FamiliarMessage] = []
        self.max_history_size = 1000
        
        # Error handling
        self.failed_messages: List[FamiliarMessage] = []
        self.error_handlers: Dict[type, Callable] = {}
        
        # Statistics
        self.stats = {
            "messages_routed": 0,
            "messages_failed": 0,
            "messages_expired": 0,
            "routing_loops": 0
        }
        
        # Threading for async message processing
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Set up logging
        self.logger = logging.getLogger(f"MessageRouter.{name}")
        
        # Add default routing rules
        self._setup_default_routing_rules()
    
    def _setup_default_routing_rules(self):
        """Set up default message routing rules."""
        # Direct delivery rule (highest priority)
        self.add_routing_rule(
            condition=lambda msg: msg.recipient_name in self.familiars,
            action=lambda msg: msg.recipient_name,
            description="Direct delivery to registered familiar",
            priority=100
        )
        
        # True name lookup rule
        self.add_routing_rule(
            condition=lambda msg: bool(msg.recipient_true_name and msg.recipient_true_name in self.true_name_lookup),
            action=lambda msg: self.true_name_lookup[msg.recipient_true_name] if msg.recipient_true_name else "",
            description="Delivery via true name lookup",
            priority=90
        )
        
        # Broadcast rule (lowest priority)
        self.add_routing_rule(
            condition=lambda msg: msg.message_type == MessageType.BROADCAST,
            action=lambda msg: "*",  # Special marker for broadcast
            description="Broadcast to all familiars",
            priority=10
        )
    
    def register_familiar(self, familiar: Any) -> None:
        """Register a familiar with the router."""
        with self._lock:
            self.familiars[familiar.name] = familiar
            if hasattr(familiar, 'true_name'):
                self.true_name_lookup[familiar.true_name] = familiar.name
            
            self.logger.info(f"Registered familiar: {familiar.name}")
    
    def unregister_familiar(self, familiar_name: str) -> None:
        """Unregister a familiar from the router."""
        with self._lock:
            if familiar_name in self.familiars:
                familiar = self.familiars[familiar_name]
                if hasattr(familiar, 'true_name') and familiar.true_name in self.true_name_lookup:
                    del self.true_name_lookup[familiar.true_name]
                del self.familiars[familiar_name]
                
                self.logger.info(f"Unregistered familiar: {familiar_name}")
    
    def add_routing_rule(self, condition: Callable[[FamiliarMessage], bool],
                        action: Callable[[FamiliarMessage], str],
                        description: str, priority: int = 0) -> None:
        """Add a custom routing rule."""
        rule = RoutingRule(condition, action, description, priority)
        self.routing_rules.append(rule)
        # Sort by priority (highest first)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
        
        self.logger.info(f"Added routing rule: {description} (priority {priority})")
    
    def route_message(self, message: FamiliarMessage) -> bool:
        """
        Route a message to its destination.
        
        Returns:
            True if message was successfully routed, False otherwise
        """
        try:
            # Validate message
            if message.is_expired():
                raise MessageExpiredError(f"Message {message.message_id} has expired")
            
            # Check for routing loops
            if message.route_history.count(self.name) > 1:
                raise RoutingLoopError(f"Routing loop detected for message {message.message_id}")
            
            # Add this router to the route history
            if not message.add_hop(self.name):
                raise MessageRouterError(f"Message {message.message_id} exceeded hop limit")
            
            # Find routing destination
            destination = self._find_destination(message)
            
            if destination == "*":
                # Broadcast message
                return self._broadcast_message(message)
            elif destination in self.familiars:
                # Direct delivery
                return self._deliver_message(message, destination)
            else:
                raise FamiliarNotFoundError(f"No route found for recipient: {message.recipient_name}")
        
        except Exception as e:
            self._handle_routing_error(message, e)
            return False
    
    def _find_destination(self, message: FamiliarMessage) -> str:
        """Find the destination for a message using routing rules."""
        for rule in self.routing_rules:
            try:
                if rule.condition(message):
                    destination = rule.action(message)
                    self.logger.debug(f"Message {message.message_id} matched rule: {rule.description} -> {destination}")
                    return destination
            except Exception as e:
                self.logger.warning(f"Routing rule failed: {rule.description} - {e}")
                continue
        
        raise FamiliarNotFoundError(f"No routing rule matched for message {message.message_id}")
    
    def _deliver_message(self, message: FamiliarMessage, destination: str) -> bool:
        """Deliver message to a specific familiar."""
        try:
            familiar = self.familiars[destination]
            
            # Use socket system if available
            if hasattr(familiar, 'has_socket') and familiar.has_socket("message_input"):
                familiar.send_to_socket("message_input", message.to_dict())
            elif hasattr(familiar, 'receive_message'):
                familiar.receive_message(message)
            else:
                # Fallback: log the message delivery
                self.logger.info(f"Delivered message {message.message_id} to {destination}")
            
            # Update statistics
            self.stats["messages_routed"] += 1
            
            # Add to history
            self._add_to_history(message)
            
            self.logger.debug(f"Successfully delivered message {message.message_id} to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deliver message {message.message_id} to {destination}: {e}")
            raise MessageRouterError(f"Delivery failed: {e}")
    
    def _broadcast_message(self, message: FamiliarMessage) -> bool:
        """Broadcast message to all registered familiars."""
        success_count = 0
        total_familiars = len(self.familiars)
        
        for familiar_name, familiar in self.familiars.items():
            try:
                # Create individual message for each recipient
                broadcast_msg = FamiliarMessage(
                    message_id=f"{message.message_id}-{familiar_name}",
                    timestamp=message.timestamp,
                    sender_name=message.sender_name,
                    sender_true_name=message.sender_true_name,
                    recipient_name=familiar_name,
                    recipient_true_name=getattr(familiar, 'true_name', None),
                    message_type=message.message_type,
                    payload=message.payload.copy(),
                    priority=message.priority,
                    expires_at=message.expires_at
                )
                
                if self._deliver_message(broadcast_msg, familiar_name):
                    success_count += 1
                    
            except Exception as e:
                self.logger.warning(f"Failed to broadcast to {familiar_name}: {e}")
        
        self.logger.info(f"Broadcast completed: {success_count}/{total_familiars} deliveries successful")
        return success_count > 0
    
    def _handle_routing_error(self, message: FamiliarMessage, error: Exception) -> None:
        """Handle routing errors and update statistics."""
        self.failed_messages.append(message)
        
        if isinstance(error, MessageExpiredError):
            self.stats["messages_expired"] += 1
        elif isinstance(error, RoutingLoopError):
            self.stats["routing_loops"] += 1
        else:
            self.stats["messages_failed"] += 1
        
        # Call custom error handlers
        error_type = type(error)
        if error_type in self.error_handlers:
            try:
                self.error_handlers[error_type](message, error)
            except Exception as handler_error:
                self.logger.error(f"Error handler failed: {handler_error}")
        
        self.logger.error(f"Routing failed for message {message.message_id}: {error}")
    
    def _add_to_history(self, message: FamiliarMessage) -> None:
        """Add message to routing history."""
        self.message_history.append(message)
        
        # Trim history if too long
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size//2:]
    
    def send_message(self, sender_name: str, sender_true_name: str,
                    recipient_name: str, message_type: MessageType,
                    payload: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                    requires_response: bool = False) -> str:
        """
        Convenience method to create and route a message.
        
        Returns:
            Message ID of the sent message
        """
        message = FamiliarMessage(
            sender_name=sender_name,
            sender_true_name=sender_true_name,
            recipient_name=recipient_name,
            message_type=message_type,
            payload=payload,
            priority=priority,
            requires_response=requires_response
        )
        
        # Add to queue for processing
        priority_value = priority.value
        self.message_queue.put((priority_value, time.time(), message))
        
        return message.message_id
    
    def start_async_processing(self) -> None:
        """Start asynchronous message processing."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_messages, daemon=True)
        self._worker_thread.start()
        self.logger.info("Started async message processing")
    
    def stop_async_processing(self) -> None:
        """Stop asynchronous message processing."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=1.0)
        self.logger.info("Stopped async message processing")
    
    def _process_messages(self) -> None:
        """Background thread for processing message queue."""
        while self._running:
            try:
                # Get message from queue (timeout to allow checking _running)
                priority, timestamp, message = self.message_queue.get(timeout=1.0)
                self.route_message(message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            **self.stats,
            "registered_familiars": len(self.familiars),
            "queue_size": self.message_queue.qsize(),
            "failed_messages": len(self.failed_messages),
            "history_size": len(self.message_history),
            "routing_rules": len(self.routing_rules)
        }
    
    def get_message_history(self, limit: int = 50) -> List[FamiliarMessage]:
        """Get recent message history."""
        return self.message_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear message history and failed messages."""
        self.message_history.clear()
        self.failed_messages.clear()
        self.logger.info("Cleared message history")
    
    def add_error_handler(self, error_type: type, handler: Callable[[FamiliarMessage, Exception], None]) -> None:
        """Add custom error handler for specific exception types."""
        self.error_handlers[error_type] = handler
        self.logger.info(f"Added error handler for {error_type.__name__}")
    
    def __str__(self) -> str:
        return f"MessageRouter({self.name}: {len(self.familiars)} familiars)"
    
    def __repr__(self) -> str:
        return f"MessageRouter(name='{self.name}', familiars={len(self.familiars)}, rules={len(self.routing_rules)})"


# Convenience functions for common message types
def create_property_update_message(sender_name: str, sender_true_name: str,
                                 recipient_name: str, property_name: str,
                                 old_value: Any, new_value: Any) -> FamiliarMessage:
    """Create a property update message."""
    return FamiliarMessage(
        sender_name=sender_name,
        sender_true_name=sender_true_name,
        recipient_name=recipient_name,
        message_type=MessageType.PROPERTY_UPDATE,
        payload={
            "property_name": property_name,
            "old_value": old_value,
            "new_value": new_value
        }
    )


def create_query_message(sender_name: str, sender_true_name: str,
                        recipient_name: str, query: str) -> FamiliarMessage:
    """Create a query message."""
    return FamiliarMessage(
        sender_name=sender_name,
        sender_true_name=sender_true_name,
        recipient_name=recipient_name,
        message_type=MessageType.QUERY,
        payload={"query": query},
        requires_response=True
    )


def create_action_request_message(sender_name: str, sender_true_name: str,
                                recipient_name: str, action: str,
                                arguments: List[Any]) -> FamiliarMessage:
    """Create an action request message."""
    return FamiliarMessage(
        sender_name=sender_name,
        sender_true_name=sender_true_name,
        recipient_name=recipient_name,
        message_type=MessageType.ACTION_REQUEST,
        payload={
            "action": action,
            "arguments": arguments
        },
        requires_response=True
    )


# Global message router instance
_global_router: Optional[MessageRouter] = None


def get_global_router() -> MessageRouter:
    """Get or create the global message router."""
    global _global_router
    if _global_router is None:
        _global_router = MessageRouter("GlobalRouter")
    return _global_router


def set_global_router(router: MessageRouter) -> None:
    """Set the global message router."""
    global _global_router
    _global_router = router