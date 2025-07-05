# Dual Terminology System Documentation

## Overview

Grimoire offers a unique **dual terminology system** that allows developers to choose between **technical** and **mystical** terminology based on their preference, project context, or team culture. Both terminologies provide identical functionality with zero performance difference.

## 🎯 Design Philosophy

The dual terminology system recognizes that different developers have different preferences:

- **Technical users** prefer conventional programming terminology
- **Mystical users** enjoy immersive, magical programming experiences
- **Mixed teams** benefit from flexibility and gradual adoption

## 📋 Complete Terminology Reference

### Core Classes and Types

| Technical | Mystical | Description |
|-----------|----------|-------------|
| `Tag` | `Mark` | Individual entity attribute |
| `TagSet` | `MarkSet` | Collection of tags/marks |
| `TaggedEntity` | `MarkedEntity` | Entity with tags/marks |
| `TagRegistry` | `MarkRegistry` | Central entity registry |
| `TagCategory` | `MarkCategory` | Tag/mark categories |
| `CommonTags` | `CommonMarks` | Pre-defined instances |

### Entity Methods

| Technical | Mystical | Description |
|-----------|----------|-------------|
| `add_tag(tag)` | `mark(tag)` | Add attribute to entity |
| `remove_tag(pattern)` | `unmark(pattern)` | Remove attributes |
| `has_tag(pattern)` | `bears_mark(pattern)` | Check for attribute |
| `has_capability(ability)` | `may(ability)` | Check capabilities |

### Registry Functions

| Technical | Mystical | Description |
|-----------|----------|-------------|
| `query_by_tags(tags)` | `seek_mark(marks)` | Find entities by attributes |
| `find_compatible(entity)` | `seek_match(entity)` | Find compatible entities |
| `get_entities_by_type(type)` | `gather_kind(type)` | Get entities by type |
| `suggest_tags(entity)` | `suggest_marks(entity)` | Get attribute suggestions |

### Agent Creation

| Technical | Mystical | Description |
|-----------|----------|-------------|
| `create_familiar` | `conjure_familiar` | Create familiar agent |
| `create_spirit` | `conjure_spirit` | Create spirit agent |
| `create_archon` | `conjure_archon` | Create archon agent |
| `create_familiar_with_pact` | `conjure_familiar_with_pact` | Create with pact |

### Utility Functions

| Technical | Mystical | Description |
|-----------|----------|-------------|
| `create_tag(cat, val)` | `create_mark(cat, val)` | Create new attribute |
| `parse_tag_string(str)` | `parse_mark_string(str)` | Parse from string |
| `tag_registry` | `mark_registry` | Global registry |
| `how_matched(a, b)` | `how_matched(a, b)` | Compatibility score |
| `has_power(entity)` | `has_power(entity)` | Get capabilities |

## 🔧 Implementation Details

### Zero-Overhead Aliasing

The dual terminology system uses **direct reference aliasing**:

```python
# Class aliases are direct references
Mark = Tag
MarkSet = TagSet
MarkedEntity = TaggedEntity

# Function aliases are wrapper functions
def create_mark(category: str, value: str, **kwargs) -> Tag:
    return create_tag(category, value, **kwargs)

def seek_mark(required_marks: List[str], **kwargs) -> List[TaggedEntity]:
    return query_by_tags(required_marks, **kwargs)
```

This ensures:
- **Zero performance overhead**
- **Identical functionality**
- **Same memory usage**
- **Thread safety preservation**

### Method Aliasing

Entity methods are aliased at the class level:

```python
class TaggedEntity:
    def add_tag(self, tag: Tag) -> bool:
        # Original implementation
        pass
    
    def mark(self, tag: Tag) -> bool:
        """Alias for add_tag using mystical terminology."""
        return self.add_tag(tag)
```

## 🎮 Usage Examples

### Basic Entity Creation

**Technical Approach:**
```python
from grimoire.tag_system import TaggedEntity, create_tag, CommonTags
from grimoire.tag_registry import query_by_tags, tag_registry

# Create entity
warrior = TaggedEntity("Warrior", "familiar")
warrior.add_tag(CommonTags.COMBAT)
warrior.add_tag(create_tag("ability", "damage"))

# Register and query
tag_registry.register_entity(warrior)
combat_units = query_by_tags(["domain:combat"])
```

**Mystical Approach:**
```python
from grimoire.tag_system import MarkedEntity, create_mark, CommonMarks
from grimoire.tag_registry import seek_mark, mark_registry

# Create entity
warrior = MarkedEntity("Warrior", "familiar")
warrior.mark(CommonMarks.COMBAT)
warrior.mark(create_mark("ability", "damage"))

# Register and query
mark_registry.register_entity(warrior)
combat_units = seek_mark(["domain:combat"])
```

**Mixed Approach:**
```python
from grimoire.tag_system import TaggedEntity, create_mark, CommonTags
from grimoire.tag_registry import seek_mark, tag_registry

# Mix terminologies freely
warrior = TaggedEntity("Warrior", "familiar")
warrior.mark(CommonTags.COMBAT)  # Mystical method
warrior.add_tag(create_mark("ability", "damage"))  # Mixed constructors

tag_registry.register_entity(warrior)
combat_units = seek_mark(["domain:combat"])  # Mystical query
```

### Advanced Compatibility Analysis

**Technical:**
```python
# Technical compatibility analysis
healer = TaggedEntity("Healer", "spirit")
healer.add_tag(create_tag("domain", "support"))
healer.add_tag(create_tag("ability", "healing"))

wounded = TaggedEntity("Wounded", "familiar")
wounded.add_tag(create_tag("status", "wounded"))

# Check compatibility
compatible_entities = find_compatible(healer, min_compatibility=0.5)
can_interact = healer.can_interact_with(wounded)
```

**Mystical:**
```python
# Mystical compatibility analysis
healer = MarkedEntity("Healer", "spirit")
healer.mark(create_mark("domain", "support"))
healer.mark(create_mark("ability", "healing"))

wounded = MarkedEntity("Wounded", "familiar")
wounded.mark(create_mark("status", "wounded"))

# Seek compatibility
compatible_entities = seek_match(healer, min_compatibility=0.5)
can_interact = healer.can_interact_with(wounded)
compatibility_score = how_matched(healer, wounded)
```

### Agent Creation Examples

**Technical:**
```python
from grimoire.interpreter import GrimoireInterpreter

interpreter = GrimoireInterpreter()

# Create agents technically
spirit = interpreter.globals.get("create_spirit")(interpreter, ["Guardian", "defense"])
archon = interpreter.globals.get("create_archon")(interpreter, ["Commander", "strategy"])
```

**Mystical:**
```python
from grimoire.interpreter import GrimoireInterpreter

interpreter = GrimoireInterpreter()

# Conjure agents mystically
spirit = interpreter.globals.get("conjure_spirit")(interpreter, ["Guardian", "defense"])
archon = interpreter.globals.get("conjure_archon")(interpreter, ["Commander", "strategy"])
```

## 🧪 Testing and Verification

### Equivalence Testing

```python
def test_terminology_equivalence():
    # Test class aliases
    assert Tag is Mark
    assert TagSet is MarkSet
    assert TaggedEntity is MarkedEntity
    
    # Test function equivalence
    tech_tag = create_tag("domain", "combat")
    mystic_mark = create_mark("domain", "combat")
    assert tech_tag.full_tag == mystic_mark.full_tag
    
    # Test method equivalence
    entity = TaggedEntity("Test", "familiar")
    entity.add_tag(tech_tag)
    entity.mark(mystic_mark)
    
    assert entity.has_tag("domain:combat")
    assert entity.bears_mark("domain:combat")
    assert entity.has_capability("combat") == entity.may("combat")
```

### Performance Testing

```python
import time

def test_performance_equivalence():
    # Create test entities
    entities = []
    for i in range(1000):
        entity = TaggedEntity(f"Entity_{i}", "familiar")
        entity.add_tag(create_tag("domain", "combat" if i % 2 else "support"))
        tag_registry.register_entity(entity)
        entities.append(entity)
    
    # Time technical terminology
    start = time.time()
    for _ in range(1000):
        results = query_by_tags(["domain:combat"])
        compatible = find_compatible(entities[0])
    tech_time = time.time() - start
    
    # Time mystical terminology
    start = time.time()
    for _ in range(1000):
        results = seek_mark(["domain:combat"])
        compatible = seek_match(entities[0])
    mystic_time = time.time() - start
    
    # Assert equivalent performance (within 1ms)
    assert abs(tech_time - mystic_time) < 0.001
```

## 🌟 Best Practices

### When to Use Technical Terminology

- **Enterprise environments** with conventional coding standards
- **Team projects** where technical precision is valued
- **Integration code** with existing technical systems
- **Documentation** requiring clear, unambiguous language

### When to Use Mystical Terminology

- **Game development** projects with magical/fantasy themes
- **Creative coding** where immersion enhances productivity
- **Educational contexts** where engagement is important
- **Prototyping** where playful exploration is encouraged

### When to Mix Terminologies

- **Migration projects** gradually adopting mystical terminology
- **Large teams** with diverse preferences
- **API boundaries** where different layers use different styles
- **Personal preference** based on context and mood

### Code Organization

```python
# Option 1: Separate imports by style
from grimoire.tag_system import Tag, TaggedEntity, create_tag  # Technical
from grimoire.tag_system import Mark, MarkedEntity, create_mark  # Mystical

# Option 2: Import both and choose contextually
from grimoire.tag_system import (
    Tag, Mark, TaggedEntity, MarkedEntity,
    create_tag, create_mark
)

# Option 3: Use aliases for team consistency
from grimoire.tag_system import Tag as Mark, TaggedEntity as MarkedEntity
```

## 🔮 Advanced Features

### Cross-Terminology Compatibility

Entities created with different terminologies are fully compatible:

```python
# Technical entity
tech_warrior = TaggedEntity("TechWarrior", "familiar")
tech_warrior.add_tag(create_tag("domain", "combat"))

# Mystical entity
mystic_healer = MarkedEntity("MysticHealer", "spirit")
mystic_healer.mark(create_mark("domain", "support"))

# Cross-terminology compatibility
compatibility = how_matched(tech_warrior, mystic_healer)  # Works perfectly
can_interact = tech_warrior.can_interact_with(mystic_healer)  # True
```

### Intelligent Suggestions

Both terminologies support intelligent tag/mark suggestions:

```python
# Technical suggestions
tech_suggestions = suggest_tags(warrior, max_suggestions=5)

# Mystical suggestions (identical results)
mystic_suggestions = suggest_marks(warrior, max_suggestions=5)

assert tech_suggestions == mystic_suggestions
```

### Registry Interoperability

Both registries are the same object:

```python
assert tag_registry is mark_registry

# Register with technical terminology
tag_registry.register_entity(tech_entity)

# Query with mystical terminology
results = seek_mark(["domain:combat"])  # Finds tech_entity
```

## 📊 Migration Guide

### Gradual Adoption

**Step 1: Start with aliases**
```python
# Keep existing code, add aliases
TaggedEntity = MarkedEntity
add_tag = mark
query_by_tags = seek_mark
```

**Step 2: Mixed usage**
```python
# Use mystical methods on technical classes
warrior = TaggedEntity("Warrior", "familiar")
warrior.mark(create_mark("domain", "combat"))  # Mixed approach
```

**Step 3: Full adoption**
```python
# Migrate to full mystical terminology
warrior = MarkedEntity("Warrior", "familiar")
warrior.mark(create_mark("domain", "combat"))
results = seek_mark(["domain:combat"])
```

### Team Guidelines

1. **Choose a primary style** for new code
2. **Document the choice** in project guidelines
3. **Allow mixed usage** during transition periods
4. **Maintain consistency** within individual modules
5. **Use linting rules** to enforce style choices

## 🎯 Conclusion

The dual terminology system makes Grimoire uniquely flexible, accommodating different developer preferences while maintaining technical excellence. Whether you prefer the precision of technical terminology or the immersion of mystical terminology, Grimoire adapts to your style without compromising functionality or performance.

Both terminologies are **production-ready**, **fully tested**, and **completely equivalent**. Choose the style that best fits your project, team, and personal preferences!