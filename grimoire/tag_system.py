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
Grimoire Tag System - Core Infrastructure

This module implements the foundational tag system that enables flexible entity
identification, categorization, and emergent behavior in the Grimoire programming
language. Tags replace hard-coded entity types with dynamic, discoverable attributes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
import hashlib
import time
import threading
from enum import Enum


class TagCategory(Enum):
    """Predefined tag categories for consistent entity classification."""
    DOMAIN = "domain"           # Primary operational area: combat, economy, support
    ROLE = "role"              # Hierarchical position: leader, support, scout
    ABILITY = "ability"        # Capabilities: healing, damage, stealth, trade
    TYPE = "type"              # Entity classification: archon, spirit, familiar
    STATUS = "status"          # Current state: active, idle, combat, wounded
    PERMISSION = "permission"   # Granted actions: heal, attack, trade, command
    RESOURCE = "resource"      # Resource types: mana, health, gold, materials
    BEHAVIOR = "behavior"      # Behavioral traits: aggressive, defensive, neutral
    SPECIALTY = "specialty"    # Specialized skills: coordination, tactics, logistics
    PRIORITY = "priority"      # Importance levels: critical, high, normal, low


@dataclass
class Tag:
    """
    Immutable tag representing a single categorized attribute of an entity.
    
    Tags use a category:value format and include metadata for advanced functionality.
    """
    category: TagCategory
    value: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # For hierarchical tag importance (0 = highest)
    
    def __post_init__(self):
        """Initialize computed fields after dataclass creation."""
        self.full_tag = f"{self.category.value}:{self.value}"
        self.hash = hashlib.sha256(self.full_tag.encode()).hexdigest()[:16]
        self._lock = threading.Lock()
    
    def matches(self, pattern: str) -> bool:
        """
        Check if tag matches a pattern.
        
        Args:
            pattern: Pattern to match against. Supports:
                    - Exact match: "domain:combat"
                    - Category wildcard: "domain:*"
                    - Category only: "domain"
        
        Returns:
            True if tag matches the pattern
        """
        if ':' not in pattern:
            # Category-only match
            return self.category.value == pattern
        
        cat, val = pattern.split(':', 1)
        return (self.category.value == cat and 
                (val == '*' or self.value == val))
    
    def is_compatible_with(self, other: 'Tag') -> bool:
        """
        Check if this tag is compatible with another tag.
        
        Args:
            other: Another tag to check compatibility with
            
        Returns:
            True if tags are compatible
        """
        if self.category != other.category:
            return self._cross_category_compatibility(other)
        
        return self._same_category_compatibility(other)
    
    def _cross_category_compatibility(self, other: 'Tag') -> bool:
        """Check compatibility between different tag categories."""
        compatibility_rules = {
            # Role-Ability compatibility
            (TagCategory.ROLE, "leader", TagCategory.ABILITY, "command"): True,
            (TagCategory.ROLE, "support", TagCategory.ABILITY, "healing"): True,
            (TagCategory.ROLE, "scout", TagCategory.ABILITY, "stealth"): True,
            
            # Domain-Behavior compatibility
            (TagCategory.DOMAIN, "combat", TagCategory.BEHAVIOR, "aggressive"): True,
            (TagCategory.DOMAIN, "support", TagCategory.BEHAVIOR, "defensive"): True,
            (TagCategory.DOMAIN, "economy", TagCategory.BEHAVIOR, "neutral"): True,
            
            # Ability-Permission compatibility
            (TagCategory.ABILITY, "healing", TagCategory.PERMISSION, "heal"): True,
            (TagCategory.ABILITY, "damage", TagCategory.PERMISSION, "attack"): True,
            (TagCategory.ABILITY, "stealth", TagCategory.PERMISSION, "scout"): True,
        }
        
        key1 = (self.category, self.value, other.category, other.value)
        key2 = (other.category, other.value, self.category, self.value)
        
        return compatibility_rules.get(key1, compatibility_rules.get(key2, True))
    
    def _same_category_compatibility(self, other: 'Tag') -> bool:
        """Check compatibility within the same category."""
        incompatible_pairs = {
            TagCategory.BEHAVIOR: [("aggressive", "defensive"), ("active", "idle")],
            TagCategory.STATUS: [("active", "idle"), ("combat", "peaceful")],
            TagCategory.DOMAIN: [],  # Most domains can coexist
        }
        
        if self.category in incompatible_pairs:
            for pair in incompatible_pairs[self.category]:
                if (self.value, other.value) in [pair, tuple(reversed(pair))]:
                    return False
        
        return True
    
    def get_semantic_distance(self, other: 'Tag') -> float:
        """
        Calculate semantic distance between tags (0.0 = identical, 1.0 = completely different).
        
        Args:
            other: Another tag to compare with
            
        Returns:
            Semantic distance as float between 0.0 and 1.0
        """
        if self.category != other.category:
            return 0.8  # Different categories are quite distant
        
        if self.value == other.value:
            return 0.0  # Identical tags
        
        # Category-specific distance calculations
        semantic_groups = {
            TagCategory.DOMAIN: {
                "combat": ["military", "warfare", "battle"],
                "support": ["healing", "assistance", "aid"],
                "economy": ["trade", "commerce", "resources"]
            },
            TagCategory.BEHAVIOR: {
                "aggressive": ["hostile", "offensive", "attacking"],
                "defensive": ["protective", "cautious", "guarding"],
                "neutral": ["passive", "balanced", "moderate"]
            }
        }
        
        if self.category in semantic_groups:
            groups = semantic_groups[self.category]
            self_group = None
            other_group = None
            
            for group_key, synonyms in groups.items():
                if self.value == group_key or self.value in synonyms:
                    self_group = group_key
                if other.value == group_key or other.value in synonyms:
                    other_group = group_key
            
            if self_group and other_group:
                return 0.3 if self_group == other_group else 0.6
        
        return 0.5  # Default distance for same category, different values
    
    def __str__(self) -> str:
        return self.full_tag
    
    def __repr__(self) -> str:
        return f"Tag({self.category.value}:{self.value})"
    
    def __hash__(self) -> int:
        return hash(self.full_tag)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return False
        return self.full_tag == other.full_tag


class TagSet:
    """
    Thread-safe collection of tags with advanced querying and compatibility features.
    
    Provides efficient operations for tag management, pattern matching, and
    compatibility scoring between entities.
    """
    
    def __init__(self, tags: Optional[List[Tag]] = None):
        """
        Initialize tag set with optional list of tags.
        
        Args:
            tags: Optional list of tags to initialize with
        """
        self.tags: Dict[str, Tag] = {}
        self._category_index: Dict[TagCategory, Set[str]] = {}
        self._lock = threading.RLock()
        
        if tags:
            for tag in tags:
                self.add_tag(tag)
    
    def add_tag(self, tag: Tag) -> bool:
        """
        Add a tag to the set.
        
        Args:
            tag: Tag to add
            
        Returns:
            True if tag was added, False if it already existed
        """
        with self._lock:
            if tag.full_tag in self.tags:
                return False
            
            self.tags[tag.full_tag] = tag
            self._update_category_index(tag, add=True)
            return True
    
    def remove_tag(self, tag_pattern: str) -> int:
        """
        Remove tags matching a pattern.
        
        Args:
            tag_pattern: Pattern to match for removal
            
        Returns:
            Number of tags removed
        """
        with self._lock:
            to_remove = []
            for tag_key, tag in self.tags.items():
                if tag.matches(tag_pattern):
                    to_remove.append(tag_key)
            
            for tag_key in to_remove:
                tag = self.tags[tag_key]
                del self.tags[tag_key]
                self._update_category_index(tag, add=False)
            
            return len(to_remove)
    
    def has_tag(self, pattern: str) -> bool:
        """
        Check if any tag in the set matches the pattern.
        
        Args:
            pattern: Pattern to search for
            
        Returns:
            True if any tag matches the pattern
        """
        with self._lock:
            return any(tag.matches(pattern) for tag in self.tags.values())
    
    def get_tags_by_category(self, category: TagCategory) -> List[Tag]:
        """
        Get all tags in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tags in the specified category
        """
        with self._lock:
            if category not in self._category_index:
                return []
            
            return [self.tags[tag_key] for tag_key in self._category_index[category]]
    
    def get_tags_by_pattern(self, pattern: str) -> List[Tag]:
        """
        Get all tags matching a pattern.
        
        Args:
            pattern: Pattern to match
            
        Returns:
            List of matching tags
        """
        with self._lock:
            return [tag for tag in self.tags.values() if tag.matches(pattern)]
    
    def matches_all(self, patterns: List[str]) -> bool:
        """
        Check if the tag set matches all provided patterns.
        
        Args:
            patterns: List of patterns that must all match
            
        Returns:
            True if all patterns are matched
        """
        with self._lock:
            return all(self.has_tag(pattern) for pattern in patterns)
    
    def matches_any(self, patterns: List[str]) -> bool:
        """
        Check if the tag set matches any of the provided patterns.
        
        Args:
            patterns: List of patterns where at least one must match
            
        Returns:
            True if any pattern is matched
        """
        with self._lock:
            return any(self.has_tag(pattern) for pattern in patterns)
    
    def compatibility_score(self, other: 'TagSet') -> float:
        """
        Calculate compatibility score with another tag set.
        
        Args:
            other: Another tag set to compare with
            
        Returns:
            Compatibility score between 0.0 and 1.0
        """
        with self._lock:
            if not self.tags or not other.tags:
                return 0.0
            
            total_score = 0.0
            comparison_count = 0
            
            # Compare tags across categories for comprehensive compatibility
            for my_tag in self.tags.values():
                for other_tag in other.tags.values():
                    if my_tag.is_compatible_with(other_tag):
                        # Weight by semantic similarity
                        distance = my_tag.get_semantic_distance(other_tag)
                        similarity = 1.0 - distance
                        total_score += similarity
                    comparison_count += 1
            
            if comparison_count == 0:
                return 0.0
            
            # Normalize score
            base_score = total_score / comparison_count
            
            # Bonus for complementary tag categories
            complementary_bonus = self._calculate_complementary_bonus(other)
            
            # Final score with diminishing returns
            final_score = base_score + (complementary_bonus * 0.3)
            return min(final_score, 1.0)
    
    def _calculate_complementary_bonus(self, other: 'TagSet') -> float:
        """Calculate bonus score for complementary tag combinations."""
        complementary_pairs = [
            (TagCategory.ABILITY, "healing", TagCategory.STATUS, "wounded"),
            (TagCategory.ABILITY, "damage", TagCategory.TYPE, "enemy"),
            (TagCategory.ROLE, "leader", TagCategory.ROLE, "support"),
            (TagCategory.DOMAIN, "combat", TagCategory.DOMAIN, "support"),
        ]
        
        bonus = 0.0
        for cat1, val1, cat2, val2 in complementary_pairs:
            my_has_first = any(tag.category == cat1 and tag.value == val1 
                             for tag in self.tags.values())
            other_has_second = any(tag.category == cat2 and tag.value == val2 
                                 for tag in other.tags.values())
            
            if my_has_first and other_has_second:
                bonus += 0.2
            
            # Check reverse combination
            my_has_second = any(tag.category == cat2 and tag.value == val2 
                              for tag in self.tags.values())
            other_has_first = any(tag.category == cat1 and tag.value == val1 
                                for tag in other.tags.values())
            
            if my_has_second and other_has_first:
                bonus += 0.2
        
        return min(bonus, 1.0)
    
    def get_dominant_characteristics(self) -> Dict[TagCategory, Tag]:
        """
        Get the dominant (highest priority) tag for each category.
        
        Returns:
            Dictionary mapping categories to their dominant tags
        """
        with self._lock:
            dominant = {}
            
            for category in TagCategory:
                category_tags = self.get_tags_by_category(category)
                if category_tags:
                    # Sort by priority (0 = highest priority)
                    dominant_tag = min(category_tags, key=lambda t: t.priority)
                    dominant[category] = dominant_tag
            
            return dominant
    
    def _update_category_index(self, tag: Tag, add: bool) -> None:
        """Update the category index when tags are added or removed."""
        if tag.category not in self._category_index:
            self._category_index[tag.category] = set()
        
        if add:
            self._category_index[tag.category].add(tag.full_tag)
        else:
            self._category_index[tag.category].discard(tag.full_tag)
            # Clean up empty categories
            if not self._category_index[tag.category]:
                del self._category_index[tag.category]
    
    def export_tags(self) -> List[Dict[str, Any]]:
        """
        Export tags to a serializable format.
        
        Returns:
            List of tag dictionaries
        """
        with self._lock:
            return [
                {
                    "category": tag.category.value,
                    "value": tag.value,
                    "metadata": tag.metadata,
                    "priority": tag.priority,
                    "full_tag": tag.full_tag
                }
                for tag in self.tags.values()
            ]
    
    def import_tags(self, tag_data: List[Dict[str, Any]]) -> int:
        """
        Import tags from serialized format.
        
        Args:
            tag_data: List of tag dictionaries
            
        Returns:
            Number of tags successfully imported
        """
        imported = 0
        for data in tag_data:
            try:
                category = TagCategory(data["category"])
                tag = Tag(
                    category=category,
                    value=data["value"],
                    metadata=data.get("metadata", {}),
                    priority=data.get("priority", 0)
                )
                if self.add_tag(tag):
                    imported += 1
            except (ValueError, KeyError) as e:
                # Skip invalid tag data
                continue
        
        return imported
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the tag set.
        
        Returns:
            Dictionary with tag set statistics
        """
        with self._lock:
            category_counts = {}
            priority_distribution = {}
            
            for tag in self.tags.values():
                # Count by category
                cat_name = tag.category.value
                if cat_name not in category_counts:
                    category_counts[cat_name] = 0
                category_counts[cat_name] += 1
                
                # Count by priority
                if tag.priority not in priority_distribution:
                    priority_distribution[tag.priority] = 0
                priority_distribution[tag.priority] += 1
            
            return {
                "total_tags": len(self.tags),
                "category_distribution": category_counts,
                "priority_distribution": priority_distribution,
                "categories_represented": len(self._category_index),
                "average_priority": sum(tag.priority for tag in self.tags.values()) / max(len(self.tags), 1)
            }
    
    def __len__(self) -> int:
        return len(self.tags)
    
    def __iter__(self):
        return iter(self.tags.values())
    
    def __contains__(self, pattern: str) -> bool:
        return self.has_tag(pattern)
    
    def __str__(self) -> str:
        tag_list = sorted([tag.full_tag for tag in self.tags.values()])
        return f"TagSet({tag_list})"
    
    def __repr__(self) -> str:
        return f"TagSet(tags={len(self.tags)})"


# Utility functions for common tag operations
def create_tag(category: str, value: str, **kwargs) -> Tag:
    """
    Convenience function to create a tag with string category.
    
    Args:
        category: Category name as string
        value: Tag value
        **kwargs: Additional tag parameters
        
    Returns:
        New Tag instance
    """
    try:
        tag_category = TagCategory(category)
        return Tag(category=tag_category, value=value, **kwargs)
    except ValueError:
        raise ValueError(f"Unknown tag category: {category}")


def parse_tag_string(tag_string: str) -> Tag:
    """
    Parse a tag from string format "category:value".
    
    Args:
        tag_string: String in format "category:value"
        
    Returns:
        New Tag instance
        
    Raises:
        ValueError: If tag string format is invalid
    """
    if ':' not in tag_string:
        raise ValueError(f"Tag string must contain ':' separator: {tag_string}")
    
    category_str, value = tag_string.split(':', 1)
    return create_tag(category_str, value)


def create_tag_set_from_strings(tag_strings: List[str]) -> TagSet:
    """
    Create a TagSet from a list of tag strings.
    
    Args:
        tag_strings: List of strings in format "category:value"
        
    Returns:
        New TagSet with parsed tags
    """
    tags = []
    for tag_string in tag_strings:
        try:
            tag = parse_tag_string(tag_string)
            tags.append(tag)
        except ValueError:
            # Skip invalid tag strings
            continue
    
    return TagSet(tags)


# Pre-defined tag collections for common use cases
class CommonTags:
    """Collection of commonly used tag instances."""
    
    # Domain tags
    COMBAT = Tag(TagCategory.DOMAIN, "combat")
    SUPPORT = Tag(TagCategory.DOMAIN, "support")
    ECONOMY = Tag(TagCategory.DOMAIN, "economy")
    EXPLORATION = Tag(TagCategory.DOMAIN, "exploration")
    
    # Role tags
    LEADER = Tag(TagCategory.ROLE, "leader")
    SUPPORT_ROLE = Tag(TagCategory.ROLE, "support")
    SCOUT = Tag(TagCategory.ROLE, "scout")
    SPECIALIST = Tag(TagCategory.ROLE, "specialist")
    
    # Ability tags
    HEALING = Tag(TagCategory.ABILITY, "healing")
    DAMAGE = Tag(TagCategory.ABILITY, "damage")
    STEALTH = Tag(TagCategory.ABILITY, "stealth")
    COMMAND = Tag(TagCategory.ABILITY, "command")
    TRADE = Tag(TagCategory.ABILITY, "trade")
    
    # Type tags
    ARCHON = Tag(TagCategory.TYPE, "archon")
    SPIRIT = Tag(TagCategory.TYPE, "spirit")
    FAMILIAR = Tag(TagCategory.TYPE, "familiar")
    
    # Status tags
    ACTIVE = Tag(TagCategory.STATUS, "active")
    IDLE = Tag(TagCategory.STATUS, "idle")
    COMBAT_STATUS = Tag(TagCategory.STATUS, "combat")
    WOUNDED = Tag(TagCategory.STATUS, "wounded")
    
    # Behavior tags
    AGGRESSIVE = Tag(TagCategory.BEHAVIOR, "aggressive")
    DEFENSIVE = Tag(TagCategory.BEHAVIOR, "defensive")
    NEUTRAL = Tag(TagCategory.BEHAVIOR, "neutral")
    ADAPTIVE = Tag(TagCategory.BEHAVIOR, "adaptive")


class TagSetBuilder:
    """Builder pattern for creating complex tag sets."""
    
    def __init__(self):
        self._tags: List[Tag] = []
    
    def add_domain(self, domain: str) -> 'TagSetBuilder':
        self._tags.append(Tag(TagCategory.DOMAIN, domain))
        return self
    
    def add_role(self, role: str) -> 'TagSetBuilder':
        self._tags.append(Tag(TagCategory.ROLE, role))
        return self
    
    def add_ability(self, ability: str) -> 'TagSetBuilder':
        self._tags.append(Tag(TagCategory.ABILITY, ability))
        return self
    
    def add_behavior(self, behavior: str) -> 'TagSetBuilder':
        self._tags.append(Tag(TagCategory.BEHAVIOR, behavior))
        return self
    
    def add_status(self, status: str) -> 'TagSetBuilder':
        self._tags.append(Tag(TagCategory.STATUS, status))
        return self
    
    def add_custom(self, category: TagCategory, value: str, **kwargs) -> 'TagSetBuilder':
        self._tags.append(Tag(category, value, **kwargs))
        return self
    
    def build(self) -> TagSet:
        return TagSet(self._tags.copy())


# Example usage and factory functions
def create_combat_familiar_tags() -> TagSet:
    """Create a standard tag set for combat familiars."""
    return (TagSetBuilder()
            .add_domain("combat")
            .add_role("specialist")
            .add_ability("damage")
            .add_behavior("aggressive")
            .add_status("active")
            .add_custom(TagCategory.TYPE, "familiar")
            .build())


def create_healer_spirit_tags() -> TagSet:
    """Create a standard tag set for healer spirits."""
    return (TagSetBuilder()
            .add_domain("support")
            .add_role("leader")
            .add_ability("healing")
            .add_behavior("defensive")
            .add_status("active")
            .add_custom(TagCategory.TYPE, "spirit")
            .build())


def create_strategic_archon_tags() -> TagSet:
    """Create a standard tag set for strategic archons."""
    return (TagSetBuilder()
            .add_domain("combat")
            .add_role("leader")
            .add_ability("command")
            .add_behavior("adaptive")
            .add_status("active")
            .add_custom(TagCategory.TYPE, "archon")
            .add_custom(TagCategory.SPECIALTY, "strategy")
            .build())