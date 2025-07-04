from __future__ import annotations

"""Standardised inter-familiar message protocol.

This lightweight helper provides a unified structure (`Message`) for all
socket-based communications between familiars.  Using a dataclass enforces a
consistent schema while remaining serialisable as a normal Python `dict`.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import time
import uuid
from datetime import datetime

__all__ = ["Message", "FamiliarMessage", "MessageRouter", "build_message", "is_message"]


@dataclass
class Message:
    """A structured communication unit sent over sockets."""

    sender: str                # familiar true_name or friendly name
    target: Optional[str]      # intended recipient; None == broadcast
    category: str              # arbitrary category: "command", "info", etc.
    payload: Any               # the actual content
    timestamp: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(**data)  # type: ignore[arg-type]

    # Convenience pretty-print
    def __str__(self) -> str:  # pragma: no cover
        tgt = self.target or "*"
        return f"[{self.category}] {self.sender} -> {tgt}: {self.payload} (@{self.timestamp:.2f})"


@dataclass
class FamiliarMessage:
    """Enhanced message format for inter-familiar communication."""
    id: str
    sender: str
    recipient: str  
    message_type: str
    payload: Any
    timestamp: datetime
    reply_to: Optional[str] = None
    
    @classmethod
    def create(cls, sender: str, recipient: str, msg_type: str, payload: Any) -> "FamiliarMessage":
        return cls(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=msg_type, 
            payload=payload,
            timestamp=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FamiliarMessage":
        return cls(**data)


class MessageRouter:
    """Routes messages between familiars with debugging support."""
    
    def __init__(self):
        self.message_queue = []
        self.familiar_registry = {}
        self.debug_mode = False
        self.message_log = []
        
    def register_familiar(self, familiar):
        """Register a familiar for message routing."""
        self.familiar_registry[familiar.name] = familiar
        if self.debug_mode:
            print(f"[MessageRouter] Registered familiar: {familiar.name}")
        
    def unregister_familiar(self, familiar_name: str):
        """Unregister a familiar from message routing."""
        if familiar_name in self.familiar_registry:
            del self.familiar_registry[familiar_name]
            if self.debug_mode:
                print(f"[MessageRouter] Unregistered familiar: {familiar_name}")
        
    def send_message(self, message: FamiliarMessage) -> bool:
        """Route message to appropriate familiar."""
        if self.debug_mode:
            self.message_log.append(message)
            print(f"[MessageRouter] Routing message: {message.id} from {message.sender} to {message.recipient}")
        
        if message.recipient in self.familiar_registry:
            recipient = self.familiar_registry[message.recipient]
            if hasattr(recipient, 'receive_message'):
                try:
                    recipient.receive_message(message)
                    return True
                except Exception as e:
                    if self.debug_mode:
                        print(f"[MessageRouter] Error delivering message: {e}")
                    return False
        
        if self.debug_mode:
            print(f"[MessageRouter] Recipient not found: {message.recipient}")
        return False
        
    def broadcast_message(self, sender: str, msg_type: str, payload: Any):
        """Send message to all registered familiars."""
        if self.debug_mode:
            print(f"[MessageRouter] Broadcasting message from {sender}: {msg_type}")
        
        for name, familiar in self.familiar_registry.items():
            if name != sender:
                msg = FamiliarMessage.create(sender, name, msg_type, payload)
                self.send_message(msg)
    
    def enable_debug(self, enable: bool = True):
        """Enable or disable debug mode."""
        self.debug_mode = enable
        if enable:
            print("[MessageRouter] Debug mode enabled")
        else:
            print("[MessageRouter] Debug mode disabled")
    
    def get_message_log(self) -> list:
        """Get the message log for debugging."""
        return self.message_log.copy()
    
    def clear_message_log(self):
        """Clear the message log."""
        self.message_log.clear()


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def build_message(sender: str, payload: Any, *, category: str = "generic", target: Optional[str] = None) -> Message:
    """Helper to quickly build Message objects."""
    return Message(sender=sender, target=target, category=category, payload=payload)


def is_message(obj: Any) -> bool:
    return isinstance(obj, Message) or (
        isinstance(obj, dict) and {"sender", "category", "payload", "timestamp"}.issubset(obj.keys())
    )


def is_familiar_message(obj: Any) -> bool:
    """Check if object is a FamiliarMessage."""
    return isinstance(obj, FamiliarMessage) or (
        isinstance(obj, dict) and {"id", "sender", "recipient", "message_type", "payload", "timestamp"}.issubset(obj.keys())
    )