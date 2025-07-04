# Current Problem:

Spirits have "domain authority" but this is mostly a label without clear enforcement mechanisms or scope definitions.

### The Intent:
Domain authority was intended to be set to whatever sort of domain the developer using it needs. So, for a game, this might be things like "economy" or combat" where for a CRM app it might have customer data, finance, security, etc.


## The solution: more powerful and relevant implementation


### 1. **Domain-Agnostic Permission Framework**

Instead of hardcoding game-specific domains, create a flexible permission system:

```grimoire
# Game development
bind combat_spirit = create_spirit upon $SCROLL(WarLeader), $SCROLL(Combat)
define_domain_permissions upon $SCROLL(Combat), [
    $SCROLL(spawn_units), $SCROLL(move_units), $SCROLL(attack), $SCROLL(defend)
]

# CRM application  
bind customer_spirit = create_spirit upon $SCROLL(CustomerManager), $SCROLL(CustomerData)
define_domain_permissions upon $SCROLL(CustomerData), [
    $SCROLL(read_profile), $SCROLL(update_contact), $SCROLL(create_lead)
]
```

### 2. **Resource and Capability Binding**

Each domain should control specific resources and capabilities:

```grimoire
# Domain controls what resources it can access
bind_domain_resources upon $SCROLL(Economy), [
    $SCROLL(gold), $SCROLL(trade_routes), $SCROLL(market_data)
]

# Domain defines what actions its familiars can perform
bind_domain_capabilities upon $SCROLL(Security), [
    $SCROLL(authenticate_user), $SCROLL(encrypt_data), $SCROLL(audit_access)
]
```

### 3. **Cross-Domain Interaction Protocols**

This is where it gets really powerful - defining how domains interact:

```grimoire
# Combat domain needs resources from Economy domain
create_domain_dependency upon $SCROLL(Combat), $SCROLL(Economy), 
    [$SCROLL(request_funding), $SCROLL(purchase_equipment)]

# Security domain can audit any other domain
grant_cross_domain_access upon $SCROLL(Security), $SCROLL(*), 
    [$SCROLL(audit), $SCROLL(compliance_check)]
```

### 4. **Dynamic Domain Boundaries**

Allow domains to be reconfigured at runtime based on application needs:

```grimoire
# Merge domains during crisis mode
merge_domains upon [$SCROLL(Combat), $SCROLL(Defense)], $SCROLL(Military)

# Split domain when scaling up
split_domain upon $SCROLL(CustomerData), 
    [$SCROLL(CustomerProfiles), $SCROLL(CustomerBehavior)]
```

## Implementation Strategy
### 1. **Domain Registry System**

Create a central registry that tracks:

- What domains exist
- What permissions each domain grants
- Which resources each domain controls
- How domains can interact with each other

### 2. **Permission Enforcement Engine**

When a familiar attempts an action:

- Check which spirit created the familiar
- Verify the spirit's domain has permission for that action type
- Ensure the action target is within domain scope
- Log the action for audit trails

### 3. **Domain-Specific Goal Templates**

Instead of generic goals, provide domain-appropriate goal templates:

```grimoire
# Economy domain goals
economy_goals = [
    $SCROLL(maximize_revenue), $SCROLL(minimize_costs), 
    $SCROLL(expand_market_share), $SCROLL(optimize_supply_chain)
]

# Security domain goals  
security_goals = [
    $SCROLL(prevent_breaches), $SCROLL(ensure_compliance),
    $SCROLL(monitor_threats), $SCROLL(maintain_availability)
]
```

### 4. **Domain Conflict Resolution**

When domains have overlapping concerns:

- Define precedence hierarchies (Security > all others for audit access)
- Implement negotiation protocols (Economy and Combat negotiate resource allocation)
- Create escalation paths (conflicts go to higher-level Archons)


## Implementation solution: “Doman  Wrangler”

Domains can be monitored through their controlling archons. The existing Familar Wrangler structure already contains most of the features we need to do this. It can be expanded and used as  follows

### 1. **Hierarchical Monitoring Extension**

```grimoire
# Extend the existing Wrangler to track domain-level activities
bind domain_wrangler = create_domain_wrangler upon

# Monitor all archons and their domain activities
enable_domain_reporting upon combat_archon, [$SCROLL(resource_allocation), $SCROLL(strategic_decisions)]
enable_domain_reporting upon economy_archon, [$SCROLL(trade_actions), $SCROLL(budget_changes)]

# Get cross-domain activity reports
bind domain_report = get_domain_wrangler_report upon
```

### 2. **Domain Activity Categories**

Extend the existing activity categories for domain-level concerns:

```grimoire
# New domain-specific reporting categories
domain_categories = [
    $SCROLL(cross_domain_requests),    # When domains interact
    $SCROLL(resource_conflicts),       # Resource allocation disputes
    $SCROLL(permission_violations),    # Unauthorized domain access
    $SCROLL(performance_metrics),      # Domain efficiency tracking
    $SCROLL(strategic_decisions),      # High-level archon choices
    $SCROLL(domain_boundaries),        # Domain scope changes
]
```

### 3. **Multi-Level Monitoring Integration**

The beauty is you get monitoring at three levels using the same pattern:

```grimoire
# Familiar level (existing)
bind familiar_stats = get_familiar_stats upon guard_familiar

# Spirit level (existing via familiars)
bind spirit_activity = get_spirit_summary upon guardian_spirit

# Domain level (new via archons)
bind domain_health = get_domain_summary upon $SCROLL(Combat)
```

## Implementation Benefits

### 1. **Unified Monitoring API**

Developers use the same patterns across all levels:


```grimoire
# Same enable/disable pattern at all levels
enable_reporting upon familiar, [$SCROLL(command)]
enable_reporting upon spirit, [$SCROLL(coordination)]  
enable_reporting upon archon, [$SCROLL(strategic_decisions)]
```

### 2. **Cross-Domain Visibility**

```grimoire
# Monitor interactions between domains
bind cross_domain_report = get_cross_domain_activity upon
# Shows: Economy requesting resources from Combat
#        Security auditing CustomerData access
#        etc.
```

### 3. **System Health Dashboard**

grimoire

```grimoire
ritual get_system_overview():
    bind familiar_health = get_wrangler_report upon
    bind domain_health = get_domain_wrangler_report upon
    
    # Combine for full system picture
    return combine_reports upon familiar_health, domain_health
```

## Advanced Domain Monitoring Features

### 1. **Domain Performance Metrics**

```grimoire
# Track domain efficiency
bind domain_metrics = get_domain_performance upon $SCROLL(Economy)
# Returns: resource_utilization, goal_completion_rate, response_time
```

### 2. **Cross-Domain Dependency Tracking

```grimoire
# See which domains are blocking others
bind dependency_report = get_domain_dependencies upon
# Shows: Combat waiting on Economy for funding
#        Security holding up CustomerData access
```

### 3. **Domain Resource Allocation Monitoring

```grimoire
# Track resource flow between domains
bind resource_flow = get_resource_allocation_report upon
# Shows: 60% CPU to Combat, 30% to Economy, 10% to Security
```

### 4. **Policy Violation Detection**

```grimoire
# Monitor domain boundary violations
enable_policy_monitoring upon $SCROLL(strict)
bind violations = get_policy_violations upon
# Reports unauthorized cross-domain access attempts
```

## Practical Applications

### For Game Development:

- Monitor which game systems are consuming the most resources
- Track player impact on different game domains
- Debug emergent behaviors between systems

### For Enterprise Applications:

- Audit cross-department data access
- Monitor system performance by business domain
- Track compliance with security policies

### For System Administration:

- Monitor microservice interactions
- Track resource allocation across service boundaries
- Detect anomalous cross-service communication

This unified monitoring approach means developers learn one monitoring pattern that scales from individual agents up to entire application domains. The Familiar Wrangler becomes the foundation for a comprehensive observability system that maintains the magical programming aesthetic while providing serious operational capabilities.

It's a perfect example of how Grimoire's fantasy elements can enhance rather than obscure practical programming patterns!

# Socket-Based  Architecture

Sockets should be to black-box the specifics of things like combat: one could have ,for example, an "attack' socket that plugs into the AI logic that determines the which of the available attacks to use.

## Socket-Based Combat Architecture

### 1. **Attack Decision Socket

```grimoire
# Combat familiar exposes decision points as sockets
artifact CombatFamiliar:
	# Input sockets - receive context
	socket enemy_analysis_input
	socket tactical_situation_input
	socket available_resources_input
	
	# Output sockets - provide decisions
	socket attack_choice_output
	socket target_selection_output
	socket retreat_decision_output
	
	ritual evaluate_combat():
		# Internal combat logic uses socket inputs
		bind enemy_data = self.enemy_analysis_input.receive()
		bind tactics = self.tactical_situation_input.receive()
		bind resources = self.available_resources_input.receive()
		
		# Complex combat AI logic here
		bind chosen_attack = self.select_optimal_attack(enemy_data, tactics, resources)
		
		# Send decision through output socket
		self.attack_choice_output.send(chosen_attack)
```

### 2. **Pluggable AI Systems**

```grimoire
# Different AI systems can plug into the same sockets
artifact SimpleAI:
	socket attack_choice_output
	
	ritual decide_attack(enemy_data, tactics, resources):
		# Simple logic: just use strongest available attack
		bind strongest = find_strongest_attack(resources.available_attacks)
		self.attack_choice_output.send(strongest)

artifact AdvancedAI:
	socket attack_choice_output
	
	ritual decide_attack(enemy_data, tactics, resources):
		# Complex logic: consider damage, mana cost, cooldowns, positioning
		bind optimal = calculate_optimal_attack(
			enemy_data.weaknesses,
			enemy_data.resistances,
			tactics.current_position,
			resources.available_attacks
		)
		self.attack_choice_output.send(optimal)
```

### 3. **Socket Connection System**

```grimoire
# Connect different AI systems to combat familiars
bind combat_familiar = create_familiar_with_pact upon combat_spirit, $SCROLL(Warrior), [$SCROLL(engage_enemies)]

# Easy AI swapping for different difficulty levels
connect_socket upon simple_ai.attack_choice_output, combat_familiar.attack_choice_input
# Later: disconnect and connect advanced AI instead
disconnect_socket upon simple_ai.attack_choice_output, combat_familiar.attack_choice_input
connect_socket upon advanced_ai.attack_choice_output, combat_familiar.attack_choice_input
```

## Benefits of This Approach

### 1. **True Separation of Concerns**

- Combat familiar handles combat mechanics (damage calculation, animation, effects)
- AI familiar handles decision-making (target selection, attack choice, timing)
- Animation familiar handles visual presentation
- Audio familiar handles sound effects

### 2. **Hot-Swappable Intelligence**

grimoire

```grimoire
# Runtime AI difficulty adjustment
ritual adjust_difficulty(level):
	if level == $SCROLL(easy):
		connect_all_enemies_to upon simple_ai
	elif level == $SCROLL(hard):
		connect_all_enemies_to upon advanced_ai
	elif level == $SCROLL(adaptive):
		connect_all_enemies_to upon learning_ai
```

### 3. **Modular Game Systems**

grimoire

```grimoire
# Different combat systems for different game types
connect_socket upon turn_based_combat.action_request, ai_system.decision_output
# vs
connect_socket upon real_time_combat.continuous_input, ai_system.decision_output
```

### 4. **Easy Testing and Debugging**

grimoire

```grimoire
# Test AI without full combat system
bind test_ai = create_test_harness upon
connect_socket upon ai_system.attack_choice_output, test_ai.decision_recorder
```

## Extended Socket Applications

### 1. **Layered Decision Making**

grimoire

```grimoire
# Chain multiple AI layers
connect_socket upon strategic_ai.tactical_directive, tactical_ai.strategy_input
connect_socket upon tactical_ai.action_command, operational_ai.tactical_input  
connect_socket upon operational_ai.specific_action, combat_familiar.action_input
```

### 2. **Cross-System Data Flow**

grimoire

```grimoire
# Economy system influences combat decisions
connect_socket upon economy_familiar.resource_status, combat_ai.budget_constraint
connect_socket upon combat_familiar.equipment_needs, economy_familiar.purchase_requests
```

### 3. **Player Input Integration**

grimoire

```grimoire
# Player can override AI decisions at any socket level
connect_socket upon player_input.manual_override, combat_familiar.action_input
# When player doesn't intervene, AI takes over
connect_socket upon combat_ai.auto_decision, combat_familiar.action_input
```

### 4. **Analytics and Learning**

grimoire

```grimoire
# Monitor AI decisions for balancing
bind analytics_familiar = create_familiar_with_pact upon metrics_spirit, $SCROLL(Analyzer), [$SCROLL(collect_data)]
connect_socket upon combat_ai.decision_rationale, analytics_familiar.decision_data
connect_socket upon combat_familiar.action_results, analytics_familiar.outcome_data
```

## Implementation Considerations

### 1. **Socket Type Safety**

grimoire

```grimoire
# Sockets should enforce data contracts
define_socket_contract upon $SCROLL(attack_choice), {
	attack_type: $SCROLL(string),
	target_id: $SCROLL(entity_id),
	power_level: $SCROLL(float),
	expected_damage: $SCROLL(integer)
}
```

### 2. **Performance Optimization**

grimoire

```grimoire
# Sockets can include performance hints
socket high_frequency_updates:
	update_rate: 60_fps
	buffering: enabled
	
socket strategic_decisions:
	update_rate: 1_per_second
	buffering: disabled
```

This socket approach transforms familiars from simple agents into a composable system architecture. The "magic" becomes the elegant way complex systems can be assembled from simple, well-defined components - much more powerful than trying to make the language magically understand domain semantics!



# Defining Goals for agents.


## The Problem: 

Having a programming language automatically understand semantic meaning from arbitrary strings like "patrol" or "defend" is  beyond reasonable bounds for a language implementation. That's venturing into AI/NLP territory rather than programming language design.

## The Solution:

A programmable Goal artifact would solve the semantic understanding problem elegantly while giving developers full control over goal definition and measurement. This transforms goals from vague strings into executable, testable components.

## Required Changes Assessment

### ✅ **What's Already There (No Changes Needed)**

- **Lexer & Parser**: Already handles familiar creation and method calls
- **Core Language**: Variables, functions, objects already work
- **Familiar System**: Basic familiar architecture exists
- **CLI & Testing**: Infrastructure already in place

### 🔧 **New Code Required (Moderate Effort)**

### 1. **Socket System Classes** (~300-500 lines)

```python
# New files to add:
grimoire/sockets.py      # Socket implementation
grimoire/connections.py  # Connection management

class Socket:
    def __init__(self, name, data_type, direction):
        self.name = name
        self.data_type = data_type  # "input" or "output"
        self.direction = direction
        self.connections = []
        self.value = None
    
    def send(self, data):
        # Send data to all connected sockets
    
    def receive(self):
        # Get data from connected input
    
    def connect_to(self, other_socket):
        # Establish connection

class SocketManager:
    def __init__(self):
        self.connections = {}
    
    def connect_sockets(self, output_socket, input_socket):
        # Manage socket connections
```

### 2. **Language Extensions** (~200-300 lines)

```python
# Add to existing lexer.py:
SOCKET = "SOCKET"
CONNECT = "CONNECT" 
DISCONNECT = "DISCONNECT"

# Add to existing parser.py:
def parse_socket_declaration(self):
    # Parse: socket attack_choice_output
    
def parse_connect_statement(self):
    # Parse: connect_socket upon ai.output, familiar.input

# Add to existing interpreter.py:
def execute_socket_declaration(self, node):
    # Create socket on familiar
    
def execute_connect_statement(self, node):
    # Establish socket connection
```

### 3. **Enhanced Familiar Base Class** (~100-200 lines)

```python
# Modify existing familiar.py:
class Familiar:
    def __init__(self, name, pacts):
        # ... existing code ...
        self.sockets = {}  # Add socket management
    
    def add_socket(self, name, socket_type, direction):
        # Create socket on this familiar
        
    def get_socket(self, name):
        # Retrieve socket by name
        
    def send_to_socket(self, socket_name, data):
        # Send data through output socket
        
    def receive_from_socket(self, socket_name):
        # Receive data from input socket
```

## Implementation Effort Estimate

### **Small Changes** (1-2 days):

- Add socket keywords to lexer
- Extend parser for socket syntax
- Add socket commands to interpreter

### **Medium Changes** (3-5 days):

- Implement Socket and SocketManager classes
- Add socket support to Familiar base class
- Create connection management system

### **Integration Work** (2-3 days):

- Update existing familiar implementations
- Add socket examples and tests
- Update CLI help system

### Total Effort: **1-2 weeks** for a solid socket implementation

## Minimal Working Example

You could actually implement a basic version quite quickly:

python

```python
# Quick socket prototype (grimoire/sockets.py)
class Socket:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.connections = []
        self.value = None
    
    def connect_to(self, other_socket):
        self.connections.append(other_socket)
    
    def send(self, data):
        for connected_socket in self.connections:
            connected_socket.receive_data(data)
    
    def receive_data(self, data):
        self.value = data

# Add to existing Familiar class:
def add_socket(self, name):
    self.sockets[name] = Socket(name, self)
    return self.sockets[name]
```

Then you could start using it immediately:

grimoire

```grimoire
# Create familiars with sockets
bind combat_familiar = create_familiar_with_pact(...)
bind ai_familiar = create_familiar_with_pact(...)

# Connect them (via Python API initially)
connect_sockets(ai_familiar.attack_output, combat_familiar.attack_input)
```
## Goal Artifact Architecture

### 1. **Goal as Programmable Artifact**

```
artifact TerritorialControlGoal:
	# Goal metadata
	bind name = $SCROLL(territorial_control)
	bind priority = 0.8
	bind domain = $SCROLL(Combat)
	
	# State tracking
	bind controlled_territory = 0
	bind total_territory = 100
	bind target_percentage = 0.75
	
	# Evaluation method - returns satisfaction level (0.0 to 1.0)
	ritual evaluate_satisfaction(world_state):
		bind current_control = world_state.get_territory_control(self.domain)
		bind satisfaction = current_control divided by (self.total_territory multiplied by self.target_percentage)
		return satisfaction
	
	# Progress tracking
	ritual get_progress_metrics():
		return {
			current: self.controlled_territory,
			target: self.total_territory multiplied by self.target_percentage,
			percentage: self.evaluate_satisfaction(current_world_state)
		}
	
	# Action suggestions - what actions would help achieve this goal
	ritual suggest_actions(available_actions, world_state):
		bind suggestions = []
		for action in available_actions:
			if action.affects_territory():
				suggestions.append(action)
		return suggestions
	
	# Goal completion check
	ritual is_satisfied(world_state):
		return self.evaluate_satisfaction(world_state) >= 0.95
```

### 2. **Different Goal Types for Different Domains**

```
# Economic goal
artifact ResourceAccumulationGoal:
	bind name = $SCROLL(resource_accumulation)
	bind target_resources = {gold: 1000, wood: 500, stone: 300}
	bind current_resources = {gold: 0, wood: 0, stone: 0}
	
	ritual evaluate_satisfaction(world_state):
		bind total_satisfaction = 0.0
		bind resource_count = 0
		
		for resource_type in self.target_resources:
			bind current = world_state.get_resource_amount(resource_type)
			bind target = self.target_resources[resource_type]
			bind resource_satisfaction = current divided by target
			if resource_satisfaction > 1.0:
				resource_satisfaction = 1.0
			total_satisfaction = total_satisfaction added to resource_satisfaction
			resource_count = resource_count added to 1
		
		return total_satisfaction divided by resource_count

# CRM application goal
artifact CustomerSatisfactionGoal:
	bind name = $SCROLL(customer_satisfaction)
	bind target_satisfaction_score = 4.5
	bind minimum_response_time = 24  # hours
	
	ritual evaluate_satisfaction(world_state):
		bind avg_satisfaction = world_state.get_average_customer_rating()
		bind avg_response_time = world_state.get_average_response_time()
		
		bind satisfaction_score = avg_satisfaction divided by self.target_satisfaction_score
		bind response_score = self.minimum_response_time divided by avg_response_time
		
		# Combined weighted score
		return (satisfaction_score multiplied by 0.7) added to (response_score multiplied by 0.3)
```

### 3. **Goal Templates for Common Patterns**

```
# Base template for threshold-based goals
artifact ThresholdGoal:
	bind current_value = 0
	bind target_value = 100
	bind threshold_percentage = 0.9
	
	ritual evaluate_satisfaction(world_state):
		self.current_value = self.get_current_value(world_state)
		bind progress = self.current_value divided by self.target_value
		return progress
	
	# Abstract method - subclasses must implement
	ritual get_current_value(world_state):
		# Override in subclasses
		pass

# Specific implementation
artifact ArmySizeGoal extends ThresholdGoal:
	ritual get_current_value(world_state):
		return world_state.count_military_units()
```
### 4. **Goal Factory for Dynamic Creation**

```
artifact GoalFactory:
	ritual create_combat_goal(target_territory_percent):
		bind goal = conjure TerritorialControlGoal upon
		goal.target_percentage = target_territory_percent
		return goal
	
	ritual create_economic_goal(resource_targets):
		bind goal = conjure ResourceAccumulationGoal upon
		goal.target_resources = resource_targets
		return goal
	
	ritual create_custom_goal(goal_type, parameters):
		# Dynamic goal creation based on type
		if goal_type == $SCROLL(territory):
			return self.create_combat_goal(parameters.territory_percent)
		elif goal_type == $SCROLL(resources):
			return self.create_economic_goal(parameters.resource_map)
```

## Benefits of Programmable Goals
### 1. **Objective Measurement**

```
# Goals can be tested and validated
ritual test_territorial_goal():
	bind goal = conjure TerritorialControlGoal upon
	bind mock_world = create_test_world_state upon
	mock_world.set_territory_control($SCROLL(Combat), 60)
	
	bind satisfaction = goal.evaluate_satisfaction(mock_world)
	scry $SCROLL(Goal satisfaction: ) added to satisfaction
	# Expected: 0.8 (60% of 75% target)
```
### 2. **Composable and Reusable**

```
# Goals can be combined and shared
bind combat_goals = [
	conjure TerritorialControlGoal upon,
	conjure DefensivePositionGoal upon,
	conjure ArmySizeGoal upon
]

bind economic_goals = [
	conjure ResourceAccumulationGoal upon,
	conjure TradeRouteGoal upon,
	conjure MarketShareGoal upon
]
```

### 3. **Domain-Agnostic Framework**

```
# Same goal architecture works for any domain
bind game_goals = load_goals_from_config upon $SCROLL(game_config.json)
bind crm_goals = load_goals_from_config upon $SCROLL(crm_config.json)
bind iot_goals = load_goals_from_config upon $SCROLL(iot_config.json)
```

## Integration with Existing Agent System

### 1. **Agent Goal Management**

```
# Agents use programmable goals
artifact CombatArchon extends Archon:
	ritual initialize_goals():
		bind territory_goal = conjure TerritorialControlGoal upon
		territory_goal.target_percentage = 0.8
		
		bind army_goal = conjure ArmySizeGoal upon
		army_goal.target_value = 50
		
		self.add_goal(territory_goal)
		self.add_goal(army_goal)
	
	ritual evaluate_current_goals(world_state):
		for goal in self.goals:
			bind satisfaction = goal.evaluate_satisfaction(world_state)
			scry $SCROLL(Goal ) added to goal.name added to $SCROLL(: ) added to satisfaction
```

### 2. **Goal-Driven Decision Making**

```
# Actions can be evaluated against multiple goals
ritual choose_best_action(available_actions, world_state):
	bind best_action = null
	bind best_score = 0.0
	
	for action in available_actions:
		bind total_score = 0.0
		
		for goal in self.goals:
			# Simulate action outcome
			bind projected_world = world_state.simulate_action(action)
			bind new_satisfaction = goal.evaluate_satisfaction(projected_world)
			bind current_satisfaction = goal.evaluate_satisfaction(world_state)
			bind improvement = new_satisfaction subtracted from current_satisfaction
			
			# Weight by goal priority
			total_score = total_score added to (improvement multiplied by goal.priority)
		
		if total_score > best_score:
			best_score = total_score
			best_action = action
	
	return best_action
```

### 3. **Goal Communication via Sockets**

```
# Goals can expose progress via sockets
artifact TerritorialControlGoal:
	# ... existing code ...
	
	socket progress_output
	socket satisfaction_output
	socket completion_status_output
	
	ritual update_sockets(world_state):
		bind progress = self.get_progress_metrics()
		bind satisfaction = self.evaluate_satisfaction(world_state)
		bind is_complete = self.is_satisfied(world_state)
		
		self.progress_output.send(progress)
		self.satisfaction_output.send(satisfaction)
		self.completion_status_output.send(is_complete)
```

This approach transforms goals from vague aspirations into concrete, testable, measurable components that can drive intelligent agent behavior. The magic isn't in trying to understand semantic meaning - it's in providing an elegant framework for developers to express complex objectives in executable code!

## Thematic variants 
### Add to grimoire/keyword_variants.py
```
GOAL': {
   MagicSchool.NEUTRAL: ['objective', 'target', 'aim'],
   MagicSchool.LIGHT: ['vow', 'oath', 'pledge'],
   MagicSchool.SHADOW: ['ambition', 'desire', 'craving'],
   MagicSchool.NATURE: ['drive', 'instinct', 'urge'],
   MagicSchool.DIVINE: ['mandate', 'decree', 'commandment'],
   MagicSchool.ARCANE: ['concordance', 'theorem', 'principle'],
   MagicSchool.TRICKSTER: ['gambit', 'scheme', 'ploy']
}
```

### Thematic usage examples:

#### Light Magic - Sacred Vows

```artifact TerritorialVow:
	bind name = $SCROLL(territorial_vow)
	bind sacred_promise = $SCROLL(Protect the holy lands)
	
	blessing evaluate_oath_fulfillment(world_state):
		bind sanctified_territory = world_state.get_blessed_territory()
		return sanctified_territory divided by promised_protection_area
```
#### Shadow Magic - Dark Ambitions
```
artifact PowerAmbition:
	bind name = $SCROLL(power_ambition)
	bind burning_desire = 0.9
	
	curse evaluate_hunger(world_state):
		bind consumed_power = world_state.get_absorbed_energy()
		return consumed_power divided by ultimate_dominion_threshold
```
#### Nature Magic - Primal Drives
```
artifact TerritorialDrive:
	bind name = $SCROLL(territorial_drive)
	bind pack_instinct = $SCROLL(Expand the forest domain)
	
	song evaluate_natural_urge(world_state):
		bind wild_territory = world_state.get_untamed_lands()
		return wild_territory divided by ancestral_homeland_size
```
#### Divine Magic - Sacred Mandates
```
artifact CelestialMandate:
	bind name = $SCROLL(celestial_mandate)
	bind divine_will = $SCROLL(Establish righteous order)
	
	miracle evaluate_divine_progress(world_state):
		bind righteous_control = world_state.get_lawful_territory()
		return righteous_control divided by prophesied_kingdom_size

```
#### Arcane Magic - Logical Concordances
```
artifact StrategicConcordance:
	bind name = $SCROLL(strategic_concordance)
	bind mathematical_proof = 0.0
	
	formula evaluate_logical_progression(world_state):
		bind territorial_data = world_state.get_control_metrics()
		bind proof_completion = territorial_data divided by theoretical_maximum
		return proof_completion

```
#### Trickster Magic - Cunning Gambits
```
artifact ChaosGambit:
	bind name = $SCROLL(chaos_gambit)
	bind mischief_factor = 0.8
	
	prank evaluate_scheme_success(world_state):
		bind disrupted_order = world_state.get_chaos_metrics()
		bind expected_mayhem = planned_disruption_level
		return disrupted_order divided by expected_mayhem

```


### Agent creation examples:
#### Light Magic archon with sacred vows
```
bind paladin_archon = create_archon upon $SCROLL(HolyCommander), $SCROLL(Combat)
bind protection_vow = conjure TerritorialVow upon
bind healing_vow = conjure RestorationVow upon
paladin_archon.add_vow(protection_vow)
paladin_archon.add_vow(healing_vow)
```
#### Shadow Magic archon with dark ambitions
```
bind necromancer_archon = create_archon upon $SCROLL(DeathLord), $SCROLL(Combat)
bind power_ambition = conjure DominationAmbition upon
bind corruption_ambition = conjure CorruptionAmbition upon
necromancer_archon.add_ambition(power_ambition)
necromancer_archon.add_ambition(corruption_ambition)
```
#### Trickster Magic archon with chaotic gambits
```
bind chaos_archon = create_archon upon $SCROLL(Jester), $SCROLL(Disruption)
bind confusion_gambit = conjure DisruptionGambit upon
bind unpredictability_gambit = conjure ChaosGambit upon
chaos_archon.add_gambit(confusion_gambit)
chaos_archon.add_gambit(unpredictability_gambit)
```