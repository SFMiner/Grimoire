"""
Codex Container Implementation

Codex represents a set container - unique, unordered elements.
"""

from .base import GrimoireContainer
from typing import Any, Set, Optional, Iterator


class Codex(GrimoireContainer):
    """Set container - unique, unordered elements"""
    
    def __init__(self, initial_data: Optional[Set] = None):
        super().__init__()
        self._elements: Set[Any] = set(initial_data) if initial_data else set()
    
    def inscribe(self, *items) -> None:
        """Add items to codex (duplicates ignored)"""
        for item in items:
            self._elements.add(item)
    
    def extract(self, item: Any) -> Any:
        """Remove specific item from codex"""
        if item not in self._elements:
            raise KeyError(f"Item '{item}' not found in codex")
        self._elements.remove(item)
        return item
    
    def extract_any(self) -> Any:
        """Remove and return arbitrary item"""
        if not self._elements:
            raise KeyError("Cannot extract from empty codex")
        return self._elements.pop()
    
    def seek(self, item: Any) -> bool:
        """Check if item exists in codex"""
        return item in self._elements
    
    def manifest(self, initial_data: Optional[Set] = None) -> None:
        """Initialize with data"""
        self._elements = set(initial_data) if initial_data else set()
    
    def enumerate_contents(self) -> Iterator[Any]:
        """Iterate over elements"""
        return iter(self._elements)
    
    def __contains__(self, item: Any) -> bool:
        return item in self._elements
    
    def __str__(self) -> str:
        return f"$CODEX({{{', '.join(map(str, self._elements))}}})"
    
    def __repr__(self) -> str:
        return f"Codex({self._elements})"
    
    # Set operations
    def unite_with(self, other: 'Codex') -> 'Codex':
        """Union operation"""
        return Codex(self._elements | other._elements)
    
    def intersect_with(self, other: 'Codex') -> 'Codex':
        """Intersection operation"""
        return Codex(self._elements & other._elements)
    
    def exclude(self, other: 'Codex') -> 'Codex':
        """Difference operation"""
        return Codex(self._elements - other._elements)