"""
Vault Container Implementation

Vault represents a tuple container - immutable sequence.
"""

from .base import GrimoireContainer
from typing import Any, Tuple, Optional, Iterator


class Vault(GrimoireContainer):
    """Tuple container - immutable sequence"""
    
    def __init__(self, initial_data: Optional[Tuple] = None):
        super().__init__()
        self._elements: Tuple[Any, ...] = tuple(initial_data) if initial_data else ()
    
    def inscribe(self, *items) -> None:
        """Add items to vault (creates new vault)"""
        self._elements = self._elements + tuple(items)
    
    def extract(self, index: int) -> Any:
        """Cannot extract from immutable vault"""
        raise RuntimeError("Cannot extract from immutable vault")
    
    def seek(self, value: Any) -> Optional[int]:
        """Find first index of value, None if not found"""
        try:
            return self._elements.index(value)
        except ValueError:
            return None
    
    def manifest(self, initial_data: Optional[Tuple] = None) -> None:
        """Initialize with data"""
        self._elements = tuple(initial_data) if initial_data else ()
    
    def enumerate_contents(self) -> Iterator[Any]:
        """Iterate over elements"""
        return iter(self._elements)
    
    def __getitem__(self, index: int) -> Any:
        return self._elements[index]
    
    def __str__(self) -> str:
        return f"$VAULT({self._elements})"
    
    def __repr__(self) -> str:
        return f"Vault({self._elements})"