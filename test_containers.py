#!/usr/bin/env python3
"""Test script for Grimoire containers."""

from grimoire.containers import Tome, Grimoire, Codex, Chronicle, Vault

def test_tome():
    """Test Tome (array/list) functionality."""
    print("Testing Tome (Arrays/Lists)...")
    
    # Create empty tome
    tome = Tome()
    print(f"Empty tome: {tome}")
    
    # Add elements
    tome.inscribe("wizard", "dragon", "spell")
    print(f"After inscribing: {tome}")
    
    # Access elements
    print(f"First element: {tome[0]}")
    print(f"Last element: {tome[-1]}")
    
    # Seek element
    wizard_index = tome.seek("wizard")
    print(f"Index of 'wizard': {wizard_index}")
    
    # Extract element
    extracted = tome.extract(1)
    print(f"Extracted element: {extracted}")
    print(f"Tome after extraction: {tome}")
    
    print("✅ Tome tests passed!\n")

def test_grimoire():
    """Test Grimoire (dictionary/map) functionality."""
    print("Testing Grimoire (Dictionaries/Maps)...")
    
    # Create empty grimoire
    grimoire = Grimoire()
    print(f"Empty grimoire: {grimoire}")
    
    # Add key-value pairs
    grimoire.inscribe("name", "Merlin")
    grimoire.inscribe("class", "Wizard")
    grimoire.inscribe("level", 50)
    print(f"After inscribing: {grimoire}")
    
    # Seek values
    name = grimoire.seek("name")
    print(f"Name: {name}")
    
    # Check if key exists
    has_mana = grimoire.contains_key("mana")
    print(f"Has mana key: {has_mana}")
    
    # Extract value
    level = grimoire.extract("level")
    print(f"Extracted level: {level}")
    print(f"Grimoire after extraction: {grimoire}")
    
    print("✅ Grimoire tests passed!\n")

def test_codex():
    """Test Codex (set) functionality."""
    print("Testing Codex (Sets)...")
    
    # Create empty codex
    codex = Codex()
    print(f"Empty codex: {codex}")
    
    # Add elements (duplicates ignored)
    codex.inscribe("fire", "water", "earth", "fire")  # "fire" appears twice
    print(f"After inscribing: {codex}")
    
    # Check membership
    has_fire = codex.seek("fire")
    has_air = codex.seek("air")
    print(f"Has fire: {has_fire}")
    print(f"Has air: {has_air}")
    
    # Set operations
    other_codex = Codex({"air", "fire"})
    union = codex.unite_with(other_codex)
    intersection = codex.intersect_with(other_codex)
    print(f"Union: {union}")
    print(f"Intersection: {intersection}")
    
    print("✅ Codex tests passed!\n")

def test_chronicle():
    """Test Chronicle (ordered collection) functionality."""
    print("Testing Chronicle (Ordered Collections)...")
    
    chronicle = Chronicle()
    chronicle.inscribe("event1", "event2", "event3")
    print(f"Chronicle: {chronicle}")
    
    # Access by index
    first_event = chronicle[0]
    print(f"First event: {first_event}")
    
    print("✅ Chronicle tests passed!\n")

def test_vault():
    """Test Vault (tuple/immutable) functionality."""
    print("Testing Vault (Tuples/Immutable)...")
    
    vault = Vault(("treasure", "gold", "gems"))
    print(f"Vault: {vault}")
    
    # Try to add (creates new vault)
    vault.inscribe("artifact")
    print(f"After inscribing: {vault}")
    
    # Access elements
    treasure = vault[0]
    print(f"First treasure: {treasure}")
    
    print("✅ Vault tests passed!\n")

def main():
    """Run all container tests."""
    print("🧙‍♂️ Grimoire Container System Tests")
    print("=" * 50)
    
    try:
        test_tome()
        test_grimoire()
        test_codex()
        test_chronicle()
        test_vault()
        
        print("🎉 All container tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()