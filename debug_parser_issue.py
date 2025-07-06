#!/usr/bin/env python3
"""Debug script to analyze the parser issue with tag system conditionals."""

from grimoire.lexer import GrimoireLexer
from grimoire.parser import GrimoireParser

def debug_parser_issue():
    """Debug the specific parser issue with tag conditionals."""
    
    # The problematic code from the user
    code = '''
# Add tags individually (if add_tag function exists)
wizard_player.add_tag upon $TAG(type:familiar)
wizard_player.add_tag upon $TAG(role:player)
wizard_player.add_tag upon $TAG(class:wizard)
wizard_player.add_tag upon $TAG(domain:magic)
wizard_player.add_tag upon $TAG(ability:spellcasting)
wizard_player.add_tag upon $TAG(ability:fireball)
wizard_player.add_tag upon $TAG(ability:heal)
wizard_player.add_tag upon $TAG(ability:teleport)
wizard_player.add_tag upon $TAG(behavior:curious)
wizard_player.add_tag upon $TAG(status:healthy)
wizard_player.add_tag upon $TAG(level:novice)
wizard_player.add_tag upon $TAG(resource:mana)
wizard_player.add_tag upon $TAG(specialty:evocation)
wizard_player.add_tag upon $TAG(permission:cast_spells)
wizard_player.add_tag upon $TAG(permission:use_items)

scry $SCROLL(Wizard created and tagged)

# Create monster using same approach
bind orc_monster = conjure_familiar upon $SCROLL(Grashk the Brutal)
orc_monster.add_tag upon $TAG(type:familiar)
orc_monster.add_tag upon $TAG(role:enemy)
orc_monster.add_tag upon $TAG(species:orc)
orc_monster.add_tag upon $TAG(domain:combat)
orc_monster.add_tag upon $TAG(ability:melee_attack)
orc_monster.add_tag upon $TAG(ability:intimidate)
orc_monster.add_tag upon $TAG(weakness:magic)

scry $SCROLL(Orc monster created and tagged)

# Create loot item
bind fire_staff = conjure_familiar upon $SCROLL(Staff of Eternal Flames)
fire_staff.add_tag upon $TAG(type:item)
fire_staff.add_tag upon $TAG(category:weapon)
fire_staff.add_tag upon $TAG(rarity:rare)
fire_staff.add_tag upon $TAG(element:fire)
fire_staff.add_tag upon $TAG(requirement:wizard)

scry $SCROLL(Fire staff created and tagged)

# Test tag-based queries (if implemented)
bind wizards = seek_mark upon $TAG(class:wizard)
scry $SCROLL(Found wizard entities)

bind combat_entities = seek_mark upon $TAG(domain:combat)
scry $SCROLL(Found combat entities)

# Test tag checking
should wizard_player.bears_mark upon $TAG(ability:fireball):
    scry $SCROLL(Wizard can cast fireball)

should orc_monster.bears_mark upon $TAG(weakness:magic):
    scry $SCROLL(Orc is vulnerable to magic)
'''
    
    print("Tokenizing code...")
    lexer = GrimoireLexer(code)
    tokens = lexer.scan_tokens()
    
    print(f"\nGenerated {len(tokens)} tokens:")
    for i, token in enumerate(tokens):
        print(f"{i:3d}: {token.type.name:20} | {repr(token.lexeme):20} | {repr(token.literal)}")
    
    print("\n" + "="*80 + "\n")
    
    print("Parsing code...")
    try:
        parser = GrimoireParser(tokens)
        ast = parser.parse()
        print("✅ Parse successful!")
        
        # Print AST structure
        print("\nAST Structure:")
        for i, stmt in enumerate(ast.statements):
            print(f"Statement {i}: {type(stmt).__name__}")
            if hasattr(stmt, 'expression'):
                print(f"  Expression: {type(stmt.expression).__name__}")
    
    except Exception as e:
        print(f"❌ Parse failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try to show where the parser failed
        if hasattr(e, 'token'):
            print(f"Failed at token: {e.token.type.name} '{e.token.lexeme}' at line {e.token.line}, column {e.token.column}")

if __name__ == "__main__":
    debug_parser_issue()