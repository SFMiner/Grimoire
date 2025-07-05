"""
Base Container Classes for Grimoire

This module provides the abstract base class for all Grimoire containers.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional


class GrimoireContainer(ABC):
    """Base class for all Grimoire containers"""
    
    def __init__(self):
        self._elements = None
        self._metadata = {}
    
    @abstractmethod
    def inscribe(self, *args) -> None:
        """Add element(s) to container"""
        pass
    
    @abstractmethod
    def extract(self, key) -> Any:
        """Remove and return element"""
        pass
    
    @abstractmethod
    def seek(self, value) -> Any:
        """Find element in container"""
        pass
    
    @abstractmethod
    def manifest(self, initial_data=None) -> None:
        """Initialize container with data"""
        pass
    
    @abstractmethod
    def enumerate_contents(self) -> Iterator:
        """Iterate over container contents"""
        pass
    
    def __len__(self) -> int:
        return len(self._elements) if self._elements else 0
    
    def __bool__(self) -> bool:
        return len(self) > 0