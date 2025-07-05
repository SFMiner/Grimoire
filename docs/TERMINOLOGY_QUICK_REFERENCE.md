# Grimoire Dual Terminology Quick Reference

## 🎭 Choose Your Style

| **Technical** | **Mystical** | **Description** |
|---------------|--------------|-----------------|
| `Tag` | `Mark` | Entity attribute |
| `TaggedEntity` | `MarkedEntity` | Entity with attributes |
| `TagSet` | `MarkSet` | Collection of attributes |
| `TagRegistry` | `MarkRegistry` | Central registry |

## 🔧 Methods & Functions

| **Technical** | **Mystical** | **Purpose** |
|---------------|--------------|-------------|
| `add_tag()` | `mark()` | Add attribute |
| `remove_tag()` | `unmark()` | Remove attribute |
| `has_tag()` | `bears_mark()` | Check attribute |
| `has_capability()` | `may()` | Check ability |
| `query_by_tags()` | `seek_mark()` | Find entities |
| `find_compatible()` | `seek_match()` | Find matches |
| `get_entities_by_type()` | `gather_kind()` | Get by type |
| `suggest_tags()` | `suggest_marks()` | Get suggestions |

## 🪄 Agent Creation

| **Technical** | **Mystical** | **Creates** |
|---------------|--------------|-------------|
| `create_familiar` | `conjure_familiar` | Familiar agent |
| `create_spirit` | `conjure_spirit` | Spirit agent |
| `create_archon` | `conjure_archon` | Archon agent |
| `create_familiar_with_pact` | `conjure_familiar_with_pact` | Familiar with pact |

## 📝 Quick Examples

### Technical Style
```python
warrior = TaggedEntity("Warrior", "familiar")
warrior.add_tag(create_tag("domain", "combat"))
results = query_by_tags(["domain:combat"])
```

### Mystical Style  
```python
warrior = MarkedEntity("Warrior", "familiar")
warrior.mark(create_mark("domain", "combat"))
results = seek_mark(["domain:combat"])
```

### Mixed Style
```python
warrior = TaggedEntity("Warrior", "familiar")
warrior.mark(create_mark("domain", "combat"))
results = seek_mark(["domain:combat"])
```

## ✨ Key Benefits

- ✅ **Zero Performance Difference**
- ✅ **Complete Feature Parity**
- ✅ **Full Backward Compatibility**
- ✅ **Mix and Match Freely**
- ✅ **Choose Your Preference**

## 🎯 When to Use

| **Technical** | **Mystical** | **Mixed** |
|---------------|--------------|-----------|
| Enterprise projects | Game development | Migration projects |
| Integration code | Creative coding | Team preferences |
| Documentation | Immersive projects | Context-based |
| Conventional teams | Educational use | Personal choice |

Both terminologies are **production-ready** and **completely equivalent**!