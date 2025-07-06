#!/usr/bin/env python3
"""Test script based on user's original Grimoire tag system demo."""

from grimoire.interpreter import interpret_grimoire

def test_user_script():
    """Test the user's original script with corrections."""
    
    code = '''
# Corrected Grimoire Tag System Demo
# Using actual function signatures from the repository

scry $SCROLL(Welcome to the Corrected Tag System Adventure)

# Create wizard familiar
bind wizard_player = conjure_familiar upon $SCROLL(Eldric the Wise)

# Add tags individually using valid categories
wizard_player.add_tag upon $TAG(type:familiar)
wizard_player.add_tag upon $TAG(role:player)
wizard_player.add_tag upon $TAG(type:wizard)
wizard_player.add_tag upon $TAG(domain:magic)
wizard_player.add_tag upon $TAG(ability:spellcasting)
wizard_player.add_tag upon $TAG(ability:fireball)
wizard_player.add_tag upon $TAG(ability:heal)
wizard_player.add_tag upon $TAG(ability:teleport)
wizard_player.add_tag upon $TAG(behavior:curious)
wizard_player.add_tag upon $TAG(status:healthy)
wizard_player.add_tag upon $TAG(priority:normal)
wizard_player.add_tag upon $TAG(resource:mana)
wizard_player.add_tag upon $TAG(specialty:evocation)
wizard_player.add_tag upon $TAG(permission:cast_spells)
wizard_player.add_tag upon $TAG(permission:use_items)

scry $SCROLL(Wizard created and tagged)

# Create monster using same approach
bind orc_monster = conjure_familiar upon $SCROLL(Grashk the Brutal)
orc_monster.add_tag upon $TAG(type:familiar)
orc_monster.add_tag upon $TAG(role:enemy)
orc_monster.add_tag upon $TAG(type:orc)
orc_monster.add_tag upon $TAG(domain:combat)
orc_monster.add_tag upon $TAG(ability:melee_attack)
orc_monster.add_tag upon $TAG(ability:intimidate)
orc_monster.add_tag upon $TAG(status:hostile)

scry $SCROLL(Orc monster created and tagged)

# Create loot item
bind fire_staff = conjure_familiar upon $SCROLL(Staff of Eternal Flames)
fire_staff.add_tag upon $TAG(type:item)
fire_staff.add_tag upon $TAG(type:weapon)
fire_staff.add_tag upon $TAG(priority:high)
fire_staff.add_tag upon $TAG(domain:magic)
fire_staff.add_tag upon $TAG(ability:fire_damage)

scry $SCROLL(Fire staff created and tagged)

# Test tag checking
should wizard_player.has_tag upon $TAG(ability:fireball):
    scry $SCROLL(Wizard can cast fireball)

should orc_monster.has_tag upon $TAG(domain:combat):
    scry $SCROLL(Orc is a combat entity)

should fire_staff.has_tag upon $TAG(type:weapon):
    scry $SCROLL(Fire staff is a weapon)

# Test negative cases
should wizard_player.has_tag upon $TAG(ability:flight):
    scry $SCROLL(Wizard can fly)
lest:
    scry $SCROLL(Wizard cannot fly)

should orc_monster.has_tag upon $TAG(behavior:friendly):
    scry $SCROLL(Orc is friendly)
lest:
    scry $SCROLL(Orc is not friendly)

scry $SCROLL(Tag system demo completed successfully)
'''
    
    print("Testing user's corrected script...")
    print("=" * 50)
    
    success = interpret_grimoire(code)
    print("=" * 50)
    print(f"Script execution successful: {success}")
    
    return success

if __name__ == "__main__":
    test_user_script()