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
Grimoire Tag Registry System

Central registry for managing tagged entities, providing fast queries, and enabling
emergent behavior discovery. The registry serves as the single source of truth for
all tagged entities in the system.
"""

from typing import Dict, List, Set, Optional, Any, Callable, Tuple
import threading
import time
from collections import defaultdict

from .tag_system import Tag, TagSet, TagCategory


class TaggedEntity:
    """
    Base class for entities that can be tagged and registered.
    
    Provides foundational functionality for tag management, true name generation,
    and registry integration.
    """
    
    def __init__(self, name: str, entity_type: str, tags: Optional[List[Tag]] = None):
        """
        Initialize tagged entity.
        
        Args:
            name: Human-readable name of the entity
            entity_type: Type classification (archon, spirit, familiar, etc.)
            tags: Optional list of initial tags
        """
        self.name = name
        self.entity_type = entity_type
        self.tags = TagSet(tags or [])
        self.creation_time = time.time()
        self.metadata: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Generate true name after tags are set
        self.true_name = self._generate_true_name()
    
    def _generate_true_name(self) -> str:
        """
        Generate cryptographic true name including tags.
        
        Returns:
            Unique true name for this entity
        """
        import hashlib
        
        content = f"{self.name}:{self.entity_type}:{self.creation_time}"
        
        # Include tag signatures for uniqueness
        tag_signatures = sorted([tag.hash for tag in self.tags.tags.values()])
        content += ":" + ":".join(tag_signatures)
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_tag(self, tag: Tag) -> bool:
        """
        Add a tag to this entity.
        
        Args:
            tag: Tag to add
            
        Returns:
            True if tag was added, False if it already existed
        """
        with self._lock:
            added = self.tags.add_tag(tag)
            if added:
                # Notify registry of tag change
                tag_registry.update_entity_tags(self)
            return added
    
    def remove_tag(self, tag_pattern: str) -> int:
        """
        Remove tags matching a pattern.
        
        Args:
            tag_pattern: Pattern to match for removal
            
        Returns:
            Number of tags removed
        """
        with self._lock:
            removed = self.tags.remove_tag(tag_pattern)
            if removed > 0:
                # Notify registry of tag change
                tag_registry.update_entity_tags(self)
            return removed
    
    def has_tag(self, pattern: str) -> bool:
        """Check if entity has a tag matching the pattern."""
        return self.tags.has_tag(pattern)
    
    def has_capability(self, capability: str) -> bool:
        """Check if entity has a specific capability."""
        return self.tags.has_tag(f"ability:{capability}")
    
    # Mark aliases for mystical terminology
    def mark(self, tag: Tag) -> bool:
        """Alias for add_tag using mystical terminology."""
        return self.add_tag(tag)
    
    def set_mark(self, tag: Tag) -> bool:
        """Alias for add_tag using mystical terminology."""
        return self.add_tag(tag)
    
    def unmark(self, tag_pattern: str) -> int:
        """Alias for remove_tag using mystical terminology."""
        return self.remove_tag(tag_pattern)
    
    def bears_mark(self, pattern: str) -> bool:
        """Alias for has_tag using mystical terminology."""
        return self.has_tag(pattern)
    
    def may(self, capability: str) -> bool:
        """Alias for has_capability using mystical terminology."""
        return self.has_capability(capability)
    
    def can_interact_with(self, other: 'TaggedEntity') -> bool:
        """
        Check if this entity can interact with another.
        
        Args:
            other: Another tagged entity
            
        Returns:
            True if interaction is possible based on tag compatibility
        """
        return self.tags.compatibility_score(other.tags) > 0.3
    
    def get_interaction_score(self, other: 'TaggedEntity') -> float:
        """
        Get detailed interaction score with another entity.
        
        Args:
            other: Another tagged entity
            
        Returns:
            Interaction score between 0.0 and 1.0
        """
        return self.tags.compatibility_score(other.tags)
    
    def get_dominant_characteristics(self) -> Dict[TagCategory, Tag]:
        """Get the dominant tag for each category."""
        return self.tags.get_dominant_characteristics()
    
    def matches_criteria(self, required_tags: List[str], 
                        forbidden_tags: Optional[List[str]] = None) -> bool:
        """
        Check if entity matches search criteria.
        
        Args:
            required_tags: Tags that must be present
            forbidden_tags: Tags that must not be present
            
        Returns:
            True if entity matches all criteria
        """
        # Check required tags
        if not self.tags.matches_all(required_tags):
            return False
        
        # Check forbidden tags
        if forbidden_tags and self.tags.matches_any(forbidden_tags):
            return False
        
        return True
    
    def export_entity_data(self) -> Dict[str, Any]:
        """
        Export entity data for serialization.
        
        Returns:
            Dictionary with entity data
        """
        return {
            "name": self.name,
            "entity_type": self.entity_type,
            "true_name": self.true_name,
            "creation_time": self.creation_time,
            "tags": self.tags.export_tags(),
            "metadata": self.metadata.copy()
        }
    
    def __str__(self) -> str:
        return f"{self.entity_type}({self.name})"
    
    def __repr__(self) -> str:
        return f"TaggedEntity(name='{self.name}', type='{self.entity_type}', tags={len(self.tags)})"


class TagRegistry:
    """
    Central registry for managing tagged entities and providing fast queries.
    
    Maintains indexes for efficient entity discovery and compatibility matching.
    """
    
    def __init__(self):
        """Initialize the tag registry."""
        self.entities: Dict[str, TaggedEntity] = {}  # true_name -> entity
        self.name_index: Dict[str, str] = {}  # name -> true_name
        self.type_index: Dict[str, Set[str]] = defaultdict(set)  # entity_type -> {true_names}
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag_pattern -> {true_names}
        self.category_index: Dict[TagCategory, Set[str]] = defaultdict(set)  # category -> {true_names}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Registry metadata
        self.creation_time = time.time()
        self.last_modified = time.time()
        
        # Query cache for performance
        self._query_cache: Dict[str, Tuple[List[TaggedEntity], float]] = {}
        self._cache_ttl = 60.0  # Cache timeout in seconds
    
    def register_entity(self, entity: TaggedEntity) -> bool:
        """
        Register an entity with the registry.
        
        Args:
            entity: Entity to register
            
        Returns:
            True if entity was registered, False if already exists
        """
        with self._lock:
            if entity.true_name in self.entities:
                return False
            
            # Check for name conflicts
            if entity.name in self.name_index:
                existing_true_name = self.name_index[entity.name]
                if existing_true_name != entity.true_name:
                    # Generate unique name
                    counter = 1
                    original_name = entity.name
                    while entity.name in self.name_index:
                        entity.name = f"{original_name}_{counter}"
                        counter += 1
            
            # Register entity
            self.entities[entity.true_name] = entity
            self.name_index[entity.name] = entity.true_name
            self.type_index[entity.entity_type].add(entity.true_name)
            
            # Index all tags
            self._index_entity_tags(entity)
            
            # Clear query cache
            self._clear_query_cache()
            
            self.last_modified = time.time()
            return True
    
    def unregister_entity(self, identifier: str) -> bool:
        """
        Unregister an entity from the registry.
        
        Args:
            identifier: Entity name or true name
            
        Returns:
            True if entity was found and removed
        """
        with self._lock:
            entity = self.get_entity(identifier)
            if not entity:
                return False
            
            # Remove from all indexes
            del self.entities[entity.true_name]
            del self.name_index[entity.name]
            self.type_index[entity.entity_type].discard(entity.true_name)
            
            self._remove_entity_from_tag_indexes(entity)
            
            # Clear query cache
            self._clear_query_cache()
            
            self.last_modified = time.time()
            return True
    
    def get_entity(self, identifier: str) -> Optional[TaggedEntity]:
        """
        Get an entity by name or true name.
        
        Args:
            identifier: Entity name or true name
            
        Returns:
            Entity if found, None otherwise
        """
        with self._lock:
            # Try as true name first
            if identifier in self.entities:
                return self.entities[identifier]
            
            # Try as name
            if identifier in self.name_index:
                true_name = self.name_index[identifier]
                return self.entities.get(true_name)
            
            return None
    
    def query_by_tags(self, required_tags: List[str], 
                     optional_tags: Optional[List[str]] = None,
                     forbidden_tags: Optional[List[str]] = None,
                     entity_type: Optional[str] = None,
                     max_results: Optional[int] = None) -> List[TaggedEntity]:
        """
        Query entities by tag criteria.
        
        Args:
            required_tags: Tags that must be present
            optional_tags: Tags that boost ranking but aren't required
            forbidden_tags: Tags that disqualify entities
            entity_type: Filter by entity type
            max_results: Maximum number of results to return
            
        Returns:
            List of matching entities, sorted by relevance
        """
        # Create cache key
        cache_key = self._create_query_cache_key(
            required_tags, optional_tags, forbidden_tags, entity_type, max_results
        )
        
        with self._lock:
            # Check cache
            if cache_key in self._query_cache:
                cached_result, timestamp = self._query_cache[cache_key]
                if time.time() - timestamp < self._cache_ttl:
                    return cached_result.copy()
            
            # Find candidate entities
            candidates = self._find_candidate_entities(required_tags, entity_type)
            
            # Filter by criteria
            matching_entities = []
            for entity in candidates:
                if entity.matches_criteria(required_tags, forbidden_tags):
                    matching_entities.append(entity)
            
            # Score by optional tags if provided
            if optional_tags:
                scored_entities = []
                for entity in matching_entities:
                    score = self._calculate_optional_tag_score(entity, optional_tags)
                    scored_entities.append((entity, score))
                
                # Sort by score (descending)
                scored_entities.sort(key=lambda x: x[1], reverse=True)
                matching_entities = [entity for entity, score in scored_entities]
            
            # Apply max results limit
            if max_results:
                matching_entities = matching_entities[:max_results]
            
            # Cache result
            self._query_cache[cache_key] = (matching_entities.copy(), time.time())
            
            return matching_entities
    
    def find_compatible_entities(self, entity: TaggedEntity, 
                               min_compatibility: float = 0.5,
                               max_results: Optional[int] = None) -> List[Tuple[TaggedEntity, float]]:
        """
        Find entities compatible with the given entity.
        
        Args:
            entity: Entity to find compatible matches for
            min_compatibility: Minimum compatibility score required
            max_results: Maximum number of results to return
            
        Returns:
            List of (entity, compatibility_score) tuples, sorted by compatibility
        """
        with self._lock:
            compatible = []
            
            for other in self.entities.values():
                if other.true_name != entity.true_name:
                    score = entity.get_interaction_score(other)
                    if score >= min_compatibility:
                        compatible.append((other, score))
            
            # Sort by compatibility score (descending)
            compatible.sort(key=lambda x: x[1], reverse=True)
            
            # Apply max results limit
            if max_results:
                compatible = compatible[:max_results]
            
            return compatible
    
    def find_entities_by_type(self, entity_type: str) -> List[TaggedEntity]:
        """
        Find all entities of a specific type.
        
        Args:
            entity_type: Type to search for
            
        Returns:
            List of entities of the specified type
        """
        with self._lock:
            if entity_type not in self.type_index:
                return []
            
            return [self.entities[true_name] for true_name in self.type_index[entity_type]]
    
    def find_entities_by_category(self, category: TagCategory) -> List[TaggedEntity]:
        """
        Find all entities that have tags in a specific category.
        
        Args:
            category: Tag category to search for
            
        Returns:
            List of entities with tags in the specified category
        """
        with self._lock:
            if category not in self.category_index:
                return []
            
            return [self.entities[true_name] for true_name in self.category_index[category]]
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about tags in the registry.
        
        Returns:
            Dictionary with tag statistics
        """
        with self._lock:
            stats = {
                "total_entities": len(self.entities),
                "entity_types": dict([(t, len(entities)) for t, entities in self.type_index.items()]),
                "tag_distribution": {},
                "category_distribution": {},
                "most_common_tags": [],
                "categories_represented": len(self.category_index),
                "compatibility_matrix_size": len(self.entities) ** 2
            }
            
            # Count tag usage
            tag_counts = defaultdict(int)
            category_counts = defaultdict(int)
            
            for entity in self.entities.values():
                for tag in entity.tags:
                    tag_counts[tag.full_tag] += 1
                    category_counts[tag.category.value] += 1
            
            stats["tag_distribution"] = dict(tag_counts)
            stats["category_distribution"] = dict(category_counts)
            
            # Most common tags
            most_common = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            stats["most_common_tags"] = most_common
            
            return stats
    
    def suggest_tags_for_entity(self, entity: TaggedEntity, 
                               max_suggestions: int = 5) -> List[Tuple[Tag, float]]:
        """
        Suggest additional tags for an entity based on similar entities.
        
        Args:
            entity: Entity to suggest tags for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of (tag, confidence_score) tuples
        """
        with self._lock:
            # Find similar entities
            similar_entities = self.find_compatible_entities(entity, min_compatibility=0.6)
            
            if not similar_entities:
                return []
            
            # Count tags from similar entities
            tag_counts = defaultdict(float)
            for similar_entity, compatibility in similar_entities:
                for tag in similar_entity.tags:
                    if not entity.has_tag(tag.full_tag):
                        # Weight by compatibility
                        tag_counts[tag] += compatibility
            
            # Sort by weighted count
            suggestions = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Convert to confidence scores
            if suggestions:
                max_score = suggestions[0][1]
                normalized_suggestions = [
                    (tag, score / max_score) for tag, score in suggestions[:max_suggestions]
                ]
                return normalized_suggestions
            
            return []
    
    def update_entity_tags(self, entity: TaggedEntity) -> None:
        """
        Update indexes when an entity's tags change.
        
        Args:
            entity: Entity whose tags have changed
        """
        with self._lock:
            if entity.true_name in self.entities:
                # Remove old tag indexes
                self._remove_entity_from_tag_indexes(entity)
                
                # Re-index with new tags
                self._index_entity_tags(entity)
                
                # Clear query cache
                self._clear_query_cache()
                
                self.last_modified = time.time()
    
    def _find_candidate_entities(self, required_tags: List[str], 
                                entity_type: Optional[str]) -> List[TaggedEntity]:
        """Find candidate entities that might match the query."""
        candidates = None
        
        # Start with entity type filter if provided
        if entity_type:
            if entity_type in self.type_index:
                candidates = set(self.type_index[entity_type])
            else:
                return []
        
        # Intersect with entities having required tags
        for tag_pattern in required_tags:
            matching_entities = self._get_entities_with_tag(tag_pattern)
            if candidates is None:
                candidates = matching_entities
            else:
                candidates = candidates.intersection(matching_entities)
        
        if candidates is None:
            candidates = set(self.entities.keys())
        
        return [self.entities[true_name] for true_name in candidates]
    
    def _get_entities_with_tag(self, tag_pattern: str) -> Set[str]:
        """Get set of entity true names that have a tag matching the pattern."""
        matching = set()
        
        # Check exact matches first
        if tag_pattern in self.tag_index:
            matching.update(self.tag_index[tag_pattern])
        
        # Check pattern matches
        for indexed_pattern, entity_names in self.tag_index.items():
            # Simple pattern matching for now
            if self._patterns_match(tag_pattern, indexed_pattern):
                matching.update(entity_names)
        
        return matching
    
    def _patterns_match(self, query_pattern: str, indexed_pattern: str) -> bool:
        """Check if a query pattern matches an indexed pattern."""
        if query_pattern == indexed_pattern:
            return True
        
        # Handle wildcard patterns
        if ':' in query_pattern:
            query_cat, query_val = query_pattern.split(':', 1)
            if ':' in indexed_pattern:
                indexed_cat, indexed_val = indexed_pattern.split(':', 1)
                return query_cat == indexed_cat and (query_val == '*' or query_val == indexed_val)
        
        return False
    
    def _calculate_optional_tag_score(self, entity: TaggedEntity, 
                                    optional_tags: List[str]) -> float:
        """Calculate score based on optional tags."""
        score = 0.0
        for tag_pattern in optional_tags:
            if entity.has_tag(tag_pattern):
                score += 1.0
        
        return score / len(optional_tags) if optional_tags else 0.0
    
    def _index_entity_tags(self, entity: TaggedEntity) -> None:
        """Index all tags of an entity."""
        for tag in entity.tags:
            # Index by full tag
            self.tag_index[tag.full_tag].add(entity.true_name)
            
            # Index by category
            self.category_index[tag.category].add(entity.true_name)
            
            # Index by category wildcard
            category_wildcard = f"{tag.category.value}:*"
            self.tag_index[category_wildcard].add(entity.true_name)
    
    def _remove_entity_from_tag_indexes(self, entity: TaggedEntity) -> None:
        """Remove entity from all tag indexes."""
        for tag in entity.tags:
            # Remove from full tag index
            self.tag_index[tag.full_tag].discard(entity.true_name)
            if not self.tag_index[tag.full_tag]:
                del self.tag_index[tag.full_tag]
            
            # Remove from category index
            self.category_index[tag.category].discard(entity.true_name)
            if not self.category_index[tag.category]:
                del self.category_index[tag.category]
            
            # Remove from category wildcard index
            category_wildcard = f"{tag.category.value}:*"
            self.tag_index[category_wildcard].discard(entity.true_name)
            if not self.tag_index[category_wildcard]:
                del self.tag_index[category_wildcard]
    
    def _create_query_cache_key(self, required_tags: List[str], 
                               optional_tags: Optional[List[str]],
                               forbidden_tags: Optional[List[str]],
                               entity_type: Optional[str],
                               max_results: Optional[int]) -> str:
        """Create a cache key for a query."""
        key_parts = [
            "req:" + ",".join(sorted(required_tags)),
            "opt:" + ",".join(sorted(optional_tags or [])),
            "forb:" + ",".join(sorted(forbidden_tags or [])),
            "type:" + (entity_type or ""),
            "max:" + str(max_results or "")
        ]
        return "|".join(key_parts)
    
    def _clear_query_cache(self) -> None:
        """Clear the query cache."""
        self._query_cache.clear()
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export the entire registry for backup/transfer.
        
        Returns:
            Dictionary with registry data
        """
        with self._lock:
            return {
                "metadata": {
                    "creation_time": self.creation_time,
                    "last_modified": self.last_modified,
                    "export_time": time.time()
                },
                "entities": {
                    true_name: entity.export_entity_data()
                    for true_name, entity in self.entities.items()
                },
                "statistics": self.get_tag_statistics()
            }
    
    def import_registry(self, registry_data: Dict[str, Any]) -> int:
        """
        Import registry data.
        
        Args:
            registry_data: Registry data to import
            
        Returns:
            Number of entities successfully imported
        """
        imported = 0
        entities_data = registry_data.get("entities", {})
        
        for true_name, entity_data in entities_data.items():
            try:
                # Create entity from data
                entity = TaggedEntity(
                    entity_data["name"],
                    entity_data["entity_type"]
                )
                
                # Import tags
                entity.tags.import_tags(entity_data.get("tags", []))
                entity.metadata = entity_data.get("metadata", {})
                
                # Register entity
                if self.register_entity(entity):
                    imported += 1
                    
            except (KeyError, ValueError):
                # Skip invalid entity data
                continue
        
        return imported
    
    def clear_registry(self) -> None:
        """Clear all entities from the registry."""
        with self._lock:
            self.entities.clear()
            self.name_index.clear()
            self.type_index.clear()
            self.tag_index.clear()
            self.category_index.clear()
            self._query_cache.clear()
            self.last_modified = time.time()


# Global registry instance
tag_registry = TagRegistry()


# Convenience functions for common operations
def register_entity(entity: TaggedEntity) -> bool:
    """Register an entity with the global registry."""
    return tag_registry.register_entity(entity)


def get_entity(identifier: str) -> Optional[TaggedEntity]:
    """Get an entity from the global registry."""
    return tag_registry.get_entity(identifier)


def query_by_tags(required_tags: List[str], **kwargs) -> List[TaggedEntity]:
    """Query entities by tags using the global registry."""
    return tag_registry.query_by_tags(required_tags, **kwargs)


def find_compatible(entity: TaggedEntity, **kwargs) -> List[Tuple[TaggedEntity, float]]:
    """Find compatible entities using the global registry."""
    return tag_registry.find_compatible_entities(entity, **kwargs)


def get_entities_by_type(entity_type: str) -> List[TaggedEntity]:
    """Get all entities of a specific type."""
    return tag_registry.find_entities_by_type(entity_type)


def suggest_tags(entity: TaggedEntity, **kwargs) -> List[Tuple[Tag, float]]:
    """Suggest tags for an entity using the global registry."""
    return tag_registry.suggest_tags_for_entity(entity, **kwargs)


def get_registry_stats() -> Dict[str, Any]:
    """Get statistics from the global registry."""
    return tag_registry.get_tag_statistics()


# =============================================================================
# MARK SYSTEM ALIASES - Mystical Terminology
# =============================================================================

# Class aliases
MarkedEntity = TaggedEntity
MarkRegistry = TagRegistry

# Global registry alias
mark_registry = tag_registry

# Function aliases for mystical terminology
def seek_mark(required_marks: List[str], **kwargs) -> List[TaggedEntity]:
    """Alias for query_by_tags using mystical terminology."""
    return query_by_tags(required_marks, **kwargs)

def seek_match(entity: TaggedEntity, **kwargs) -> List[Tuple[TaggedEntity, float]]:
    """Alias for find_compatible using mystical terminology."""
    return find_compatible(entity, **kwargs)

def seek_matches(entity: TaggedEntity, **kwargs) -> List[Tuple[TaggedEntity, float]]:
    """Alias for find_compatible_entities using mystical terminology."""
    return find_compatible(entity, **kwargs)

def gather_kind(entity_type: str) -> List[TaggedEntity]:
    """Alias for get_entities_by_type using mystical terminology."""
    return get_entities_by_type(entity_type)

def how_matched(entity1: TaggedEntity, entity2: TaggedEntity) -> float:
    """Check compatibility between two entities using mystical terminology."""
    return entity1.get_interaction_score(entity2)

def suggest_marks(entity: TaggedEntity, **kwargs) -> List[Tuple[Tag, float]]:
    """Alias for suggest_tags using mystical terminology."""
    return suggest_tags(entity, **kwargs)

def has_power(entity: TaggedEntity) -> List[str]:
    """Get entity capabilities using mystical terminology."""
    capabilities = []
    for tag in entity.tags:
        if tag.category.value == "ability":
            capabilities.append(tag.value)
    return capabilities