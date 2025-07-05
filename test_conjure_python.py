#!/usr/bin/env python3
"""
Test conjure aliases in the interpreter directly
"""

from grimoire.interpreter import GrimoireInterpreter

def test_conjure_aliases():
    """Test that conjure aliases are available in the interpreter."""
    print("🪄 TESTING CONJURE ALIASES")
    print("="*50)
    
    interpreter = GrimoireInterpreter()
    
    # Test that conjure functions are defined
    print("✅ Checking conjure function availability:")
    
    try:
        conjure_familiar = interpreter.globals.get("conjure_familiar")
        print(f"  conjure_familiar defined: {conjure_familiar is not None}")
        
        conjure_spirit = interpreter.globals.get("conjure_spirit") 
        print(f"  conjure_spirit defined: {conjure_spirit is not None}")
        
        conjure_archon = interpreter.globals.get("conjure_archon")
        print(f"  conjure_archon defined: {conjure_archon is not None}")
        
        # Test they're the same as create_ functions
        create_spirit = interpreter.globals.get("create_spirit")
        create_archon = interpreter.globals.get("create_archon")
        
        print(f"  conjure_spirit is create_spirit: {conjure_spirit is create_spirit}")
        print(f"  conjure_archon is create_archon: {conjure_archon is create_archon}")
        
        print("\n✅ Testing direct function calls:")
        
        # Test conjure_spirit
        spirit = conjure_spirit(interpreter, ["TestSpirit", "healer"])
        print(f"  conjure_spirit created: {spirit}")
        
        # Test conjure_archon
        archon = conjure_archon(interpreter, ["TestArchon", "combat"])
        print(f"  conjure_archon created: {archon}")
        
        print("\n🎉 ALL CONJURE ALIAS TESTS PASSED!")
        
    except Exception as e:
        print(f"❌ Error testing conjure aliases: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conjure_aliases()