"""
Chronicle Container Implementation

Chronicle represents an ordered collection container.
"""

from .base import GrimoireContainer
from typing import Any, List, Optional, Iterator


class Chronicle(GrimoireContainer):
    """Ordered collection container - maintains insertion order"""
    
    def __init__(self, initial_data: Optional[List] = None):
        super().__init__()
        self._elements: List[Any] = initial_data.copy() if initial_data else []
    
    def inscribe(self, *items) -> None:
        """Add items to end of chronicle"""
        self._elements.extend(items)
    
    def extract(self, index: int) -> Any:
        """Remove and return item at index"""
        if index < 0 or index >= len(self._elements):
            raise IndexError(f"Chronicle index {index} out of bounds")
        return self._elements.pop(index)
    
    def seek(self, value: Any) -> Optional[int]:
        """Find first index of value, None if not found"""
        try:
            return self._elements.index(value)
        except ValueError:
            return None
    
    def manifest(self, initial_data: Optional[List] = None) -> None:
        """Initialize with data"""
        self._elements = initial_data.copy() if initial_data else []
    
    def enumerate_contents(self) -> Iterator[Any]:
        """Iterate over elements"""
        return iter(self._elements)
    
    def __getitem__(self, index: int) -> Any:
        return self._elements[index]
    
    def __str__(self) -> str:
        return f"$CHRONICLE({self._elements})"
    
    def __repr__(self) -> str:
        return f"Chronicle({self._elements})"