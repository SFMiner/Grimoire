"""
Grimoire Container Implementation

Grimoire represents a dictionary/map container - key-value associations.
"""

from .base import GrimoireContainer
from typing import Any, Dict, Iterator, Optional, Tuple, Union


class Grimoire(GrimoireContainer):
    """Dictionary/Map container - key-value associations"""
    
    def __init__(self, initial_data: Optional[Dict] = None):
        super().__init__()
        self._elements: Dict[Any, Any] = initial_data.copy() if initial_data else {}
    
    def inscribe(self, key: Any, value: Any) -> None:
        """Add or update key-value pair"""
        self._elements[key] = value
    
    def inscribe_many(self, pairs: Dict[Any, Any]) -> None:
        """Add multiple key-value pairs"""
        self._elements.update(pairs)
    
    def extract(self, key: Any) -> Any:
        """Remove and return value for key"""
        if key not in self._elements:
            raise KeyError(f"Key '{key}' not found in grimoire")
        return self._elements.pop(key)
    
    def extract_or_default(self, key: Any, default: Any = None) -> Any:
        """Remove and return value, or default if key not found"""
        return self._elements.pop(key, default)
    
    def seek(self, key: Any) -> Any:
        """Get value for key (doesn't remove)"""
        return self._elements.get(key)
    
    def seek_or_default(self, key: Any, default: Any = None) -> Any:
        """Get value for key or return default"""
        return self._elements.get(key, default)
    
    def seek_by_value(self, value: Any) -> Optional[Any]:
        """Find first key with given value"""
        for k, v in self._elements.items():
            if v == value:
                return k
        return None
    
    def manifest(self, initial_data: Optional[Dict] = None) -> None:
        """Initialize with data"""
        self._elements = initial_data.copy() if initial_data else {}
    
    def enumerate_contents(self) -> Iterator[Tuple[Any, Any]]:
        """Iterate over key-value pairs"""
        return iter(self._elements.items())
    
    def enumerate_keys(self) -> Iterator[Any]:
        """Iterate over keys"""
        return iter(self._elements.keys())
    
    def enumerate_values(self) -> Iterator[Any]:
        """Iterate over values"""
        return iter(self._elements.values())
    
    def contains_key(self, key: Any) -> bool:
        """Check if key exists"""
        return key in self._elements
    
    def contains_value(self, value: Any) -> bool:
        """Check if value exists"""
        return value in self._elements.values()
    
    def __getitem__(self, key: Any) -> Any:
        return self._elements[key]
    
    def __setitem__(self, key: Any, value: Any) -> None:
        self._elements[key] = value
    
    def __contains__(self, key: Any) -> bool:
        return key in self._elements
    
    def __str__(self) -> str:
        pairs = [f"{k}: {v}" for k, v in self._elements.items()]
        return f"$GRIMOIRE({{{', '.join(pairs)}}})"
    
    def __repr__(self) -> str:
        return f"Grimoire({self._elements})"