#!/usr/bin/env python3
"""Test script to verify the container system works."""

from grimoire.interpreter import interpret_grimoire

def test_container_system():
    """Test that container creation and operations work correctly."""
    
    code = '''
    scry $SCROLL(Testing Container System)
    
    # Test Tome (array/list) creation
    bind my_tome = create_tome upon
    scry $SCROLL(Created empty tome)
    
    # Test Grimoire (dictionary) creation  
    bind my_grimoire = create_grimoire upon
    scry $SCROLL(Created empty grimoire)
    
    # Test Codex (set) creation
    bind my_codex = create_codex upon
    scry $SCROLL(Created empty codex)
    
    # Test Chronicle (ordered list) creation
    bind my_chronicle = create_chronicle upon
    scry $SCROLL(Created empty chronicle)
    
    # Test Vault (immutable tuple) creation
    bind my_vault = create_vault upon
    scry $SCROLL(Created empty vault)
    
    scry $SCROLL(All container types created successfully!)
    '''
    
    print("Testing container system...")
    print("Code:")
    print(code)
    print("\n" + "="*50 + "\n")
    
    success = interpret_grimoire(code)
    
    if success:
        print("\n✅ Container system test passed!")
    else:
        print("\n❌ Container system test failed!")
    
    return success

if __name__ == "__main__":
    test_container_system()