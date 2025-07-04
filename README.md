# Grimoire Programming Language

A magical programming language designed for game development with familiar-based programming paradigms, effect systems, and dimensional programming concepts.

## Overview

Grimoire is a unique programming language that brings magical concepts to software development. It features:

- **Magical Syntax**: Uses mystical terminology like `conjure`, `ritual`, `artifact`, and `familiar`
- **Object-Oriented Programming**: Classes are called "artifacts" and methods are "rituals"
- **Familiar System**: Specialized entities for game development and AI
- **Effect System**: Explicit handling of side effects through magical auras
- **Planar Programming**: Dimensional concepts for complex state management

## Installation

```bash
pip install grimoire-lang
```

Or clone and install from source:

```bash
git clone https://github.com/SFMiner/Grimoire.git
cd grimoire
pip install -e .
```

## Quick Start

### Hello World

```grimoire
# hello_world.grim
ritual main():
    scry $SCROLL(Hello, Grimoire World!)

main upon
```

Run with:
```bash
grimoire hello_world.grim
```

### Basic Syntax

#### Variables and Data Types

```grimoire
# Variable binding
bind wizard_name = $SCROLL(Merlin)  # String literal
bind power_level = 9000             # Integer literal  
bind mana_ratio = 0.75              # Float literal

# Output
scry wizard_name
```

#### Artifacts (Classes)

```grimoire
artifact Wizard:
    essence name        # Class attribute
    essence mana = 100  # With default value
    
    ritual invoke(wizard_name):  # Constructor
        bind self.name = wizard_name
        scry $SCROLL(Wizard ) added to wizard_name added to $SCROLL( awakens!)
    
    ritual cast_spell(spell_name):
        if enchanted self.mana is greater than 10:
            bind self.mana = self.mana subtracted from 10
            scry $SCROLL(Casting ) added to spell_name
        else cursed:
            scry $SCROLL(Not enough mana!)

# Create instance
bind merlin = conjure Wizard upon $SCROLL(Merlin)
merlin.cast_spell upon $SCROLL(Fireball)
```

#### Control Flow

```grimoire
# Conditional statements
if enchanted player.health is greater than 0:
    scry $SCROLL(Player is alive!)
else cursed:
    scry $SCROLL(Game over!)

# Loops
while charged enemy.health is greater than 0:
    player.attack upon enemy
    
for each arcana spell in spellbook:
    spell.cast upon
```

#### Functions (Rituals)

```grimoire
ritual calculate_damage(base_damage, modifier):
    bind total = base_damage multiplied by modifier
    return total

bind damage = calculate_damage upon 50, 1.5
scry damage  # Outputs: 75
```

## Language Features

### Magical Operators

| Grimoire | Traditional | Description |
|----------|-------------|-------------|
| `added to` | `+` | Addition |
| `subtracted from` | `-` | Subtraction |
| `multiplied by` | `*` | Multiplication |
| `divided by` | `/` | Division |
| `is greater than` | `>` | Greater than |
| `is lesser than` | `<` | Less than |
| `is equal to` | `==` | Equality |
| `is now` | `=` | Assignment |
| `diminish by` | `-=` | Decrement |
| `strengthen by` | `+=` | Increment |

### Keywords

- `conjure` - Create objects
- `summon` - Import modules
- `bind` - Variable assignment
- `ritual` - Function definition
- `artifact` - Class definition
- `familiar` - Familiar definition
- `essence` - Class attribute
- `scry` - Print/output
- `upon` - Function call
- `if enchanted` - If statement
- `else cursed` - Else statement
- `while charged` - While loop
- `for each arcana` - For loop

## Examples

### Wizard Battle System

```grimoire
artifact Wizard:
    essence name
    essence health = 100
    essence mana = 50
    
    ritual invoke(wizard_name):
        bind self.name = wizard_name
    
    ritual fireball(target):
        if enchanted self.mana is not lesser than 20:
            bind damage = 35
            target.take_damage upon damage
            diminish self.mana by 20
            scry self.name added to $SCROLL( casts Fireball!)
        else cursed:
            scry $SCROLL(Not enough mana!)
    
    ritual take_damage(amount):
        diminish self.health by amount
        scry self.name added to $SCROLL( takes ) added to amount added to $SCROLL( damage!)

# Battle simulation
bind gandalf = conjure Wizard upon $SCROLL(Gandalf)
bind saruman = conjure Wizard upon $SCROLL(Saruman)

gandalf.fireball upon saruman
```

## Development Roadmap

The Grimoire language is under active development. Current status:

✅ **Phase 1: Core Language** (Complete)
- Lexical analyzer and parser
- Basic interpreter
- Object-oriented programming
- Control flow structures

🚧 **Phase 2: Familiar System** (In Progress)
- Familiar entities for game development
- AI goal system
- Entity management

🔮 **Phase 3: Advanced Features** (Planned)
- Effect system for side effect management
- Planar programming for dimensional concepts
- Socket system for dynamic connections

🔮 **Phase 4: Standard Library** (Planned)
- Game development utilities
- Built-in familiars and artifacts
- Development tools and REPL

## Contributing

Grimoire is an open-source project and contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Philosophy

Grimoire aims to make programming more intuitive and expressive by using magical metaphors that align with game development concepts. The language encourages thinking about software in terms of entities, behaviors, and magical interactions rather than just functions and data structures.

*"Any sufficiently advanced technology is indistinguishable from magic."* - Arthur C. Clarke
