#!/usr/bin/env python3
"""
Test script to demonstrate Grimoire's thematic keyword variants system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from grimoire.keyword_variants import demonstrate_keyword_variants, ThematicCodeGenerator, MagicSchool


def test_basic_functionality():
    """Test that the thematic keywords are recognized by the lexer."""
    print("🧪 Testing Basic Keyword Variants Recognition")
    print("=" * 50)
    
    from grimoire.lexer import tokenize_grimoire
    
    # Test Light Magic keywords
    light_code = "bless health = 100\nilluminate $SCROLL(Healing!)"
    tokens = tokenize_grimoire(light_code)
    
    print("Light Magic Code:")
    print(light_code)
    print("\nTokens produced:")
    for token in tokens:
        if token.type.name not in ['NEWLINE', 'EOF']:
            print(f"  {token.type.name}: '{token.lexeme}'")
    
    print("\n" + "-" * 30)
    
    # Test Shadow Magic keywords  
    shadow_code = "hex soul = 50\nwhisper $SCROLL(Darkness falls!)"
    tokens = tokenize_grimoire(shadow_code)
    
    print("Shadow Magic Code:")
    print(shadow_code)
    print("\nTokens produced:")
    for token in tokens:
        if token.type.name not in ['NEWLINE', 'EOF']:
            print(f"  {token.type.name}: '{token.lexeme}'")


def test_code_conversion():
    """Test converting code between different magical schools."""
    print("\n\n🎨 Testing Code Style Conversion")
    print("=" * 50)
    
    generator = ThematicCodeGenerator()
    
    # Original code in neutral style
    neutral_code = """ritual healing_spell():
    bind patient_health = 75
    if enchanted patient_health is lesser than 100:
        strengthen patient_health by 25
        scry $SCROLL(Healing complete!)
    else cursed:
        scry $SCROLL(Already at full health!)"""
    
    print("Original Code (Neutral):")
    print(neutral_code)
    
    # Convert to different schools
    schools_to_test = [MagicSchool.LIGHT, MagicSchool.SHADOW, MagicSchool.ARCANE]
    
    for school in schools_to_test:
        converted = generator.convert_code(neutral_code, school)
        print(f"\n{school.name.title()} Magic Style:")
        print("-" * 25)
        print(converted)


def test_executable_variants():
    """Test that different keyword variants actually execute the same way."""
    print("\n\n⚡ Testing Executable Equivalence")
    print("=" * 50)
    
    from grimoire.interpreter import interpret_grimoire
    
    # Same logic using different magic schools
    test_codes = {
        "Neutral": """
ritual test():
    bind value = 10
    scry $SCROLL(Neutral: ) added to value
test upon""",
        
        "Light": """
blessing test():
    bless value = 10  
    illuminate $SCROLL(Light: ) added to value
test upon""",
        
        "Shadow": """
curse test():
    hex value = 10
    whisper $SCROLL(Shadow: ) added to value  
test upon"""
    }
    
    print("Executing equivalent code in different styles:")
    print()
    
    for style, code in test_codes.items():
        print(f"--- {style} Magic ---")
        try:
            interpret_grimoire(code)
        except Exception as e:
            print(f"Error in {style}: {e}")
        print()


def main():
    """Run all keyword variants demonstrations."""
    print("🧙‍♂️ GRIMOIRE KEYWORD VARIANTS SYSTEM DEMO")
    print("=" * 60)
    
    # Show the variants system info
    demonstrate_keyword_variants()
    
    # Test integration with lexer
    test_basic_functionality()
    
    # Test code conversion
    test_code_conversion()
    
    # Test execution equivalence
    test_executable_variants()
    
    print("\n✨ Keyword Variants Demo Complete! ✨")
    print("🎭 Same functionality, infinite magical expression! 🎭")


if __name__ == "__main__":
    main()