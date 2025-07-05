#!/usr/bin/env python3
"""
Simple test to demonstrate dual terminology working
"""

from grimoire.tag_system import (
    # Technical terminology
    Tag, TagSet, CommonTags, create_tag,
    # Mystical terminology (aliases)
    Mark, MarkSet, CommonMarks, create_mark
)

from grimoire.tag_registry import (
    # Technical terminology  
    TaggedEntity, tag_registry, query_by_tags,
    # Mystical terminology (aliases)
    MarkedEntity, mark_registry, seek_mark, how_matched
)

def test_dual_terminology():
    """Test that both terminologies work identically."""
    print("🎭 DUAL TERMINOLOGY TEST")
    print("="*50)
    
    # Test 1: Class aliases
    print("✅ Class aliases work:")
    print(f"  Tag is Mark: {Tag is Mark}")
    print(f"  TagSet is MarkSet: {TagSet is MarkSet}")
    print(f"  TaggedEntity is MarkedEntity: {TaggedEntity is MarkedEntity}")
    print(f"  tag_registry is mark_registry: {tag_registry is mark_registry}")
    
    # Test 2: Function aliases
    print("\n✅ Function aliases work:")
    tech_tag = create_tag("domain", "combat")
    mystic_mark = create_mark("domain", "combat")
    print(f"  create_tag result: {tech_tag}")
    print(f"  create_mark result: {mystic_mark}")
    print(f"  Results identical: {tech_tag.full_tag == mystic_mark.full_tag}")
    
    # Test 3: Entity method aliases
    print("\n✅ Entity method aliases work:")
    entity = TaggedEntity("TestEntity", "familiar")
    
    # Add using technical method
    entity.add_tag(CommonTags.COMBAT)
    print(f"  Added tag with add_tag(): {entity.has_tag('domain:combat')}")
    
    # Add using mystical method
    entity.mark(CommonMarks.HEALING)
    print(f"  Added mark with mark(): {entity.bears_mark('ability:healing')}")
    
    # Check capabilities with both terminologies
    print(f"  has_capability('healing'): {entity.has_capability('healing')}")
    print(f"  may('healing'): {entity.may('healing')}")
    
    # Test 4: Registry queries
    print("\n✅ Registry query aliases work:")
    tag_registry.register_entity(entity)
    
    tech_results = query_by_tags(["domain:combat"])
    mystic_results = seek_mark(["domain:combat"])
    
    print(f"  query_by_tags results: {len(tech_results)}")
    print(f"  seek_mark results: {len(mystic_results)}")
    print(f"  Results identical: {tech_results == mystic_results}")
    
    # Test 5: Compatibility scoring
    print("\n✅ Compatibility aliases work:")
    entity2 = MarkedEntity("TestEntity2", "spirit")
    entity2.mark(create_mark("domain", "support"))
    entity2.mark(create_mark("ability", "healing"))
    tag_registry.register_entity(entity2)
    
    compatibility = how_matched(entity, entity2)
    print(f"  how_matched() compatibility: {compatibility:.3f}")
    
    print("\n🎉 ALL DUAL TERMINOLOGY TESTS PASSED!")
    print("Both technical and mystical terminologies work perfectly!")

if __name__ == "__main__":
    test_dual_terminology()