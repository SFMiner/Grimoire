## Concept:

Building a tag system into the program language itself could in the simplicity and robustness of programming. Various inputs and agents, for example, can be given tags, to identify what they are, rather than have to hard code those into the system.

## Analysis of Grimoire's Current Structure

The Grimoire programming language is an impressively designed magical-themed language with:

**Current Architecture:**

- Three-tier hierarchical agent system (Archons → Spirits → Familiars)
- Immutable pact system for secure agent interactions
- Rich thematic syntax with magical keywords
- Built-in monitoring and debugging systems
- Python-based implementation with lexer, parser, and interpreter modules

**Current Entity Identification:**

- Uses "true names" with SHA256 hashing for security
- Domain-based authority systems
- Immutable pacts for defining agent behavior
- Hard-coded agent types and roles

## Efficacy of Incorporating a Tag System

### **High Efficacy - Strongly Recommended**

Incorporating a tag system would be extremely beneficial for Grimoire for several key reasons:

### **1. Enhanced Flexibility and Extensibility**

**Current Limitation:** The system currently requires hard-coding specific agent types, domains, and pact terms. New entity types require code changes.

**Tag System Solution:**

grimoire

```grimoire
# Instead of hard-coded types
create_spirit("Infantry", "Combat", ["maintain_formation"])

# Use flexible tags
bind infantry_spirit = create_spirit upon $SCROLL(Infantry), 
    tags: [$TAG(unit_type:infantry), $TAG(domain:combat), $TAG(role:tactical), $TAG(mobility:ground)]
```

### **2. Dynamic Query and Discovery**

**Benefits:**

- Agents could discover compatible entities by tags
- Dynamic formation of groups based on tag matching
- Runtime adaptation without pre-defined relationships

grimoire

```grimoire
# Find all combat units with healing capabilities
bind healers = query_entities_by_tags([$TAG(domain:combat), $TAG(ability:healing)])

# Find entities that can work together
bind compatible_agents = find_compatible_by_tags(my_familiar, $TAG(cooperation:tactical))
```

### **3. Emergent Behavior Through Tag-Based Interactions**

**Current:** Interactions are predefined in pact terms and agent hierarchies.

**With Tags:** Entities could dynamically form relationships based on complementary or compatible tags:

grimoire

```grimoire
ritual auto_form_squad():
    bind leader = query_by_tags([$TAG(role:leader), $TAG(domain:combat)])
    bind supporters = query_by_tags([$TAG(role:support), $TAG(domain:combat)])
    # Automatically create tactical groups
```

### **4. Simplified Pact Creation**

**Enhanced Pact System:**

grimoire

```grimoire
# Tag-based pact templates
bind healing_pact = create_pact_template upon
    required_tags: [$TAG(ability:healing), $TAG(domain:support)],
    granted_permissions: [$TAG(action:heal), $TAG(access:mana_pool)],
    conditions: [$TAG(trigger:health_low)]

# Automatically match familiars to appropriate pacts
bind healer = create_familiar_with_tag_matching upon healing_spirit, healing_pact
```

### **5. Advanced Monitoring and Analytics**

**Enhanced Familiar Wrangler:**

grimoire

```grimoire
# Monitor by tag categories
enable_reporting_by_tags([$TAG(domain:combat)], ["command", "environmental"])

# Analytics across tag groups
bind combat_performance = analyze_performance_by_tags([$TAG(domain:combat)])
bind healing_efficiency = get_stats_by_tags([$TAG(ability:healing)])
```

## Recommended Implementation Strategy

### **Phase 1: Core Tag Infrastructure**

python

```python
class Tag:
    def __init__(self, category: str, value: str, metadata: dict = None):
        self.category = category
        self.value = value
        self.metadata = metadata or {}
        self.full_tag = f"{category}:{value}"

class TaggedEntity:
    def __init__(self, name: str, tags: List[Tag]):
        self.name = name
        self.tags = {tag.full_tag: tag for tag in tags}
        self.true_name = self.generate_true_name()
    
    def has_tag(self, tag_pattern: str) -> bool:
        return tag_pattern in self.tags
    
    def matches_any(self, tag_patterns: List[str]) -> bool:
        return any(self.has_tag(pattern) for pattern in tag_patterns)
```

### **Phase 2: Language Syntax Integration**

grimoire

```grimoire
# New tag literal syntax
$TAG(category:value)
$TAG(domain:combat)
$TAG(ability:healing)
$TAG(role:leader)

# Tag-aware agent creation
bind combat_archon = create_archon upon $SCROLL(WarLeader),
    tags: [$TAG(domain:combat), $TAG(level:strategic), $TAG(specialty:coordination)]

# Tag-based queries in the language
bind healers = query_by_tags([$TAG(ability:healing), $TAG(status:available)])
```

### **Phase 3: Enhanced Pact System**

grimoire

```grimoire
# Tag-based pact matching
create_pact_template upon $SCROLL(healing_template),
    required_entity_tags: [$TAG(type:familiar), $TAG(ability:healing)],
    required_spirit_tags: [$TAG(domain:support)],
    granted_tags: [$TAG(permission:heal), $TAG(access:mana_pool)]
```

### **Phase 4: Advanced Features**

- Tag inheritance and hierarchies
- Dynamic tag assignment based on experience
- Tag-based AI goal generation
- Performance optimization for tag queries

## Integration Points in Current Codebase

**Lexer Updates:**

- Add `$TAG()` token type
- Support tag literal parsing

**Parser Enhancements:**

- Tag expressions in entity creation
- Tag-based query syntax
- Tag conditions in pacts

**Interpreter Extensions:**

- Tag registry and query engine
- Tag-aware agent creation functions
- Enhanced pact matching system

## Conclusion

A tag system would dramatically enhance Grimoire's flexibility and power while maintaining its magical theme. It addresses the current limitation of hard-coded entity types and relationships, enabling:

1. **Dynamic Discovery** - Entities finding each other based on capabilities
2. **Emergent Relationships** - Natural formation of agent groups
3. **Simplified Configuration** - Less hard-coding, more declarative specifications
4. **Enhanced Debugging** - Better categorization and filtering of entities
5. **Scalable Architecture** - Easy addition of new entity types without code changes

The tag system aligns perfectly with Grimoire's existing architecture while providing the extensibility needed for complex game development scenarios. It would transform Grimoire from a structured but rigid system into a truly adaptive and emergent AI ecosystem.

Retry

SM

Write up an implementation plan.

Edit

# Grimoire Tag System Implementation Plan

## 🎯 Executive Summary

This plan outlines the implementation of a comprehensive tag system for the Grimoire programming language, transforming it from a rigid, hard-coded entity system into a flexible, emergent AI ecosystem. The tag system will integrate seamlessly with existing hierarchical agents, pacts, and monitoring systems while maintaining Grimoire's magical theme.

## 📋 Implementation Overview

### **Timeline:** 12-16 weeks

### **Phases:** 6 major phases with incremental deliverables

### **Impact:** Revolutionary enhancement to entity flexibility and emergent behavior

---

## 🏗️ Phase 1: Core Tag Infrastructure (Weeks 1-3)

### **Objective**

Build the foundational tag system that will underpin all entity identification and categorization.

### **Deliverables**

#### **1.1 Tag Data Structures**

python

```python
# grimoire/tag_system.py
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
import hashlib
from enum import Enum

class TagCategory(Enum):
    DOMAIN = "domain"           # combat, economy, support
    ROLE = "role"              # leader, support, scout
    ABILITY = "ability"        # healing, damage, stealth
    TYPE = "type"              # archon, spirit, familiar
    STATUS = "status"          # active, idle, combat
    PERMISSION = "permission"   # heal, attack, trade
    RESOURCE = "resource"      # mana, health, gold
    BEHAVIOR = "behavior"      # aggressive, defensive, neutral
    SPECIALTY = "specialty"    # coordination, tactics, logistics

@dataclass
class Tag:
    category: TagCategory
    value: str
    metadata: Dict[str, Any] = None
    priority: int = 0  # For hierarchical tag importance
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.full_tag = f"{self.category.value}:{self.value}"
        self.hash = hashlib.sha256(self.full_tag.encode()).hexdigest()[:16]
    
    def matches(self, pattern: str) -> bool:
        """Check if tag matches a pattern like 'domain:*' or 'domain:combat'"""
        if ':' not in pattern:
            return self.category.value == pattern
        cat, val = pattern.split(':', 1)
        return (self.category.value == cat and 
                (val == '*' or self.value == val))

class TagSet:
    def __init__(self, tags: List[Tag] = None):
        self.tags: Dict[str, Tag] = {}
        if tags:
            for tag in tags:
                self.add_tag(tag)
    
    def add_tag(self, tag: Tag) -> None:
        self.tags[tag.full_tag] = tag
    
    def remove_tag(self, tag_pattern: str) -> bool:
        matches = [k for k in self.tags.keys() if self.tags[k].matches(tag_pattern)]
        for match in matches:
            del self.tags[match]
        return len(matches) > 0
    
    def has_tag(self, pattern: str) -> bool:
        return any(tag.matches(pattern) for tag in self.tags.values())
    
    def get_tags_by_category(self, category: TagCategory) -> List[Tag]:
        return [tag for tag in self.tags.values() if tag.category == category]
    
    def matches_all(self, patterns: List[str]) -> bool:
        return all(self.has_tag(pattern) for pattern in patterns)
    
    def matches_any(self, patterns: List[str]) -> bool:
        return any(self.has_tag(pattern) for pattern in patterns)
    
    def compatibility_score(self, other: 'TagSet') -> float:
        """Calculate compatibility score between two tag sets"""
        common_categories = set()
        compatible_pairs = 0
        
        for tag in self.tags.values():
            for other_tag in other.tags.values():
                if tag.category == other_tag.category:
                    common_categories.add(tag.category)
                    if self._tags_compatible(tag, other_tag):
                        compatible_pairs += 1
        
        return compatible_pairs / max(len(common_categories), 1)
    
    def _tags_compatible(self, tag1: Tag, tag2: Tag) -> bool:
        """Define compatibility rules between tags"""
        compatibility_rules = {
            (TagCategory.ROLE, "leader", "support"): True,
            (TagCategory.ABILITY, "healing", "damage"): True,
            (TagCategory.BEHAVIOR, "aggressive", "defensive"): False,
        }
        
        key = (tag1.category, tag1.value, tag2.value)
        reverse_key = (tag1.category, tag2.value, tag1.value)
        
        return compatibility_rules.get(key, compatibility_rules.get(reverse_key, True))
```

#### **1.2 Tag Registry System**

python

```python
# grimoire/tag_registry.py
class TagRegistry:
    def __init__(self):
        self.entities: Dict[str, 'TaggedEntity'] = {}
        self.tag_index: Dict[str, Set[str]] = {}  # tag_pattern -> entity_names
        self.category_index: Dict[TagCategory, Set[str]] = {}
    
    def register_entity(self, entity: 'TaggedEntity') -> None:
        self.entities[entity.true_name] = entity
        self._index_entity_tags(entity)
    
    def unregister_entity(self, entity_name: str) -> None:
        if entity_name in self.entities:
            self._remove_from_indexes(entity_name)
            del self.entities[entity_name]
    
    def query_by_tags(self, required_tags: List[str], 
                     optional_tags: List[str] = None) -> List['TaggedEntity']:
        """Find entities matching tag criteria"""
        candidates = None
        
        # Find intersection of entities with required tags
        for tag_pattern in required_tags:
            matching_entities = self._get_entities_with_tag(tag_pattern)
            if candidates is None:
                candidates = matching_entities
            else:
                candidates = candidates.intersection(matching_entities)
        
        if candidates is None:
            return []
        
        # Score by optional tags if provided
        results = [self.entities[name] for name in candidates]
        if optional_tags:
            results.sort(key=lambda e: self._score_optional_tags(e, optional_tags), 
                        reverse=True)
        
        return results
    
    def find_compatible_entities(self, entity: 'TaggedEntity', 
                               min_compatibility: float = 0.5) -> List['TaggedEntity']:
        """Find entities compatible with the given entity"""
        compatible = []
        for other in self.entities.values():
            if other.true_name != entity.true_name:
                score = entity.tags.compatibility_score(other.tags)
                if score >= min_compatibility:
                    compatible.append((other, score))
        
        # Sort by compatibility score
        compatible.sort(key=lambda x: x[1], reverse=True)
        return [entity for entity, score in compatible]
```

#### **1.3 Tagged Entity Base Class**

python

```python
# grimoire/tagged_entity.py
class TaggedEntity:
    def __init__(self, name: str, entity_type: str, tags: List[Tag] = None):
        self.name = name
        self.entity_type = entity_type
        self.tags = TagSet(tags or [])
        self.true_name = self._generate_true_name()
        self.creation_time = time.time()
        self.metadata = {}
    
    def _generate_true_name(self) -> str:
        """Generate cryptographic true name including tags"""
        content = f"{self.name}:{self.entity_type}:{self.creation_time}"
        tag_signatures = sorted([tag.hash for tag in self.tags.tags.values()])
        content += ":" + ":".join(tag_signatures)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_tag(self, tag: Tag) -> None:
        """Add a tag and update registry"""
        self.tags.add_tag(tag)
        # Notify registry of tag change
        registry.update_entity_tags(self)
    
    def remove_tag(self, tag_pattern: str) -> bool:
        """Remove tags matching pattern"""
        removed = self.tags.remove_tag(tag_pattern)
        if removed:
            registry.update_entity_tags(self)
        return removed
    
    def has_capability(self, capability: str) -> bool:
        """Check if entity has specific capability"""
        return self.tags.has_tag(f"ability:{capability}")
    
    def can_interact_with(self, other: 'TaggedEntity') -> bool:
        """Check if this entity can interact with another"""
        return self.tags.compatibility_score(other.tags) > 0.3
```

### **Testing Strategy**

- Unit tests for tag matching and compatibility
- Performance tests for tag queries
- Integration tests with existing entity system

---

## ⚡ Phase 2: Language Syntax Integration (Weeks 4-6)

### **Objective**

Integrate tag syntax into Grimoire's lexer, parser, and interpreter.

### **Deliverables**

#### **2.1 Lexer Extensions**

python

```python
# grimoire/lexer.py - Token additions
class TokenType(Enum):
    # ... existing tokens
    TAG = auto()              # $TAG(category:value)
    TAG_QUERY = auto()        # query_by_tags()
    TAG_MATCH = auto()        # matches_tags()
    COLON = auto()            # : for tag syntax

# Lexer.scan_token() additions
elif c == '$':
    if self.match_sequence('TAG'):
        self.tag_literal()
    elif self.match_sequence('SCROLL'):
        self.scroll_literal()
    # ... other $ literals

def tag_literal(self) -> None:
    """Handle $TAG(category:value) literals"""
    if not self.match('('):
        raise SyntaxError(f"Expected '(' after $TAG at line {self.line}")
    
    # Parse category:value inside parentheses
    tag_content = ""
    while self.peek() != ')' and not self.is_at_end():
        tag_content += self.advance()
    
    if ':' not in tag_content:
        raise SyntaxError(f"Tag must have format 'category:value' at line {self.line}")
    
    category, value = tag_content.split(':', 1)
    self.advance()  # consume )
    self.add_token(TokenType.TAG, (category.strip(), value.strip()))
```

#### **2.2 Parser Extensions**

python

```python
# grimoire/parser.py - AST node additions
class TagLiteralNode(ASTNode):
    def __init__(self, category: str, value: str):
        self.category = category
        self.value = value

class TaggedEntityCreationNode(ASTNode):
    def __init__(self, entity_type: str, name: str, tags: List[TagLiteralNode]):
        self.entity_type = entity_type
        self.name = name
        self.tags = tags

class TagQueryNode(ASTNode):
    def __init__(self, required_tags: List[TagLiteralNode], 
                 optional_tags: List[TagLiteralNode] = None):
        self.required_tags = required_tags
        self.optional_tags = optional_tags or []

# Parser method additions
def parse_tag_literal(self) -> TagLiteralNode:
    """Parse $TAG(category:value)"""
    token = self.consume(TokenType.TAG, "Expected tag literal")
    category, value = token.literal
    return TagLiteralNode(category, value)

def parse_entity_with_tags(self) -> TaggedEntityCreationNode:
    """Parse entity creation with tags"""
    entity_type = self.consume(TokenType.IDENTIFIER, "Expected entity type").lexeme
    name = self.parse_expression()
    
    tags = []
    if self.match(TokenType.IDENTIFIER) and self.previous().lexeme == "tags":
        self.consume(TokenType.COLON, "Expected ':' after 'tags'")
        tags = self.parse_tag_list()
    
    return TaggedEntityCreationNode(entity_type, name, tags)
```

#### **2.3 Interpreter Integration**

python

```python
# grimoire/interpreter.py - Evaluation additions
def visit_tag_literal(self, node: TagLiteralNode) -> Tag:
    """Evaluate tag literal"""
    try:
        category = TagCategory(node.category)
    except ValueError:
        raise RuntimeError(f"Unknown tag category: {node.category}")
    
    return Tag(category, node.value)

def visit_tagged_entity_creation(self, node: TaggedEntityCreationNode) -> TaggedEntity:
    """Create tagged entity"""
    name_value = self.evaluate(node.name)
    tags = [self.evaluate(tag_node) for tag_node in node.tags]
    
    entity = TaggedEntity(str(name_value), node.entity_type, tags)
    tag_registry.register_entity(entity)
    
    return entity

# Built-in function additions
def builtin_query_by_tags(self, required_tags: List[str], 
                         optional_tags: List[str] = None) -> List[TaggedEntity]:
    """Query entities by tags"""
    return tag_registry.query_by_tags(required_tags, optional_tags)

def builtin_find_compatible(self, entity: TaggedEntity, 
                           min_score: float = 0.5) -> List[TaggedEntity]:
    """Find compatible entities"""
    return tag_registry.find_compatible_entities(entity, min_score)
```

### **New Syntax Examples**

grimoire

```grimoire
# Tag literals
bind combat_tag = $TAG(domain:combat)
bind healing_tag = $TAG(ability:healing)

# Tagged entity creation
bind warrior_spirit = create_spirit upon $SCROLL(BattleLeader),
    tags: [$TAG(domain:combat), $TAG(role:leader), $TAG(specialty:tactics)]

# Tag-based queries
bind healers = query_by_tags([$TAG(ability:healing), $TAG(status:available)])
bind compatible_units = find_compatible(my_familiar, 0.7)

# Tag-based conditionals
if entity has_tag($TAG(ability:healing)):
    scry $SCROLL("This entity can heal!")
```

---

## 🤝 Phase 3: Enhanced Pact System (Weeks 7-9)

### **Objective**

Revolutionize the pact system to use tags for dynamic matching and permission granting.

### **Deliverables**

#### **3.1 Tag-Aware Pact System**

python

```python
# grimoire/enhanced_pact_system.py
class TaggedPact:
    def __init__(self, name: str, spirit_true_name: str):
        self.name = name
        self.spirit_true_name = spirit_true_name
        self.required_entity_tags: TagSet = TagSet()
        self.required_spirit_tags: TagSet = TagSet()
        self.granted_tags: TagSet = TagSet()
        self.forbidden_tags: TagSet = TagSet()
        self.conditions: List[str] = []
        self.creation_time = time.time()
        self.immutable = False
    
    def make_immutable(self) -> None:
        """Lock the pact against further changes"""
        self.immutable = True
    
    def can_bind_entity(self, entity: TaggedEntity) -> bool:
        """Check if entity qualifies for this pact"""
        if self.immutable:
            return (entity.tags.matches_all([tag.full_tag for tag in self.required_entity_tags.tags.values()]) and
                   not entity.tags.matches_any([tag.full_tag for tag in self.forbidden_tags.tags.values()]))
        return False
    
    def apply_to_entity(self, entity: TaggedEntity) -> None:
        """Apply pact tags to entity"""
        if not self.can_bind_entity(entity):
            raise RuntimeError(f"Entity {entity.name} does not qualify for pact {self.name}")
        
        # Grant permission tags
        for tag in self.granted_tags.tags.values():
            entity.add_tag(tag)
        
        # Add pact binding tag
        pact_tag = Tag(TagCategory.STATUS, f"bound_to_{self.name}")
        entity.add_tag(pact_tag)

class PactTemplate:
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.required_entity_tags: List[str] = []
        self.required_spirit_tags: List[str] = []
        self.granted_permissions: List[str] = []
        self.behavioral_constraints: List[str] = []
    
    def instantiate_for_spirit(self, spirit: 'TaggedSpirit') -> TaggedPact:
        """Create a pact instance for a specific spirit"""
        pact = TaggedPact(f"{self.template_name}_{spirit.name}", spirit.true_name)
        
        # Set requirements
        for tag_pattern in self.required_entity_tags:
            category, value = tag_pattern.split(':')
            pact.required_entity_tags.add_tag(Tag(TagCategory(category), value))
        
        # Set granted permissions
        for permission in self.granted_permissions:
            pact.granted_tags.add_tag(Tag(TagCategory.PERMISSION, permission))
        
        pact.make_immutable()
        return pact

# Pre-defined pact templates
HEALING_PACT_TEMPLATE = PactTemplate("healing_support")
HEALING_PACT_TEMPLATE.required_entity_tags = ["ability:healing", "type:familiar"]
HEALING_PACT_TEMPLATE.required_spirit_tags = ["domain:support"]
HEALING_PACT_TEMPLATE.granted_permissions = ["heal", "access_mana", "priority_targeting"]

COMBAT_PACT_TEMPLATE = PactTemplate("combat_engagement")
COMBAT_PACT_TEMPLATE.required_entity_tags = ["ability:damage", "type:familiar"]
COMBAT_PACT_TEMPLATE.required_spirit_tags = ["domain:combat"]
COMBAT_PACT_TEMPLATE.granted_permissions = ["attack", "move_tactical", "call_reinforcements"]
```

#### **3.2 Automatic Pact Matching**

python

```python
# grimoire/pact_matcher.py
class PactMatcher:
    def __init__(self, pact_registry: 'PactRegistry'):
        self.pact_registry = pact_registry
        self.templates = {}
    
    def register_template(self, template: PactTemplate) -> None:
        self.templates[template.template_name] = template
    
    def find_suitable_pacts(self, entity: TaggedEntity, 
                           spirit: 'TaggedSpirit') -> List[TaggedPact]:
        """Find pacts that both entity and spirit qualify for"""
        suitable_pacts = []
        
        for template in self.templates.values():
            # Check if entity meets requirements
            entity_qualifies = all(
                entity.tags.has_tag(req) for req in template.required_entity_tags
            )
            
            # Check if spirit meets requirements
            spirit_qualifies = all(
                spirit.tags.has_tag(req) for req in template.required_spirit_tags
            )
            
            if entity_qualifies and spirit_qualifies:
                pact = template.instantiate_for_spirit(spirit)
                suitable_pacts.append(pact)
        
        return suitable_pacts
    
    def auto_create_optimal_pact(self, entity: TaggedEntity, 
                                spirit: 'TaggedSpirit') -> Optional[TaggedPact]:
        """Automatically create the best pact for entity-spirit pair"""
        suitable_pacts = self.find_suitable_pacts(entity, spirit)
        
        if not suitable_pacts:
            return None
        
        # Score pacts by compatibility and granted permissions
        best_pact = max(suitable_pacts, 
                       key=lambda p: self._score_pact_fitness(p, entity, spirit))
        
        return best_pact
    
    def _score_pact_fitness(self, pact: TaggedPact, entity: TaggedEntity, 
                           spirit: 'TaggedSpirit') -> float:
        """Score how well a pact fits the entity-spirit combination"""
        # Base compatibility score
        compatibility = entity.tags.compatibility_score(spirit.tags)
        
        # Bonus for number of relevant permissions granted
        relevant_permissions = 0
        for granted_tag in pact.granted_tags.tags.values():
            if granted_tag.category == TagCategory.PERMISSION:
                if entity.tags.has_tag(f"ability:{granted_tag.value}"):
                    relevant_permissions += 1
        
        return compatibility + (relevant_permissions * 0.1)
```

#### **3.3 New Pact Syntax**

grimoire

```grimoire
# Pact template definition
create_pact_template upon $SCROLL(healing_template),
    entity_requirements: [$TAG(ability:healing), $TAG(type:familiar)],
    spirit_requirements: [$TAG(domain:support)],
    grants: [$TAG(permission:heal), $TAG(permission:access_mana)]

# Automatic pact creation
bind healer_familiar = create_familiar_with_auto_pact upon healing_spirit, 
    $SCROLL(Healer),
    tags: [$TAG(ability:healing), $TAG(behavior:supportive)]

# Manual pact selection
bind available_pacts = find_suitable_pacts(my_familiar, combat_spirit)
bind chosen_pact = available_pacts[0]
bind_pact(my_familiar, chosen_pact)
```

---

## 🤖 Phase 4: Agent System Enhancement (Weeks 10-12)

### **Objective**

Upgrade Archons, Spirits, and Familiars to be fully tag-aware and enable emergent behavior.

### **Deliverables**

#### **4.1 Tagged Agent Hierarchy**

python

```python
# grimoire/tagged_agents.py
class TaggedArchon(TaggedEntity):
    def __init__(self, name: str, domain: str, goals: List[str], tags: List[Tag] = None):
        base_tags = [
            Tag(TagCategory.TYPE, "archon"),
            Tag(TagCategory.DOMAIN, domain),
            Tag(TagCategory.ROLE, "strategic")
        ]
        super().__init__(name, "archon", base_tags + (tags or []))
        
        self.domain = domain
        self.goals = goals
        self.managed_spirits: List['TaggedSpirit'] = []
        self.goal_priorities = {goal: 1.0 for goal in goals}
    
    def discover_compatible_spirits(self) -> List['TaggedSpirit']:
        """Find spirits that can work under this archon"""
        compatible = tag_registry.query_by_tags([
            f"type:spirit",
            f"domain:{self.domain}"
        ])
        return [spirit for spirit in compatible if isinstance(spirit, TaggedSpirit)]
    
    def auto_recruit_spirits(self, max_spirits: int = 5) -> None:
        """Automatically recruit compatible spirits"""
        available_spirits = self.discover_compatible_spirits()
        
        # Score spirits by compatibility and capabilities
        scored_spirits = [
            (spirit, self._score_spirit_value(spirit)) 
            for spirit in available_spirits 
            if not spirit.has_archon()
        ]
        
        # Recruit best spirits up to limit
        scored_spirits.sort(key=lambda x: x[1], reverse=True)
        recruited = 0
        for spirit, score in scored_spirits:
            if recruited >= max_spirits:
                break
            self.recruit_spirit(spirit)
            recruited += 1
    
    def _score_spirit_value(self, spirit: 'TaggedSpirit') -> float:
        """Score how valuable a spirit would be to this archon"""
        # Base compatibility
        score = self.tags.compatibility_score(spirit.tags)
        
        # Bonus for complementary abilities
        my_abilities = self.tags.get_tags_by_category(TagCategory.ABILITY)
        spirit_abilities = spirit.tags.get_tags_by_category(TagCategory.ABILITY)
        
        complementary = 0
        for my_ability in my_abilities:
            for spirit_ability in spirit_abilities:
                if self._abilities_complement(my_ability.value, spirit_ability.value):
                    complementary += 1
        
        return score + (complementary * 0.2)

class TaggedSpirit(TaggedEntity):
    def __init__(self, name: str, domain: str, specialties: List[str], tags: List[Tag] = None):
        base_tags = [
            Tag(TagCategory.TYPE, "spirit"),
            Tag(TagCategory.DOMAIN, domain),
            Tag(TagCategory.ROLE, "tactical")
        ]
        # Add specialty tags
        for specialty in specialties:
            base_tags.append(Tag(TagCategory.SPECIALTY, specialty))
        
        super().__init__(name, "spirit", base_tags + (tags or []))
        
        self.domain = domain
        self.specialties = specialties
        self.managed_familiars: List['TaggedFamiliar'] = []
        self.archon: Optional['TaggedArchon'] = None
        self.available_pacts: List[TaggedPact] = []
    
    def discover_suitable_familiars(self, max_results: int = 10) -> List['TaggedFamiliar']:
        """Find familiars that could work with this spirit"""
        # Look for familiars in compatible domains
        potential_familiars = tag_registry.query_by_tags([
            "type:familiar"
        ])
        
        # Filter and score by compatibility
        compatible = []
        for familiar in potential_familiars:
            if isinstance(familiar, TaggedFamiliar) and not familiar.has_spirit():
                compatibility = self.tags.compatibility_score(familiar.tags)
                if compatibility > 0.3:  # Minimum compatibility threshold
                    compatible.append((familiar, compatibility))
        
        # Sort by compatibility and return top matches
        compatible.sort(key=lambda x: x[1], reverse=True)
        return [familiar for familiar, score in compatible[:max_results]]
    
    def auto_create_familiars(self, count: int = 3) -> List['TaggedFamiliar']:
        """Automatically create familiars based on spirit's needs"""
        created_familiars = []
        
        # Create different types based on spirit's domain and specialties
        familiar_templates = self._get_familiar_templates()
        
        for i in range(min(count, len(familiar_templates))):
            template = familiar_templates[i]
            familiar = TaggedFamiliar(
                f"{self.name}_familiar_{i+1}",
                template["tags"]
            )
            
            # Auto-create optimal pact
            pact = pact_matcher.auto_create_optimal_pact(familiar, self)
            if pact:
                familiar.bind_pact(pact)
                self.manage_familiar(familiar)
                created_familiars.append(familiar)
        
        return created_familiars

class TaggedFamiliar(TaggedEntity):
    def __init__(self, name: str, tags: List[Tag] = None):
        base_tags = [Tag(TagCategory.TYPE, "familiar")]
        super().__init__(name, "familiar", base_tags + (tags or []))
        
        self.spirit: Optional['TaggedSpirit'] = None
        self.bound_pacts: List[TaggedPact] = []
        self.activity_log: List[Dict[str, Any]] = []
        self.current_goals: List[str] = []
    
    def can_perform_action(self, action: str) -> bool:
        """Check if familiar has permission to perform action"""
        permission_tag = f"permission:{action}"
        return self.tags.has_tag(permission_tag)
    
    def discover_interaction_opportunities(self) -> List[Dict[str, Any]]:
        """Find entities this familiar can meaningfully interact with"""
        opportunities = []
        
        # Find compatible entities
        compatible_entities = tag_registry.find_compatible_entities(self, 0.4)
        
        for entity in compatible_entities:
            interaction_types = self._determine_interaction_types(entity)
            if interaction_types:
                opportunities.append({
                    "entity": entity,
                    "interactions": interaction_types,
                    "compatibility": self.tags.compatibility_score(entity.tags)
                })
        
        return opportunities
    
    def _determine_interaction_types(self, other: TaggedEntity) -> List[str]:
        """Determine what interactions are possible with another entity"""
        interactions = []
        
        # Check for complementary abilities
        my_abilities = self.tags.get_tags_by_category(TagCategory.ABILITY)
        other_abilities = other.tags.get_tags_by_category(TagCategory.ABILITY)
        
        for my_ability in my_abilities:
            for other_ability in other_abilities:
                if my_ability.value == "healing" and other.tags.has_tag("status:wounded"):
                    interactions.append("heal")
                elif my_ability.value == "damage" and other.tags.has_tag("type:enemy"):
                    interactions.append("attack")
                elif my_ability.value == "support" and other.tags.has_tag("type:ally"):
                    interactions.append("assist")
        
        return interactions
```

#### **4.2 Emergent Behavior System**

python

```python
# grimoire/emergent_behavior.py
class EmergentBehaviorEngine:
    def __init__(self, tag_registry: TagRegistry):
        self.registry = tag_registry
        self.behavior_rules: List[BehaviorRule] = []
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
    
    def register_behavior_rule(self, rule: 'BehaviorRule') -> None:
        self.behavior_rules.append(rule)
    
    def process_emergent_behaviors(self) -> None:
        """Process all entities for emergent behavior opportunities"""
        all_entities = list(self.registry.entities.values())
        
        for entity in all_entities:
            if isinstance(entity, TaggedFamiliar):
                self._process_familiar_behaviors(entity)
            elif isinstance(entity, TaggedSpirit):
                self._process_spirit_behaviors(entity)
            elif isinstance(entity, TaggedArchon):
                self._process_archon_behaviors(entity)
    
    def _process_familiar_behaviors(self, familiar: TaggedFamiliar) -> None:
        """Process emergent behaviors for a familiar"""
        # Find interaction opportunities
        opportunities = familiar.discover_interaction_opportunities()
        
        # Apply behavior rules
        for rule in self.behavior_rules:
            if rule.applies_to(familiar):
                actions = rule.suggest_actions(familiar, opportunities)
                for action in actions:
                    if familiar.can_perform_action(action["type"]):
                        self._execute_emergent_action(familiar, action)

class BehaviorRule:
    def __init__(self, name: str, trigger_tags: List[str], 
                 priority: int = 1):
        self.name = name
        self.trigger_tags = trigger_tags
        self.priority = priority
    
    def applies_to(self, entity: TaggedEntity) -> bool:
        return entity.tags.matches_all(self.trigger_tags)
    
    def suggest_actions(self, entity: TaggedEntity, 
                       opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Override in subclasses to define specific behavior"""
        return []

class HealingBehaviorRule(BehaviorRule):
    def __init__(self):
        super
```

Retry

SM

Continue

Edit

3 / 3

python

```python
class HealingBehaviorRule(BehaviorRule):
   def __init__(self):
       super().__init__("healing_behavior", ["ability:healing"], priority=3)
   
   def suggest_actions(self, entity: TaggedEntity, 
                      opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
       actions = []
       
       for opportunity in opportunities:
           target = opportunity["entity"]
           if "heal" in opportunity["interactions"]:
               # Priority based on target's wound severity and relationship
               priority = self._calculate_healing_priority(entity, target)
               actions.append({
                   "type": "heal",
                   "target": target,
                   "priority": priority,
                   "estimated_cost": self._estimate_healing_cost(target)
               })
       
       return sorted(actions, key=lambda x: x["priority"], reverse=True)
   
   def _calculate_healing_priority(self, healer: TaggedEntity, 
                                  target: TaggedEntity) -> float:
       priority = 0.5  # Base priority
       
       # Higher priority for allies
       if target.tags.has_tag("type:ally"):
           priority += 0.3
       
       # Higher priority for leaders
       if target.tags.has_tag("role:leader"):
           priority += 0.2
       
       # Higher priority for critical wounds
       if target.tags.has_tag("status:critical"):
           priority += 0.4
       
       # Compatibility bonus
       compatibility = healer.tags.compatibility_score(target.tags)
       priority += compatibility * 0.2
       
       return min(priority, 1.0)

class CombatBehaviorRule(BehaviorRule):
   def __init__(self):
       super().__init__("combat_behavior", ["ability:damage"], priority=2)
   
   def suggest_actions(self, entity: TaggedEntity, 
                      opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
       actions = []
       
       for opportunity in opportunities:
           target = opportunity["entity"]
           if "attack" in opportunity["interactions"]:
               threat_level = self._assess_threat_level(target)
               actions.append({
                   "type": "attack",
                   "target": target,
                   "priority": threat_level,
                   "estimated_damage": self._estimate_damage_output(entity, target)
               })
       
       return sorted(actions, key=lambda x: x["priority"], reverse=True)
   
   def _assess_threat_level(self, target: TaggedEntity) -> float:
       threat = 0.3  # Base threat
       
       if target.tags.has_tag("type:enemy"):
           threat += 0.4
       
       if target.tags.has_tag("ability:damage"):
           threat += 0.2
       
       if target.tags.has_tag("role:leader"):
           threat += 0.3
       
       return min(threat, 1.0)

# Register default behavior rules
emergent_engine = EmergentBehaviorEngine(tag_registry)
emergent_engine.register_behavior_rule(HealingBehaviorRule())
emergent_engine.register_behavior_rule(CombatBehaviorRule())
```

#### **4.3 Enhanced Agent Creation Syntax**

grimoire

```grimoire
# Auto-recruiting archon
bind war_archon = create_auto_archon upon $SCROLL(WarMaster),
    domain: $TAG(domain:combat),
    tags: [$TAG(specialty:tactics), $TAG(behavior:aggressive)],
    auto_recruit: true,
    max_spirits: 3

# Self-organizing spirit
bind battle_spirit = create_adaptive_spirit upon $SCROLL(BattleLeader),
    tags: [$TAG(domain:combat), $TAG(role:tactical), $TAG(specialty:frontline)],
    auto_create_familiars: 2,
    behavior_rules: ["combat_behavior", "protection_behavior"]

# Emergent familiar
bind scout_familiar = create_emergent_familiar upon 
    tags: [$TAG(ability:stealth), $TAG(role:scout), $TAG(behavior:cautious)],
    emergence_priority: $TAG(behavior:adaptive)
```

---

## 📊 Phase 5: Monitoring and Analytics Enhancement (Weeks 13-14)

### **Objective**

Upgrade the Familiar Wrangler system to provide tag-based monitoring, analytics, and visualization.

### **Deliverables**

#### **5.1 Tag-Aware Monitoring System**

python

```python
# grimoire/enhanced_wrangler.py
class EnhancedFamiliarWrangler:
    def __init__(self):
        self.activity_logs: Dict[str, List[Dict[str, Any]]] = {}
        self.tag_analytics: TagAnalytics = TagAnalytics()
        self.behavior_tracker: BehaviorTracker = BehaviorTracker()
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
    
    def enable_tag_based_reporting(self, tag_patterns: List[str], 
                                  report_types: List[str]) -> None:
        """Enable reporting for all entities matching tag patterns"""
        matching_entities = tag_registry.query_by_tags(tag_patterns)
        
        for entity in matching_entities:
            self.enable_reporting(entity.true_name, report_types)
            # Add tag-specific metadata to reports
            self._add_tag_metadata(entity)
    
    def get_analytics_by_tags(self, tag_patterns: List[str]) -> Dict[str, Any]:
        """Get comprehensive analytics for entities matching tags"""
        matching_entities = tag_registry.query_by_tags(tag_patterns)
        
        analytics = {
            "entity_count": len(matching_entities),
            "tag_distribution": self.tag_analytics.get_tag_distribution(matching_entities),
            "performance_summary": self._get_performance_summary(matching_entities),
            "interaction_patterns": self._analyze_interaction_patterns(matching_entities),
            "emergent_behaviors": self._track_emergent_behaviors(matching_entities)
        }
        
        return analytics
    
    def get_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """Generate compatibility matrix for all entities"""
        all_entities = list(tag_registry.entities.values())
        matrix = {}
        
        for entity1 in all_entities:
            matrix[entity1.true_name] = {}
            for entity2 in all_entities:
                if entity1.true_name != entity2.true_name:
                    compatibility = entity1.tags.compatibility_score(entity2.tags)
                    matrix[entity1.true_name][entity2.true_name] = compatibility
        
        return matrix
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Suggest optimizations based on tag analysis"""
        suggestions = []
        
        # Find underutilized entities
        underutilized = self._find_underutilized_entities()
        for entity in underutilized:
            suggestions.append({
                "type": "underutilized_entity",
                "entity": entity.name,
                "recommendation": "Consider adding more relevant tasks or removing",
                "tags": [tag.full_tag for tag in entity.tags.tags.values()]
            })
        
        # Find compatibility mismatches
        mismatches = self._find_compatibility_mismatches()
        for mismatch in mismatches:
            suggestions.append({
                "type": "compatibility_mismatch",
                "entities": [mismatch["entity1"].name, mismatch["entity2"].name],
                "recommendation": "Consider reassigning or adding bridging tags",
                "compatibility_score": mismatch["score"]
            })
        
        # Suggest beneficial tag additions
        tag_suggestions = self._suggest_beneficial_tags()
        suggestions.extend(tag_suggestions)
        
        return suggestions

class TagAnalytics:
    def get_tag_distribution(self, entities: List[TaggedEntity]) -> Dict[str, Any]:
        """Analyze tag distribution across entities"""
        category_counts = {}
        value_counts = {}
        tag_combinations = {}
        
        for entity in entities:
            for tag in entity.tags.tags.values():
                # Count by category
                if tag.category.value not in category_counts:
                    category_counts[tag.category.value] = 0
                category_counts[tag.category.value] += 1
                
                # Count by full tag
                if tag.full_tag not in value_counts:
                    value_counts[tag.full_tag] = 0
                value_counts[tag.full_tag] += 1
        
        # Find common tag combinations
        for entity in entities:
            entity_tags = sorted([tag.full_tag for tag in entity.tags.tags.values()])
            for i in range(len(entity_tags)):
                for j in range(i + 1, len(entity_tags)):
                    combo = (entity_tags[i], entity_tags[j])
                    if combo not in tag_combinations:
                        tag_combinations[combo] = 0
                    tag_combinations[combo] += 1
        
        return {
            "category_distribution": category_counts,
            "tag_frequency": value_counts,
            "common_combinations": sorted(tag_combinations.items(), 
                                       key=lambda x: x[1], reverse=True)[:10]
        }
    
    def calculate_tag_effectiveness(self, tag: str) -> float:
        """Calculate how effective a tag is based on entity performance"""
        entities_with_tag = tag_registry.query_by_tags([tag])
        entities_without_tag = [e for e in tag_registry.entities.values() 
                              if not e.tags.has_tag(tag)]
        
        if not entities_with_tag or not entities_without_tag:
            return 0.5  # Neutral effectiveness
        
        # Compare performance metrics
        with_tag_performance = self._average_performance(entities_with_tag)
        without_tag_performance = self._average_performance(entities_without_tag)
        
        # Return relative effectiveness (0.0 to 1.0)
        return min(max(with_tag_performance / (without_tag_performance + 0.1), 0.0), 1.0)

class BehaviorTracker:
    def __init__(self):
        self.behavior_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.interaction_history: List[Dict[str, Any]] = []
    
    def track_behavior(self, entity: TaggedEntity, behavior: str, 
                      context: Dict[str, Any]) -> None:
        """Track a behavior instance"""
        if entity.true_name not in self.behavior_patterns:
            self.behavior_patterns[entity.true_name] = []
        
        self.behavior_patterns[entity.true_name].append({
            "behavior": behavior,
            "timestamp": time.time(),
            "context": context,
            "entity_tags": [tag.full_tag for tag in entity.tags.tags.values()]
        })
    
    def analyze_behavior_trends(self, entity: TaggedEntity) -> Dict[str, Any]:
        """Analyze behavior trends for an entity"""
        if entity.true_name not in self.behavior_patterns:
            return {"trends": [], "frequency": {}, "effectiveness": {}}
        
        patterns = self.behavior_patterns[entity.true_name]
        
        # Calculate behavior frequency
        frequency = {}
        for pattern in patterns:
            behavior = pattern["behavior"]
            if behavior not in frequency:
                frequency[behavior] = 0
            frequency[behavior] += 1
        
        # Analyze effectiveness (simplified)
        effectiveness = {}
        for behavior in frequency.keys():
            effectiveness[behavior] = self._calculate_behavior_effectiveness(
                entity, behavior, patterns
            )
        
        return {
            "total_behaviors": len(patterns),
            "frequency": frequency,
            "effectiveness": effectiveness,
            "recent_trend": self._calculate_recent_trend(patterns)
        }
```

#### **5.2 Enhanced Monitoring Syntax**

grimoire

```grimoire
# Tag-based monitoring
enable_tag_monitoring([$TAG(domain:combat)], ["command", "environmental", "interactions"])
enable_tag_monitoring([$TAG(ability:healing)], ["healing_events", "resource_usage"])

# Analytics queries
bind combat_analytics = get_analytics_by_tags([$TAG(domain:combat)])
bind healer_performance = get_performance_by_tags([$TAG(ability:healing)])

# Optimization suggestions
bind suggestions = get_optimization_suggestions()
for suggestion in suggestions:
    scry $CRYSTAL("Optimization: " + suggestion.recommendation)

# Compatibility analysis
bind compatibility_matrix = get_compatibility_matrix()
bind most_compatible = find_most_compatible_pair()
scry $SCROLL("Most compatible entities: " + most_compatible.entity1 + " and " + most_compatible.entity2)
```

---

## 🎯 Phase 6: Documentation and Integration Testing (Weeks 15-16)

### **Objective**

Complete comprehensive documentation, testing, and integration validation.

### **Deliverables**

#### **6.1 Comprehensive Documentation**

markdown

````markdown
# Grimoire Tag System Documentation

## Overview
The Grimoire Tag System revolutionizes entity identification, interaction, and behavior management through flexible, hierarchical tagging.

## Core Concepts

### Tags
Tags are immutable identifiers that categorize entities by:
- **Domain**: Primary operational area (combat, support, economy)
- **Role**: Hierarchical position (leader, support, operative)
- **Ability**: Capabilities (healing, damage, stealth)
- **Type**: Entity classification (archon, spirit, familiar)
- **Status**: Current state (active, idle, combat)
- **Permission**: Granted actions (heal, attack, trade)

### Tag Syntax
```grimoire
# Tag literals
$TAG(category:value)
$TAG(domain:combat)
$TAG(ability:healing)

# Tag queries
query_by_tags([$TAG(domain:combat), $TAG(status:active)])
find_compatible(entity, min_compatibility: 0.7)
````

### Advanced Features

#### Emergent Behavior

Entities with compatible tags automatically discover interaction opportunities:

grimoire

```grimoire
# Automatic healing behavior
bind healer = create_familiar upon tags: [$TAG(ability:healing)]
bind wounded = create_familiar upon tags: [$TAG(status:wounded)]
# Healer automatically detects and attempts to heal wounded entities
```

#### Dynamic Pact Creation

Pacts are created based on tag compatibility:

grimoire

```grimoire
# Template-based pacts
create_pact_template upon $SCROLL(support_template),
    entity_tags: [$TAG(ability:healing)],
    spirit_tags: [$TAG(domain:support)],
    grants: [$TAG(permission:heal)]
```

#### Performance Analytics

Comprehensive monitoring by tag categories:

grimoire

```grimoire
bind analytics = get_analytics_by_tags([$TAG(domain:combat)])
scry $CRYSTAL("Combat entities performance: " + analytics.efficiency)
```

## Migration Guide

### From Hard-Coded to Tag-Based

grimoire

```grimoire
# Old approach
create_spirit("Healer", "Support", ["healing"])

# New approach
create_spirit upon $SCROLL(Healer),
    tags: [$TAG(domain:support), $TAG(ability:healing), $TAG(role:tactical)]
```

### Best Practices

1. Use consistent tag vocabularies
2. Combine general and specific tags
3. Leverage tag hierarchies for organization
4. Monitor tag effectiveness with analytics
5. Use emergent behavior for natural interactions

````

#### **6.2 Comprehensive Test Suite**
```python
# tests/test_tag_system.py
import pytest
from grimoire.tag_system import Tag, TagSet, TagCategory, TagRegistry
from grimoire.tagged_agents import TaggedFamiliar, TaggedSpirit, TaggedArchon
from grimoire.enhanced_pact_system import TaggedPact, PactTemplate

class TestTagSystem:
    def test_tag_creation_and_matching(self):
        """Test basic tag functionality"""
        tag = Tag(TagCategory.DOMAIN, "combat")
        assert tag.full_tag == "domain:combat"
        assert tag.matches("domain:combat")
        assert tag.matches("domain:*")
        assert not tag.matches("role:combat")
    
    def test_tag_set_operations(self):
        """Test tag set functionality"""
        tags = TagSet([
            Tag(TagCategory.DOMAIN, "combat"),
            Tag(TagCategory.ABILITY, "healing")
        ])
        
        assert tags.has_tag("domain:combat")
        assert tags.has_tag("ability:healing")
        assert not tags.has_tag("role:leader")
        
        assert tags.matches_all(["domain:combat", "ability:healing"])
        assert not tags.matches_all(["domain:combat", "role:leader"])
    
    def test_entity_tag_queries(self):
        """Test entity querying by tags"""
        registry = TagRegistry()
        
        # Create test entities
        warrior = TaggedFamiliar("Warrior", [
            Tag(TagCategory.DOMAIN, "combat"),
            Tag(TagCategory.ABILITY, "damage")
        ])
        healer = TaggedFamiliar("Healer", [
            Tag(TagCategory.DOMAIN, "support"),
            Tag(TagCategory.ABILITY, "healing")
        ])
        
        registry.register_entity(warrior)
        registry.register_entity(healer)
        
        # Test queries
        combat_entities = registry.query_by_tags(["domain:combat"])
        assert len(combat_entities) == 1
        assert combat_entities[0].name == "Warrior"
        
        healers = registry.query_by_tags(["ability:healing"])
        assert len(healers) == 1
        assert healers[0].name == "Healer"
    
    def test_compatibility_scoring(self):
        """Test compatibility calculations"""
        warrior_tags = TagSet([
            Tag(TagCategory.DOMAIN, "combat"),
            Tag(TagCategory.ROLE, "damage_dealer")
        ])
        
        healer_tags = TagSet([
            Tag(TagCategory.DOMAIN, "support"),
            Tag(TagCategory.ROLE, "healer")
        ])
        
        score = warrior_tags.compatibility_score(healer_tags)
        assert 0.0 <= score <= 1.0
    
    def test_pact_matching(self):
        """Test automatic pact creation"""
        spirit = TaggedSpirit("SupportSpirit", "support", ["healing"])
        familiar = TaggedFamiliar("Healer", [
            Tag(TagCategory.ABILITY, "healing"),
            Tag(TagCategory.TYPE, "familiar")
        ])
        
        template = PactTemplate("healing_template")
        template.required_entity_tags = ["ability:healing", "type:familiar"]
        template.required_spirit_tags = ["domain:support"]
        template.granted_permissions = ["heal", "access_mana"]
        
        pact = template.instantiate_for_spirit(spirit)
        assert pact.can_bind_entity(familiar)
    
    def test_emergent_behavior(self):
        """Test emergent behavior discovery"""
        healer = TaggedFamiliar("Healer", [
            Tag(TagCategory.ABILITY, "healing")
        ])
        
        wounded = TaggedFamiliar("Wounded", [
            Tag(TagCategory.STATUS, "wounded")
        ])
        
        tag_registry.register_entity(healer)
        tag_registry.register_entity(wounded)
        
        opportunities = healer.discover_interaction_opportunities()
        assert len(opportunities) > 0
        assert any("heal" in opp["interactions"] for opp in opportunities)

class TestAgentIntegration:
    def test_archon_spirit_recruitment(self):
        """Test automatic spirit recruitment"""
        archon = TaggedArchon("WarMaster", "combat", ["defend_territory"])
        spirit = TaggedSpirit("Infantry", "combat", ["frontline"])
        
        tag_registry.register_entity(archon)
        tag_registry.register_entity(spirit)
        
        compatible_spirits = archon.discover_compatible_spirits()
        assert spirit in compatible_spirits
    
    def test_spirit_familiar_creation(self):
        """Test automatic familiar creation"""
        spirit = TaggedSpirit("Healer", "support", ["healing"])
        familiars = spirit.auto_create_familiars(2)
        
        assert len(familiars) == 2
        for familiar in familiars:
            assert familiar.spirit == spirit
            assert len(familiar.bound_pacts) > 0

class TestPerformanceMetrics:
    def test_analytics_generation(self):
        """Test analytics system"""
        # Create test ecosystem
        entities = []
        for i in range(10):
            familiar = TaggedFamiliar(f"TestEntity{i}", [
                Tag(TagCategory.DOMAIN, "combat" if i % 2 == 0 else "support"),
                Tag(TagCategory.ABILITY, "damage" if i % 3 == 0 else "healing")
            ])
            entities.append(familiar)
            tag_registry.register_entity(familiar)
        
        wrangler = EnhancedFamiliarWrangler()
        analytics = wrangler.get_analytics_by_tags(["domain:combat"])
        
        assert "entity_count" in analytics
        assert "tag_distribution" in analytics
        assert analytics["entity_count"] == 5  # Half should be combat
    
    def test_optimization_suggestions(self):
        """Test optimization suggestion system"""
        wrangler = EnhancedFamiliarWrangler()
        suggestions = wrangler.suggest_optimizations()
        
        assert isinstance(suggestions, list)
        # Should have suggestions for test entities
        assert len(suggestions) >= 0

# Integration tests
class TestFullIntegration:
    def test_complete_ecosystem(self):
        """Test complete tag-based ecosystem"""
        # Create archon
        archon = TaggedArchon("EmpireLeader", "economy", ["maximize_trade"])
        
        # Auto-recruit spirits
        archon.auto_recruit_spirits(3)
        
        # Spirits auto-create familiars
        for spirit in archon.managed_spirits:
            spirit.auto_create_familiars(2)
        
        # Process emergent behaviors
        emergent_engine.process_emergent_behaviors()
        
        # Verify ecosystem is functional
        assert len(archon.managed_spirits) <= 3
        total_familiars = sum(len(spirit.managed_familiars) 
                            for spirit in archon.managed_spirits)
        assert total_familiars <= 6  # 3 spirits * 2 familiars each
    
    def test_cross_domain_interactions(self):
        """Test interactions between different domains"""
        # Create entities from different domains
        combat_familiar = TaggedFamiliar("Warrior", [
            Tag(TagCategory.DOMAIN, "combat"),
            Tag(TagCategory.STATUS, "wounded")
        ])
        
        support_familiar = TaggedFamiliar("Medic", [
            Tag(TagCategory.DOMAIN, "support"),
            Tag(TagCategory.ABILITY, "healing")
        ])
        
        tag_registry.register_entity(combat_familiar)
        tag_registry.register_entity(support_familiar)
        
        # Test cross-domain interaction discovery
        opportunities = support_familiar.discover_interaction_opportunities()
        healing_opportunities = [opp for opp in opportunities 
                               if "heal" in opp["interactions"]]
        
        assert len(healing_opportunities) > 0
        assert any(opp["entity"] == combat_familiar for opp in healing_opportunities)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
````

#### **6.3 Performance Benchmarks**

python

```python
# benchmarks/tag_performance.py
import time
import random
from grimoire.tag_system import Tag, TagRegistry, TagCategory
from grimoire.tagged_agents import TaggedFamiliar

def benchmark_tag_queries():
    """Benchmark tag query performance"""
    registry = TagRegistry()
    
    # Create large number of entities
    entity_count = 10000
    for i in range(entity_count):
        tags = [
            Tag(TagCategory.DOMAIN, random.choice(["combat", "support", "economy"])),
            Tag(TagCategory.ABILITY, random.choice(["healing", "damage", "stealth"])),
            Tag(TagCategory.ROLE, random.choice(["leader", "support", "scout"]))
        ]
        entity = TaggedFamiliar(f"Entity{i}", tags)
        registry.register_entity(entity)
    
    # Benchmark different query types
    print(f"Created {entity_count} entities")
    
    # Single tag query
    start_time = time.time()
    results = registry.query_by_tags(["domain:combat"])
    single_tag_time = time.time() - start_time
    print(f"Single tag query: {single_tag_time:.4f}s, {len(results)} results")
    
    # Multi-tag query
    start_time = time.time()
    results = registry.query_by_tags(["domain:combat", "ability:damage"])
    multi_tag_time = time.time() - start_time
    print(f"Multi-tag query: {multi_tag_time:.4f}s, {len(results)} results")
    
    # Compatibility search
    test_entity = TaggedFamiliar("TestEntity", [
        Tag(TagCategory.DOMAIN, "support"),
        Tag(TagCategory.ABILITY, "healing")
    ])
    
    start_time = time.time()
    compatible = registry.find_compatible_entities(test_entity, 0.5)
    compatibility_time = time.time() - start_time
    print(f"Compatibility search: {compatibility_time:.4f}s, {len(compatible)} results")

if __name__ == "__main__":
    benchmark_tag_queries()
```

---

## 📈 Success Metrics and Validation

### **Functional Success Criteria**

1. ✅ **Tag System Core**: Full tag creation, matching, and querying functionality
2. ✅ **Language Integration**: Seamless syntax integration with existing Grimoire
3. ✅ **Agent Enhancement**: All agent types support tag-based operations
4. ✅ **Emergent Behavior**: Entities autonomously discover and engage in interactions
5. ✅ **Performance**: Sub-100ms query response for 1000+ entity ecosystems

### **Performance Benchmarks**

- **Query Performance**: <50ms for complex multi-tag queries on 1000 entities
- **Memory Efficiency**: <2MB additional memory overhead for tag system
- **Compatibility Calculation**: <10ms for pairwise compatibility scoring
- **Emergent Behavior Processing**: <100ms per entity per cycle

### **Integration Validation**

1. **Backward Compatibility**: All existing Grimoire code continues to function
2. **Migration Path**: Clear upgrade path from hard-coded to tag-based entities
3. **Documentation Completeness**: Full API documentation and tutorials
4. **Test Coverage**: >90% code coverage with comprehensive test suite

---

## 🚀 Deployment and Rollout Strategy

### **Phase Deployment Plan**

#### **Alpha Release (Phase 1-2 Complete)**

- Core tag system for internal testing
- Basic language syntax integration
- Limited to development team

#### **Beta Release (Phase 3-4 Complete)**

- Enhanced pact system
- Agent system upgrades
- Selected external developers

#### **Production Release (All Phases Complete)**

- Full feature set
- Comprehensive documentation
- Public availability

### **Migration Support**

grimoire

```grimoire
# Automatic migration utilities
migrate_legacy_entities()  # Convert existing hard-coded entities
validate_tag_consistency()  # Check for tag conflicts
optimize_tag_structure()   # Suggest tag improvements
```

### **Training and Adoption**

1. **Developer Workshops**: Hands-on tag system training
2. **Example Projects**: Complete tag-based game examples
3. **Best Practices Guide**: Comprehensive tag design patterns
4. **Community Support**: Forums and documentation wikis

---

## 🔮 Future Enhancements (Post-Implementation)

### **Advanced Tag Features**

1. **Tag Hierarchies**: Parent-child tag relationships
2. **Dynamic Tags**: Tags that change based on experience/performance
3. **Tag Inheritance**: Automatic tag propagation in entity hierarchies
4. **Weighted Tags**: Tags with importance/confidence scores

### **AI/ML Integration**

1. **Tag Recommendation**: ML-based tag suggestions for new entities
2. **Behavior Prediction**: Predict entity behavior based on tag patterns
3. **Optimization Learning**: Automatically optimize tag configurations
4. **Pattern Recognition**: Discover emergent tag interaction patterns

### **Visualization and Tooling**

1. **Tag Relationship Graphs**: Visual entity relationship mapping
2. **Performance Dashboards**: Real-time tag system analytics
3. **Debug Visualizations**: Tag-based debugging interfaces
4. **IDE Integration**: Smart tag completion and validation

---

## 💰 Resource Requirements

### **Development Resources**

- **Lead Developer**: 16 weeks full-time (system architecture and core implementation)
- **Language Developer**: 12 weeks (lexer/parser/interpreter integration)
- **Testing Engineer**: 8 weeks (test suite development and validation)
- **Documentation Specialist**: 4 weeks (comprehensive documentation)

### **Infrastructure Requirements**

- **Development Environment**: Enhanced Python development stack
- **Testing Infrastructure**: Automated testing pipeline with performance monitoring
- **Documentation Platform**: Comprehensive API documentation and tutorials