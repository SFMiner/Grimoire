"""
Tome Container Implementation

Tome represents an array/list container - ordered, mutable sequence.
"""

from .base import GrimoireContainer
from typing import Any, List, Optional, Union


class Tome(GrimoireContainer):
    """Array/List container - ordered, mutable sequence"""
    
    def __init__(self, initial_data: Optional[List] = None):
        super().__init__()
        self._elements: List[Any] = initial_data.copy() if initial_data else []
    
    def inscribe(self, *items) -> None:
        """Add items to end of tome"""
        self._elements.extend(items)
    
    def inscribe_at(self, index: int, item: Any) -> None:
        """Insert item at specific index"""
        if index < 0 or index > len(self._elements):
            raise IndexError(f"Tome index {index} out of bounds")
        self._elements.insert(index, item)
    
    def extract(self, index: int) -> Any:
        """Remove and return item at index"""
        if index < 0 or index >= len(self._elements):
            raise IndexError(f"Tome index {index} out of bounds")
        return self._elements.pop(index)
    
    def extract_last(self) -> Any:
        """Remove and return last item"""
        if not self._elements:
            raise IndexError("Cannot extract from empty tome")
        return self._elements.pop()
    
    def seek(self, value: Any) -> Optional[int]:
        """Find first index of value, None if not found"""
        try:
            return self._elements.index(value)
        except ValueError:
            return None
    
    def seek_all(self, value: Any) -> List[int]:
        """Find all indices of value"""
        return [i for i, x in enumerate(self._elements) if x == value]
    
    def manifest(self, initial_data: Optional[List] = None) -> None:
        """Initialize with data"""
        self._elements = initial_data.copy() if initial_data else []
    
    def enumerate_contents(self):
        """Iterate over elements"""
        return iter(self._elements)
    
    def enumerate(self):
        """Return the number of elements"""
        return len(self._elements)
    
    def __getitem__(self, key: Union[int, slice]) -> Any:
        return self._elements[key]
    
    def __setitem__(self, key: Union[int, slice], value: Any) -> None:
        self._elements[key] = value
    
    def __str__(self) -> str:
        return f"$TOME({self._elements})"
    
    def __repr__(self) -> str:
        return f"Tome({self._elements})"
    
    # Tome-specific methods
    def reverse_order(self) -> None:
        """Reverse the tome in place"""
        self._elements.reverse()
    
    def sort_contents(self, key=None, reverse=False) -> None:
        """Sort the tome in place"""
        self._elements.sort(key=key, reverse=reverse)
    
    def slice_tome(self, start: Optional[int] = None, end: Optional[int] = None, step: Optional[int] = None) -> 'Tome':
        """Return a new tome with sliced contents"""
        sliced_data = self._elements[start:end:step]
        return Tome(sliced_data)