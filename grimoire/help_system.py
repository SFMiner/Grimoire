"""
Grimoire Programming Language Help System

This module provides comprehensive documentation for all Grimoire language features.
"""

HELP_TOPICS = {
    'keywords': """
🔮 Grimoire Keywords & Language Constructs:

VARIABLE DECLARATION:
    bind x = value              # Declare and bind a variable
    evoke x                     # Reference a variable
    
CONDITIONAL STATEMENTS:
    if condition:               # Standard if statement
        # code
    elif condition:             # Else if 
        # code
    else:                       # Else clause
        # code

LOOPS:
    for item in collection:     # For loop
        # code
    while condition:            # While loop
        # code
        
FUNCTION DEFINITION:
    ritual function_name(params):    # Define a function
        # code
        return value            # Return a value
        
AGENT SYSTEM:
    archon name domain:         # Create an archon (strategic AI)
        # archon definition
    spirit name domain:         # Create a spirit (tactical AI)
        # spirit definition
    familiar name:              # Create a familiar (operational AI)
        # familiar definition

PACT SYSTEM:
    pact name terms:            # Define a pact
        # pact terms
    invoke pact_name            # Invoke a pact
    
SCRYING (OUTPUT):
    scry expression             # Print/output expression
    scry $SCROLL(text)          # Print text to scroll
    scry $CRYSTAL(data)         # Display data in crystal
    scry $FLAME(message)        # Send message to flame
    scry $MIRROR(reflection)    # Show reflection in mirror
""",

    'functions': """
📜 Grimoire Built-in Functions:

AGENT CREATION:
    create_archon(name, domain, goals)      # Create a strategic archon
    create_spirit(name, domain, goals)      # Create a tactical spirit
    summon(name, pacts)                     # Create a familiar with pacts
    
PACT MANAGEMENT:
    create_familiar_with_pact(name, pact_terms)  # Create familiar with pact
    invoke_pact(familiar_name, pact_name)        # Invoke a pact
    revoke_pact(familiar_name, pact_name)        # Revoke a pact
    
MONITORING & DEBUGGING:
    enable_reporting(familiar_name, types)       # Enable activity reporting
    disable_reporting(familiar_name)            # Disable activity reporting
    get_wrangler_report()                       # Get wrangler status
    
SYSTEM MANAGEMENT:
    autonomous_update(agent_name)               # Trigger autonomous update
    oversee_domain(spirit_name, domain)         # Oversee domain authority
    
INSPECTION:
    get_pact_summary()                         # Get all pact information
    get_spirit_pacts(spirit_name)              # Get spirit's pacts
    get_familiar_stats(familiar_name)          # Get familiar statistics
    
UTILITY:
    true_name(entity)                          # Get true name of entity
    domain_authority(spirit, domain)           # Check domain authority
    
EXAMPLES:
    # Create a combat archon
    create_archon("BattleMaster", "Combat", ["defend_base", "attack_enemies"])
    
    # Create familiar with pact
    create_familiar_with_pact("scout", "patrol_area")
    
    # Monitor familiar activity
    enable_reporting("scout", ["environmental", "command"])
""",

    'agents': """
🤖 Grimoire Hierarchical Agent System:

AGENT HIERARCHY:
    Archon (Strategic)    →    Spirit (Tactical)    →    Familiar (Operational)
    
ARCHONS - Strategic Level AI:
    • Manage multiple spirits
    • Handle domain-specific strategic goals
    • Allocate resources across spirits
    • Make high-level decisions
    
    DOMAINS: Combat, Economy, Diplomacy, Exploration, Defense
    
    EXAMPLE:
        archon WarCommander Combat:
            goals: [defend_territory, coordinate_attacks]
            spirits: [infantry_leader, cavalry_leader]
            resources: [troops, weapons, gold]

SPIRITS - Tactical Level AI:
    • Manage multiple familiars
    • Handle short-term objectives
    • Coordinate familiar activities
    • Execute archon directives
    
    EXAMPLE:
        spirit InfantryLeader Combat:
            goals: [maintain_formation, execute_orders]
            familiars: [soldier1, soldier2, soldier3]
            authority: [movement, combat_actions]

FAMILIARS - Operational Level AI:
    • Direct entity management
    • Reactive behaviors
    • Activity logging
    • Execute spirit commands
    
    EXAMPLE:
        familiar Soldier:
            pacts: [follow_orders, report_enemies]
            behaviors: [patrol, attack, defend]
            
GOAL SYSTEM:
    • Priority-based goal selection
    • Weighted goal satisfaction
    • Cross-agent coordination
    • Dynamic goal adjustment
    
COMMUNICATION:
    • Archon → Spirit: Strategic directives
    • Spirit → Familiar: Tactical commands
    • Familiar → Spirit: Status reports
    • Spirit → Archon: Progress updates
""",

    'pacts': """
🤝 Grimoire Pact System:

PACT FUNDAMENTALS:
    • Immutable agreements between spirits and familiars
    • Black box security - cannot be inspected or modified
    • Spirit-controlled creation with true name authority
    • Initialization-only - pacts set during familiar creation
    
PACT LIFECYCLE:
    1. Spirit creates pact with specific terms
    2. Familiar created with pact binding
    3. Pact becomes immutable and secure
    4. Familiar executes pact terms
    5. Spirit can revoke pact (destroys familiar)
    
PACT TYPES:
    • Behavioral Pacts: Define how familiar should act
    • Reporting Pacts: What information to share
    • Authority Pacts: What actions familiar can take
    • Resource Pacts: What resources familiar can access
    
SECURITY FEATURES:
    • True name authentication
    • Domain authority checking
    • Immutable terms and conditions
    • Violation correction by spirits
    
EXAMPLES:
    # Create pact for patrol behavior
    pact patrol_duty:
        behavior: patrol_area
        reporting: location_updates
        authority: movement_only
        
    # Create familiar with pact
    create_familiar_with_pact("guard", "patrol_duty")
    
    # Invoke pact behavior
    invoke_pact("guard", "patrol_duty")
    
PACT TERMS:
    • 'behavior': Core actions familiar should perform
    • 'reporting': Information to report to spirit
    • 'authority': Permissions and allowed actions
    • 'resources': Available resources and limits
    • 'conditions': Circumstances for pact activation
    
BEST PRACTICES:
    • Define clear, specific pact terms
    • Use descriptive pact names
    • Balance authority with security
    • Monitor pact performance
    • Revoke unused or problematic pacts
""",

    'syntax': """
📝 Grimoire Syntax Guide:

BASIC SYNTAX:
    • Statements end with newlines (no semicolons)
    • Blocks use indentation (like Python)
    • Comments start with # 
    • Case sensitive
    
VARIABLE NAMES:
    • Start with letter or underscore
    • Can contain letters, numbers, underscores
    • Cannot be keywords
    
OPERATORS:
    Arithmetic: +, -, *, /, %, **
    Comparison: ==, !=, <, >, <=, >=
    Logical: and, or, not
    Assignment: =
    
LITERALS:
    Numbers: 42, 3.14, -10
    Strings: "hello", 'world'
    Booleans: true, false
    Lists: [1, 2, 3]
    Dictionaries: {key: value}
    
SCRYING VARIANTS (Output):
    $SCROLL(text)    # Standard text output
    $CRYSTAL(data)   # Structured data display
    $FLAME(msg)      # Urgent/important messages
    $MIRROR(refl)    # Reflection/debug output
    $RUNE(symbol)    # Symbolic/magical output
    
CONTROL FLOW:
    if condition:
        # code
    elif other_condition:
        # code
    else:
        # code
        
    for item in collection:
        # code
        
    while condition:
        # code
        
FUNCTION DEFINITION:
    ritual function_name(param1, param2):
        # function body
        return value
        
AGENT DEFINITIONS:
    archon name domain:
        # archon configuration
        
    spirit name domain: 
        # spirit configuration
        
    familiar name:
        # familiar configuration
""",

    'examples': """
🎯 Grimoire Code Examples:

BASIC PROGRAM:
    # Simple hello world
    scry $SCROLL("Hello, magical world!")
    
    # Variables and arithmetic
    bind x = 10
    bind y = 20
    bind sum = x + y
    scry $CRYSTAL(sum)

FUNCTION EXAMPLE:
    ritual greet(name):
        scry $SCROLL("Greetings, " + name + "!")
        return true
    
    greet("Wizard")

CONDITIONAL EXAMPLE:
    bind health = 75
    
    if health > 80:
        scry $SCROLL("Excellent health!")
    elif health > 50:
        scry $SCROLL("Good health")
    else:
        scry $SCROLL("Poor health")

LOOP EXAMPLES:
    # For loop
    for i in [1, 2, 3, 4, 5]:
        scry $SCROLL("Count: " + str(i))
    
    # While loop
    bind count = 0
    while count < 3:
        scry $SCROLL("Iteration: " + str(count))
        count = count + 1

AGENT SYSTEM EXAMPLE:
    # Create strategic archon
    create_archon("CityMaster", "Economy", ["manage_resources", "trade"])
    
    # Create tactical spirit
    create_spirit("Merchant", "Economy", ["buy_goods", "sell_goods"])
    
    # Create operational familiar
    create_familiar_with_pact("trader", "execute_trades")
    
    # Enable monitoring
    enable_reporting("trader", ["command", "environmental"])
    
    # Check system status
    get_wrangler_report()

PACT EXAMPLE:
    # Create a guard familiar with patrol pact
    create_familiar_with_pact("castle_guard", "patrol_walls")
    
    # Invoke the pact
    invoke_pact("castle_guard", "patrol_walls")
    
    # Check pact status
    get_familiar_stats("castle_guard")

COMPLETE MINI-GAME:
    # Simple RPG character system
    bind player_health = 100
    bind player_mana = 50
    
    ritual cast_spell(spell_name, cost):
        if player_mana >= cost:
            player_mana = player_mana - cost
            scry $FLAME("Cast " + spell_name + "!")
            return true
        else:
            scry $SCROLL("Not enough mana")
            return false
    
    ritual heal_player(amount):
        player_health = player_health + amount
        scry $CRYSTAL("Health: " + str(player_health))
    
    # Game loop
    cast_spell("Fireball", 20)
    heal_player(15)
    scry $MIRROR("Final health: " + str(player_health))
""",

    'debugging': """
🐛 Grimoire Debugging Guide:

REPL DEBUG COMMANDS:
    debug on/off           # Toggle debug mode
    show_tokens           # Show lexer tokens
    show_ast              # Show parser AST
    
DEBUGGING TECHNIQUES:
    1. Use $MIRROR() for debug output
    2. Enable familiar reporting
    3. Check wrangler status
    4. Inspect pact relationships
    
COMMON ERRORS:
    • Undefined Variable: Check 'bind' statements
    • Pact Violations: Check spirit authority
    • Agent Conflicts: Review domain assignments
    • Syntax Errors: Check indentation and keywords
    
MONITORING TOOLS:
    get_wrangler_report()              # System overview
    get_familiar_stats(name)           # Individual familiar
    get_pact_summary()                 # All pacts
    enable_reporting(name, types)      # Activity logging
    
DEBUGGING WORKFLOW:
    1. Identify the problem area
    2. Enable debug mode
    3. Use show_tokens/show_ast
    4. Add $MIRROR() debug outputs
    5. Check agent/pact status
    6. Fix and test incrementally
    
AGENT DEBUGGING:
    • Check domain authority conflicts
    • Verify pact terms are correct
    • Monitor familiar activity logs
    • Ensure proper goal priorities
    
PERFORMANCE TIPS:
    • Limit familiar activity logging
    • Use efficient pact terms
    • Monitor resource allocation
    • Balance agent responsibilities
""",

    'quickstart': """
🚀 Grimoire Quick Start Guide:

GETTING STARTED:
    1. Install Grimoire
    2. Run: grimoire --interactive
    3. Type: help() for this help
    4. Start coding!

FIRST STEPS:
    # 1. Hello World
    scry $SCROLL("Hello, World!")
    
    # 2. Variables
    bind name = "Wizard"
    scry $SCROLL("Hello, " + name)
    
    # 3. Function
    ritual greet(name):
        scry $SCROLL("Greetings, " + name + "!")
    
    greet("Apprentice")

NEXT STEPS:
    # 4. Create your first familiar
    create_familiar_with_pact("helper", "assist_player")
    
    # 5. Enable monitoring
    enable_reporting("helper", ["command"])
    
    # 6. Check status
    get_wrangler_report()

LEARNING PATH:
    1. Master basic syntax (variables, functions, loops)
    2. Learn the agent system (familiars, spirits, archons)
    3. Understand pacts and security
    4. Build complex interactive systems
    5. Create your own game!

RESOURCES:
    help('syntax')     # Language syntax
    help('functions')  # Built-in functions
    help('agents')     # Agent system
    help('pacts')      # Pact system
    help('examples')   # Code examples
    
TIPS:
    • Use descriptive variable names
    • Start with simple familiars
    • Test pacts thoroughly
    • Monitor agent performance
    • Build incrementally
""",

    'advanced': """
⚡ Advanced Grimoire Features:

MULTI-AGENT COORDINATION:
    • Cross-domain communication
    • Resource sharing protocols
    • Conflict resolution
    • Emergent behaviors
    
COMPLEX PACT PATTERNS:
    • Conditional pacts
    • Time-limited agreements
    • Hierarchical authority
    • Dynamic pact modification
    
PERFORMANCE OPTIMIZATION:
    • Efficient goal prioritization
    • Resource pooling
    • Lazy evaluation
    • Batch processing
    
SECURITY CONSIDERATIONS:
    • True name protection
    • Domain isolation
    • Authority validation
    • Audit trails
    
ARCHITECTURAL PATTERNS:
    • Command pattern with pacts
    • Observer pattern with reporting
    • Strategy pattern with goals
    • Mediator pattern with spirits
    
DEBUGGING ADVANCED SYSTEMS:
    • Distributed tracing
    • Agent interaction graphs
    • Performance profiling
    • Resource utilization
    
EXTENSIBILITY:
    • Custom agent types
    • Domain-specific languages
    • Plugin architecture
    • External integrations
    
BEST PRACTICES:
    • Separation of concerns
    • Clear responsibilities
    • Minimal coupling
    • Comprehensive testing
    • Documentation
""",
}

# Additional topic mappings
TOPIC_ALIASES = {
    'help': 'quickstart',
    'start': 'quickstart',
    'begin': 'quickstart',
    'intro': 'quickstart',
    'tutorial': 'quickstart',
    'guide': 'quickstart',
    
    'vars': 'syntax',
    'variables': 'syntax',
    'operators': 'syntax',
    'literals': 'syntax',
    
    'funcs': 'functions',
    'builtin': 'functions',
    'builtins': 'functions',
    'built-in': 'functions',
    'methods': 'functions',
    
    'agent': 'agents',
    'agents': 'agents',
    'archon': 'agents',
    'spirit': 'agents',
    'familiar': 'agents',
    'familiars': 'agents',
    'ai': 'agents',
    
    'pact': 'pacts',
    'contract': 'pacts',
    'contracts': 'pacts',
    'agreement': 'pacts',
    'agreements': 'pacts',
    
    'code': 'examples',
    'sample': 'examples',
    'samples': 'examples',
    'demo': 'examples',
    'demos': 'examples',
    
    'debug': 'debugging',
    'troubleshoot': 'debugging',
    'error': 'debugging',
    'errors': 'debugging',
    'problem': 'debugging',
    'problems': 'debugging',
    
    'reference': 'keywords',
    'ref': 'keywords',
    'lang': 'keywords',
    'language': 'keywords',
    
    'expert': 'advanced',
    'pro': 'advanced',
    'professional': 'advanced',
    'complex': 'advanced',
}


def get_help_for_topic(topic: str) -> str:
    """Get help text for a specific topic."""
    if not topic:
        return HELP_TOPICS.get('quickstart', '')
    
    # Normalize topic
    topic = topic.lower().strip()
    
    # Check direct topics
    if topic in HELP_TOPICS:
        return HELP_TOPICS[topic]
    
    # Check aliases
    if topic in TOPIC_ALIASES:
        return HELP_TOPICS[TOPIC_ALIASES[topic]]
    
    # Return empty string if not found
    return ""


def get_all_topics() -> list:
    """Get list of all available help topics."""
    return list(HELP_TOPICS.keys())


def search_topics(query: str) -> list:
    """Search for topics containing the query."""
    query = query.lower()
    matches = []
    
    for topic, content in HELP_TOPICS.items():
        if query in topic.lower() or query in content.lower():
            matches.append(topic)
    
    return matches