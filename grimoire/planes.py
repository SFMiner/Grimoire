#!/usr/bin/env python3
"""
Grimoire Planar System - Multi-dimensional Program Space

This module implements the planar system for Grimoire, allowing programs to
exist across multiple isolated execution contexts (planes) with controlled
inter-plane communication through portals.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import copy
from .sockets import Socket


class PlaneType(Enum):
    """Types of planes with different characteristics."""
    MATERIAL = auto()    # Normal execution plane
    ETHEREAL = auto()    # Reduced memory/computation plane  
    ASTRAL = auto()      # High-level coordination plane
    SHADOW = auto()      # Isolated/sandbox plane
    ELEMENTAL = auto()   # Specialized computation plane


@dataclass
class PlaneProperties:
    """Configuration properties for a plane."""
    plane_type: PlaneType = PlaneType.MATERIAL
    memory_limit: Optional[int] = None  # Max memory usage
    time_dilation: float = 1.0  # Execution speed modifier
    isolation_level: int = 1    # 0=none, 1=data, 2=complete
    persistent: bool = True     # Whether plane survives shifts
    auto_cleanup: bool = False  # Clean up when empty


@dataclass 
class PlaneContext:
    """Execution context for a single plane."""
    name: str
    properties: PlaneProperties
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    familiars: Dict[str, Any] = field(default_factory=dict)
    sockets: Dict[str, Socket] = field(default_factory=dict)
    portals: Dict[str, 'Portal'] = field(default_factory=dict)
    active: bool = True
    creation_time: float = field(default_factory=lambda: __import__('time').time())
    
    def copy_environment(self) -> Dict[str, Any]:
        """Create a copy of the current environment."""
        return {
            'variables': copy.deepcopy(self.variables),
            'functions': copy.deepcopy(self.functions),
            'familiars': copy.deepcopy(self.familiars)
        }
    
    def restore_environment(self, env: Dict[str, Any]) -> None:
        """Restore environment from a copy."""
        self.variables = env.get('variables', {})
        self.functions = env.get('functions', {})
        self.familiars = env.get('familiars', {})


@dataclass
class Portal:
    """Inter-plane communication portal."""
    source_plane: str
    target_plane: str
    target_function: Optional[str] = None
    bidirectional: bool = False
    access_filter: Optional[Callable] = None
    message_transform: Optional[Callable] = None
    
    def can_access(self, data: Any) -> bool:
        """Check if data can pass through portal."""
        if self.access_filter:
            return self.access_filter(data)
        return True
    
    def transform_message(self, data: Any) -> Any:
        """Transform data passing through portal."""
        if self.message_transform:
            return self.message_transform(data)
        return data


class PlaneManager:
    """Manages multiple execution planes and plane switching."""
    
    def __init__(self):
        self.planes: Dict[str, PlaneContext] = {}
        self.current_plane: Optional[str] = None
        self.plane_stack: List[str] = []  # For nested plane calls
        self.global_portals: Dict[str, Portal] = {}
        
        # Create default material plane
        self.create_plane("material", PlaneProperties(PlaneType.MATERIAL))
        self.current_plane = "material"
    
    def create_plane(self, name: str, properties: PlaneProperties) -> PlaneContext:
        """Create a new plane with given properties."""
        if name in self.planes:
            raise ValueError(f"Plane '{name}' already exists")
        
        plane = PlaneContext(name, properties)
        self.planes[name] = plane
        return plane
    
    def get_plane(self, name: str) -> Optional[PlaneContext]:
        """Get plane by name."""
        return self.planes.get(name)
    
    def get_current_plane(self) -> Optional[PlaneContext]:
        """Get the currently active plane."""
        if self.current_plane:
            return self.planes.get(self.current_plane)
        return None
    
    def shift_to_plane(self, target_plane: str, save_context: bool = True) -> bool:
        """Shift execution to a different plane."""
        if target_plane not in self.planes:
            raise ValueError(f"Plane '{target_plane}' does not exist")
        
        # Save current context if requested
        if save_context and self.current_plane:
            self.plane_stack.append(self.current_plane)
        
        # Switch to target plane
        old_plane = self.current_plane
        self.current_plane = target_plane
        
        # Apply time dilation effect
        current = self.get_current_plane()
        if current and current.properties.time_dilation != 1.0:
            # Time dilation would be implemented at runtime level
            pass
        
        return True
    
    def shift_back(self) -> bool:
        """Return to previous plane in the stack."""
        if not self.plane_stack:
            return False
        
        previous_plane = self.plane_stack.pop()
        self.current_plane = previous_plane
        return True
    
    def create_portal(self, portal_id: str, source: str, target: str, 
                     target_function: Optional[str] = None,
                     bidirectional: bool = False) -> Portal:
        """Create a portal between two planes."""
        if source not in self.planes:
            raise ValueError(f"Source plane '{source}' does not exist")
        if target not in self.planes:
            raise ValueError(f"Target plane '{target}' does not exist")
        
        portal = Portal(source, target, target_function, bidirectional)
        self.global_portals[portal_id] = portal
        
        # Add portal to source plane
        self.planes[source].portals[portal_id] = portal
        
        # Add reverse portal if bidirectional
        if bidirectional:
            reverse_portal = Portal(target, source, None, False)
            reverse_id = f"{portal_id}_reverse"
            self.global_portals[reverse_id] = reverse_portal
            self.planes[target].portals[reverse_id] = reverse_portal
        
        return portal
    
    def portal_call(self, portal_id: str, function_name: Optional[str] = None, 
                   args: Optional[List[Any]] = None) -> Any:
        """Call a function through a portal."""
        if portal_id not in self.global_portals:
            raise ValueError(f"Portal '{portal_id}' does not exist")
        
        portal = self.global_portals[portal_id]
        target_plane = self.get_plane(portal.target_plane)
        
        if not target_plane:
            raise RuntimeError(f"Target plane '{portal.target_plane}' not found")
        
        # Determine function to call
        func_name = function_name or portal.target_function
        if not func_name:
            raise ValueError("No function specified for portal call")
        
        # Check access permissions
        safe_args = args or []
        call_data = {'function': func_name, 'args': safe_args}
        if not portal.can_access(call_data):
            raise PermissionError(f"Access denied through portal '{portal_id}'")
        
        # Transform the call data
        transformed_data = portal.transform_message(call_data)
        
        # Save current context and shift to target plane
        original_plane = self.current_plane
        self.shift_to_plane(portal.target_plane, save_context=True)
        
        try:
            # Execute function in target plane
            if func_name in target_plane.functions:
                func = target_plane.functions[func_name]
                result = func(*transformed_data['args'])
                
                # Transform result back
                return portal.transform_message(result)
            else:
                raise NameError(f"Function '{func_name}' not found in plane '{portal.target_plane}'")
        
        finally:
            # Always return to original plane
            self.shift_back()
    
    def isolate_plane(self, plane_name: str, isolation_level: int = 2) -> None:
        """Increase isolation level of a plane."""
        plane = self.get_plane(plane_name)
        if plane:
            plane.properties.isolation_level = isolation_level
    
    def destroy_plane(self, plane_name: str, force: bool = False) -> bool:
        """Destroy a plane and clean up resources."""
        if plane_name == "material" and not force:
            raise ValueError("Cannot destroy material plane without force=True")
        
        if plane_name not in self.planes:
            return False
        
        plane = self.planes[plane_name]
        
        # Clean up sockets
        for socket in plane.sockets.values():
            # Disconnect from all connected sockets
            for connection in list(socket.connections):
                socket.disconnect_from(connection)
        
        # Remove portals
        portals_to_remove = []
        for portal_id, portal in self.global_portals.items():
            if portal.source_plane == plane_name or portal.target_plane == plane_name:
                portals_to_remove.append(portal_id)
        
        for portal_id in portals_to_remove:
            del self.global_portals[portal_id]
        
        # Remove plane
        del self.planes[plane_name]
        
        # Switch to material plane if current plane was destroyed
        if self.current_plane == plane_name:
            self.current_plane = "material"
        
        return True
    
    def list_planes(self) -> List[str]:
        """List all available planes."""
        return list(self.planes.keys())
    
    def get_plane_info(self, plane_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plane."""
        plane = self.get_plane(plane_name)
        if not plane:
            return None
        
        return {
            'name': plane.name,
            'type': plane.properties.plane_type.name,
            'active': plane.active,
            'variables': len(plane.variables),
            'functions': len(plane.functions),
            'familiars': len(plane.familiars),
            'sockets': len(plane.sockets),
            'portals': len(plane.portals),
            'memory_limit': plane.properties.memory_limit,
            'time_dilation': plane.properties.time_dilation,
            'isolation_level': plane.properties.isolation_level,
            'creation_time': plane.creation_time
        }


# Global plane manager instance
PLANE_MANAGER = PlaneManager()


def get_plane_manager() -> PlaneManager:
    """Get the global plane manager instance."""
    return PLANE_MANAGER


def current_plane() -> Optional[PlaneContext]:
    """Get the current plane context."""
    return PLANE_MANAGER.get_current_plane()


def shift_to(plane_name: str) -> bool:
    """Convenience function to shift to a plane."""
    return PLANE_MANAGER.shift_to_plane(plane_name)


def create_portal(source: str, target: str, function: Optional[str] = None) -> Portal:
    """Convenience function to create a portal."""
    portal_id = f"{source}_to_{target}"
    return PLANE_MANAGER.create_portal(portal_id, source, target, function)