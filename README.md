# 🔮 Grimoire Programming Language

A magical programming language designed for game development with hierarchical autonomous agents, immutable pacts, and emergent AI behaviors.

## ✨ Features

- **🤖 Hierarchical Agent System**: Three-tier AI architecture (Archons → Spirits → Familiars)
- **🤝 Immutable Pact System**: Secure, black-box agreements with true name authentication
- **📊 Familiar Wrangler**: Centralized monitoring and debugging for agent activities
- **🎯 Goal-Oriented AI**: Priority-based decision making with emergent behaviors
- **🎨 Thematic Syntax**: Magical keywords and constructs for immersive coding
- **🔍 Interactive REPL**: Rich debugging and exploration environment

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/grimoire-lang/grimoire.git
cd grimoire

# Install dependencies
pip install -r requirements.txt

# Run the interactive REPL
python -m grimoire --interactive
```

### Your First Spell

```grimoire
# Hello World
scry $SCROLL("Hello, magical world!")

# Variables and functions
bind name = "Wizard"
ritual greet(target):
    scry $SCROLL("Greetings, " + target + "!")

greet(name)

# Create your first familiar
create_familiar_with_pact("helper", "assist_player")
enable_reporting("helper", ["command"])
get_wrangler_report()
```

## 🎭 Language Overview

### Core Syntax

```grimoire
# Variables
bind health = 100
bind mana = 50

# Functions (called "rituals")
ritual cast_spell(spell_name, cost):
    if mana >= cost:
        mana = mana - cost
        scry $FLAME("Cast " + spell_name + "!")
        return true
    else:
        scry $SCROLL("Not enough mana")
        return false

# Control flow
if health > 50:
    scry $CRYSTAL("Healthy")
elif health > 20:
    scry $SCROLL("Wounded")
else:
    scry $MIRROR("Critical!")

# Loops
for i in [1, 2, 3, 4, 5]:
    scry $SCROLL("Count: " + str(i))
```

### Scrying (Output) System

Grimoire uses thematic output variants:

- `$SCROLL(text)` - Standard text output
- `$CRYSTAL(data)` - Structured data display
- `$FLAME(message)` - Urgent/important messages
- `$MIRROR(reflection)` - Debug/reflection output
- `$RUNE(symbol)` - Symbolic/magical output

## 🤖 Agent System

### Three-Tier Architecture

```grimoire
# Strategic Level (Archons)
create_archon("WarCommander", "Combat", ["defend_territory", "coordinate_attacks"])

# Tactical Level (Spirits)
create_spirit("Infantry", "Combat", ["maintain_formation", "execute_orders"])

# Operational Level (Familiars)
create_familiar_with_pact("soldier", "follow_orders")
```

### Agent Hierarchy

```
Archon (Strategic AI)
├── Domain: Combat, Economy, Diplomacy, etc.
├── Goals: High-level strategic objectives
├── Spirits: Multiple tactical managers
└── Resources: Cross-domain resource allocation

Spirit (Tactical AI)
├── Domain: Specific area of authority
├── Goals: Short-term tactical objectives
├── Familiars: Multiple operational units
└── Authority: Pact creation and management

Familiar (Operational AI)
├── Pacts: Immutable behavioral contracts
├── Activities: Direct entity management
├── Reporting: Activity logs and status
└── Behaviors: Reactive and proactive actions
```

## 🤝 Pact System

### Immutable Agreements

```grimoire
# Create a patrol pact
create_familiar_with_pact("guard", "patrol_walls")

# Invoke pact behavior
invoke_pact("guard", "patrol_walls")

# Monitor pact execution
get_familiar_stats("guard")
```

### Pact Features

- **Immutable**: Cannot be modified after creation
- **Secure**: True name authentication and domain authority
- **Black Box**: Terms hidden from external inspection
- **Spirit-Controlled**: Only spirits can create and revoke pacts
- **Initialization-Only**: Pacts bound during familiar creation

## 📊 Monitoring & Debugging

### Interactive REPL Commands

```grimoire
# Basic help
help()
help('agents')
help('pacts')

# Debugging
debug on
show_tokens
show_ast

# Agent monitoring
agents()
familiars()
wrangler()

# System status
get_wrangler_report()
get_pact_summary()
```

### Activity Reporting

```grimoire
# Enable selective reporting
enable_reporting("familiar_name", ["command", "environmental", "inter_familiar"])

# Check activity logs
get_familiar_stats("familiar_name")

# System overview
get_wrangler_report()
```

## 🎯 Examples

### Simple RPG System

```grimoire
# Character stats
bind player_health = 100
bind player_mana = 50
bind player_gold = 250

# Spell casting system
ritual cast_spell(spell_name, mana_cost):
    if player_mana >= mana_cost:
        player_mana = player_mana - mana_cost
        scry $FLAME("✨ Cast " + spell_name + "!")
        return true
    else:
        scry $SCROLL("❌ Not enough mana")
        return false

# Combat AI
create_archon("BattleCommander", "Combat", ["protect_player", "defeat_enemies"])
create_spirit("Guardian", "Combat", ["defensive_stance", "healing_support"])
create_familiar_with_pact("healer", "heal_when_low_health")

# Enable monitoring
enable_reporting("healer", ["command", "environmental"])

# Game loop
cast_spell("Healing Light", 25)
autonomous_update("healer")
scry $CRYSTAL("Health: " + str(player_health) + ", Mana: " + str(player_mana))
```

### Complex Agent Coordination

```grimoire
# Multi-domain strategy
create_archon("CityMaster", "Economy", ["manage_resources", "optimize_trade"])
create_archon("DefenseChief", "Defense", ["protect_borders", "coordinate_patrols"])

# Tactical managers
create_spirit("Merchant", "Economy", ["buy_low", "sell_high"])
create_spirit("Captain", "Defense", ["patrol_routes", "respond_to_threats"])

# Operational units
create_familiar_with_pact("trader", "execute_trades")
create_familiar_with_pact("scout", "patrol_perimeter")
create_familiar_with_pact("guard", "defend_gates")

# Enable comprehensive monitoring
enable_reporting("trader", ["command", "environmental"])
enable_reporting("scout", ["environmental", "inter_familiar"])
enable_reporting("guard", ["command", "pact"])

# Coordinate activities
autonomous_update("trader")
autonomous_update("scout")
autonomous_update("guard")

# System overview
get_wrangler_report()
```

## 🛠️ Development

### Project Structure

```
grimoire/
├── cli.py              # Command-line interface
├── lexer.py            # Tokenization
├── parser.py           # Syntax analysis
├── interpreter.py      # Code execution
├── help_system.py      # Documentation system
├── hierarchical_agents.py  # Agent system
├── familiar_wrangler.py    # Monitoring system
├── pact_system.py          # Pact management
└── examples/               # Example programs
    ├── hierarchical_agents_demo.grim
    ├── basic_syntax_demo.grim
    └── pact_system_demo.grim
```

### Running Tests

```bash
# Run the comprehensive demo
python -m grimoire examples/hierarchical_agents_demo.grim

# Interactive development
python -m grimoire --interactive
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📚 Documentation

### Command Line Help

```bash
# Show CLI help
grimoire --help

# Show version
grimoire --version

# Interactive help
grimoire --interactive
> help()
> help('agents')
> help('pacts')
```

### Available Help Topics

- `keywords` - Language syntax and constructs
- `functions` - Built-in functions
- `agents` - Hierarchical agent system
- `pacts` - Immutable pact system
- `syntax` - Basic language syntax
- `examples` - Code examples
- `debugging` - Debugging guide
- `quickstart` - Getting started guide
- `advanced` - Advanced features

## 🔮 Philosophy

Grimoire is designed around the concept of **magical programming** - where code is not just functional but thematically rich and engaging. The language embraces:

- **Immersive Terminology**: Rituals instead of functions, scrying instead of printing
- **Emergent Behaviors**: AI agents that develop complex behaviors through simple rules
- **Secure Contracts**: Pacts that enforce agreements without exposing implementation
- **Hierarchical Intelligence**: Natural command structures that mirror real-world organizations

## 🎨 Keyword Variants

Grimoire supports thematic keyword variants for different magical schools:

- **Elemental**: `forge` (bind), `transmute` (transform)
- **Arcane**: `inscribe` (bind), `manifest` (create)
- **Divine**: `consecrate` (bind), `bless` (enhance)
- **Shadow**: `bind` (default), `conceal` (hide)
- **Nature**: `grow` (bind), `nurture` (develop)

## 🚧 Roadmap

### Current Status (v1.0.0)
- ✅ Complete hierarchical agent system
- ✅ Immutable pact system with security
- ✅ Familiar wrangler monitoring
- ✅ Goal-oriented AI framework
- ✅ Interactive help system
- ✅ Comprehensive documentation

### Future Features
- 🔄 Multidimensional plane system
- 🔄 Advanced learning algorithms
- 🔄 Visual agent debugging tools
- 🔄 Real-time collaboration features
- 🔄 Game engine integrations

## 📄 License

MIT License - see LICENSE file for details.

## 🌟 Credits

Created with ❤️ for game developers who believe in the magic of code.

---

*"Any sufficiently advanced technology is indistinguishable from magic."* - Arthur C. Clarke

*"Any sufficiently magical code is indistinguishable from advanced technology."* - Grimoire Philosophy