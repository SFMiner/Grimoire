#!/usr/bin/env python3
"""
Grimoire Keyword Variants System

This system allows multiple equivalent keywords for the same functionality,
enabling more expressive and thematically appropriate code.
"""

from enum import Enum, auto
from typing import Dict, List, Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import TokenType


class MagicSchool(Enum):
    """Different schools of magic that influence keyword choice."""
    NEUTRAL = auto()
    LIGHT = auto()      # Healing, protection, positive magic
    SHADOW = auto()     # Destructive, dark magic  
    NATURE = auto()     # Elemental, growth magic
    DIVINE = auto()     # Holy, celestial magic
    ARCANE = auto()     # Pure magic, scholarly
    TRICKSTER = auto()  # Mischief, transformation


class KeywordVariants:
    """Manages equivalent keywords for Grimoire language features."""
    
    def __init__(self):
        # Core language constructs with thematic variants
        self.variants = {
            # Variable assignment
            'BIND': {
                MagicSchool.NEUTRAL: ['bind', 'set', 'assign'],
                MagicSchool.LIGHT: ['bless', 'consecrate', 'sanctify'],
                MagicSchool.SHADOW: ['curse', 'hex', 'doom'],
                MagicSchool.NATURE: ['grow', 'cultivate', 'nurture'],
                MagicSchool.DIVINE: ['ordain', 'decree', 'proclaim'],
                MagicSchool.ARCANE: ['inscribe', 'encode', 'cipher'],
                MagicSchool.TRICKSTER: ['trick', 'swap', 'transform']
            },
            
            # Output/printing
            'SCRY': {
                MagicSchool.NEUTRAL: ['scry', 'display', 'show'],
                MagicSchool.LIGHT: ['illuminate', 'reveal', 'enlighten'],
                MagicSchool.SHADOW: ['whisper', 'manifest', 'materialize'],
                MagicSchool.NATURE: ['sing', 'echo', 'resonate'],
                MagicSchool.DIVINE: ['prophesy', 'proclaim', 'herald'],
                MagicSchool.ARCANE: ['divine', 'calculate', 'compute'],
                MagicSchool.TRICKSTER: ['announce', 'jest', 'mock']
            },
            
            # Property access/mystical getter
            'EVOKE': {
                MagicSchool.NEUTRAL: ['evoke', 'get', 'retrieve'],
                MagicSchool.LIGHT: ['divine', 'illuminate', 'reveal'],
                MagicSchool.SHADOW: ['extract', 'drain', 'siphon'],
                MagicSchool.NATURE: ['sense', 'feel', 'perceive'],
                MagicSchool.DIVINE: ['behold', 'witness', 'receive'],
                MagicSchool.ARCANE: ['query', 'analyze', 'probe'],
                MagicSchool.TRICKSTER: ['peek', 'spy', 'discover']
            },
            
            # Function definition
            'RITUAL': {
                MagicSchool.NEUTRAL: ['ritual', 'spell', 'procedure'],
                MagicSchool.LIGHT: ['blessing', 'prayer', 'invocation'],
                MagicSchool.SHADOW: ['curse', 'incantation', 'dark_ritual'],
                MagicSchool.NATURE: ['song', 'growth', 'cycle'],
                MagicSchool.DIVINE: ['miracle', 'commandment', 'decree'],
                MagicSchool.ARCANE: ['formula', 'theorem', 'algorithm'],
                MagicSchool.TRICKSTER: ['prank', 'trick', 'jest']
            },
            
            # Object creation
            'CONJURE': {
                MagicSchool.NEUTRAL: ['conjure', 'create', 'make'],
                MagicSchool.LIGHT: ['call forth', 'manifest'],
                MagicSchool.SHADOW: ['raise', 'spawn', 'birth'],
                MagicSchool.NATURE: ['sprout', 'bloom', 'emerge'],
                MagicSchool.DIVINE: ['create', 'forge', 'craft'],
                MagicSchool.ARCANE: ['instantiate', 'construct', 'compile'],
                MagicSchool.TRICKSTER: ['poof', 'materialize', 'surprise']
            },
            
            # Class definition
            'ARTIFACT': {
                MagicSchool.NEUTRAL: ['artifact', 'class', 'blueprint'],
                MagicSchool.LIGHT: ['relic', 'sacred object', 'holy vessel'],
                MagicSchool.SHADOW: ['cursed item', 'dark relic', 'forbidden tome'],
                MagicSchool.NATURE: ['creature', 'being', 'spirit'],
                MagicSchool.DIVINE: ['creation', 'vessel', 'avatar'],
                MagicSchool.ARCANE: ['construct', 'schema', 'pattern'],
                MagicSchool.TRICKSTER: ['disguise', 'illusion', 'form']
            },
            
            # Conditionals
            'SHOULD': {
                MagicSchool.NEUTRAL: ['should', 'if', 'when'],
                MagicSchool.LIGHT: ['should', 'if blessed', 'when pure'],
                MagicSchool.SHADOW: ['should', 'if cursed', 'when dark'],
                MagicSchool.NATURE: ['should', 'if flourishing', 'when alive'],
                MagicSchool.DIVINE: ['should', 'if ordained', 'when holy'],
                MagicSchool.ARCANE: ['should', 'if logical', 'when proven'],
                MagicSchool.TRICKSTER: ['should', 'if amusing', 'when clever']
            },
            
            'LEST': {
                MagicSchool.NEUTRAL: ['lest', 'else', 'otherwise'],
                MagicSchool.LIGHT: ['lest', 'else darkened', 'otherwise fallen'],
                MagicSchool.SHADOW: ['lest', 'else blessed', 'otherwise pure'],
                MagicSchool.NATURE: ['lest', 'else withered', 'otherwise dead'],
                MagicSchool.DIVINE: ['lest', 'else forsaken', 'otherwise profane'],
                MagicSchool.ARCANE: ['lest', 'else illogical', 'otherwise error'],
                MagicSchool.TRICKSTER: ['lest', 'else boring', 'otherwise obvious']
            }
        }
        
        # Multi-word conditionals and operators
        self.multiword_variants = {
            
            'WHILE_CHARGED': {
                MagicSchool.NEUTRAL: ['while charged', 'while active', 'repeat while'],
                MagicSchool.LIGHT: ['while radiant', 'while glowing', 'while warm'],
                MagicSchool.SHADOW: ['while shrouded', 'while dark', 'while cold'],
                MagicSchool.NATURE: ['while growing', 'while flowing', 'while breathing'],
                MagicSchool.DIVINE: ['while faithful', 'while devoted', 'while blessed'],
                MagicSchool.ARCANE: ['while computing', 'while processing', 'while analyzing'],
                MagicSchool.TRICKSTER: ['while dancing', 'while playing', 'while shifting']
            },
            
            # Increment/Decrement operators
            'STRENGTHEN_BY': {
                MagicSchool.NEUTRAL: ['strengthen by', 'increase by', 'add'],
                MagicSchool.LIGHT: ['empower by', 'brighten by', 'heal by'],
                MagicSchool.SHADOW: ['corrupt by', 'taint by', 'infect by'],
                MagicSchool.NATURE: ['grow by', 'bloom by', 'flourish by'],
                MagicSchool.DIVINE: ['bless by', 'sanctify by', 'elevate by'],
                MagicSchool.ARCANE: ['amplify by', 'increment by', 'enhance by'],
                MagicSchool.TRICKSTER: ['trick by', 'boost by', 'surprise by']
            },
            
            'DIMINISH_BY': {
                MagicSchool.NEUTRAL: ['diminish by', 'reduce by', 'subtract'],
                MagicSchool.LIGHT: ['purify by', 'cleanse by', 'calm by'],
                MagicSchool.SHADOW: ['weaken by', 'darken by', 'drain by'],
                MagicSchool.NATURE: ['wither by', 'fade by', 'shrink by'],
                MagicSchool.DIVINE: ['humble by', 'lower by', 'decrease by'],
                MagicSchool.ARCANE: ['decrement by', 'divide by', 'factor by'],
                MagicSchool.TRICKSTER: ['fool by', 'confuse by', 'mislead by']
            }
        }
        
        # Build reverse lookup for parsing
        self.keyword_to_token = {}
        self.multiword_to_token = {}
        
        # Map single-word variants to token types
        for concept, schools in self.variants.items():
            token_type = getattr(TokenType, concept)
            for school, keywords in schools.items():
                for keyword in keywords:
                    self.keyword_to_token[keyword] = token_type
        
        # Map multi-word variants to token types
        for concept, schools in self.multiword_variants.items():
            token_type = getattr(TokenType, concept)
            for school, keywords in schools.items():
                for keyword in keywords:
                    self.multiword_to_token[keyword] = token_type
    
    def get_token_type(self, keyword: str) -> Optional['TokenType']:
        """Get the token type for a keyword variant."""
        return self.keyword_to_token.get(keyword)
    
    def get_multiword_token_type(self, phrase: str) -> Optional['TokenType']:
        """Get the token type for a multi-word phrase variant."""
        return self.multiword_to_token.get(phrase)
    
    def get_variants(self, concept: str, school: Optional[MagicSchool] = None) -> List[str]:
        """Get all variants for a concept, optionally filtered by school."""
        variants_dict = self.variants.get(concept) or self.multiword_variants.get(concept)
        if not variants_dict:
            return []
        
        if school:
            return variants_dict.get(school, [])
        
        # Return all variants from all schools
        all_variants = []
        for school_variants in variants_dict.values():
            all_variants.extend(school_variants)
        return list(set(all_variants))  # Remove duplicates
    
    def is_valid_keyword(self, keyword: str) -> bool:
        """Check if a keyword is valid in any school."""
        return keyword in self.keyword_to_token
    
    def is_valid_multiword(self, phrase: str) -> bool:
        """Check if a multi-word phrase is valid in any school."""
        return phrase in self.multiword_to_token
    
    def get_all_keywords(self) -> Dict[str, 'TokenType']:
        """Get all single-word keyword mappings."""
        return self.keyword_to_token.copy()
    
    def get_all_multiwords(self) -> Dict[str, 'TokenType']:
        """Get all multi-word phrase mappings."""
        return self.multiword_to_token.copy()
    
    def suggest_alternatives(self, concept: str, current_school: MagicSchool) -> Dict[str, List[str]]:
        """Suggest alternative keywords from other schools."""
        suggestions = {}
        variants_dict = self.variants.get(concept) or self.multiword_variants.get(concept)
        
        if variants_dict:
            for school, keywords in variants_dict.items():
                if school != current_school:
                    suggestions[school.name] = keywords
        return suggestions


class ThematicCodeGenerator:
    """Generates equivalent code in different magical styles."""
    
    def __init__(self):
        self.variants = KeywordVariants()
    
    def convert_code(self, code: str, target_school: MagicSchool) -> str:
        """Convert code from one magical school to another."""
        lines = code.split('\n')
        converted_lines = []
        
        for line in lines:
            converted_line = line
            
            # Replace multi-word phrases first (to avoid partial matches)
            for phrase, token_type in self.variants.multiword_to_token.items():
                if phrase in line:
                    # Find the concept name for this token type
                    concept = token_type.name
                    target_variants = self.variants.get_variants(concept, target_school)
                    if target_variants:
                        converted_line = converted_line.replace(phrase, target_variants[0])
            
            # Replace single-word keywords
            words = converted_line.split()
            converted_words = []
            
            for word in words:
                # Clean word of punctuation for lookup
                clean_word = word.strip('():,.')
                token_type = self.variants.get_token_type(clean_word)
                
                if token_type:
                    concept = token_type.name
                    target_variants = self.variants.get_variants(concept, target_school)
                    if target_variants:
                        # Preserve punctuation
                        punctuation = word[len(clean_word):]
                        converted_words.append(target_variants[0] + punctuation)
                    else:
                        converted_words.append(word)
                else:
                    converted_words.append(word)
            
            converted_lines.append(' '.join(converted_words))
        
        return '\n'.join(converted_lines)
    
    def generate_style_variants(self, base_code: str) -> Dict[str, str]:
        """Generate the same code in all magical school styles."""
        variants = {}
        
        for school in MagicSchool:
            variants[school.name] = self.convert_code(base_code, school)
        
        return variants


# Global instance for easy access
KEYWORD_VARIANTS = KeywordVariants()


# Example usage and demonstration
def demonstrate_keyword_variants():
    """Show how keyword variants work in practice."""
    
    variants = KeywordVariants()
    generator = ThematicCodeGenerator()
    
    print("🧙‍♂️ Grimoire Keyword Variants Demonstration")
    print("=" * 50)
    
    # Show variants for a concept
    print("\n📝 Variants for 'SCRY' (output) concept:")
    for school in MagicSchool:
        keywords = variants.get_variants('SCRY', school)
        print(f"  {school.name:12}: {keywords}")
    
    print("\n📝 Variants for 'RITUAL' (function) concept:")
    for school in MagicSchool:
        keywords = variants.get_variants('RITUAL', school)
        print(f"  {school.name:12}: {keywords}")
    
    # Example base code
    base_code = """blessing healing_spell():
    bless patient_health = 50
    should blessed patient_health is lesser than 100:
        empower patient_health by 25
        illuminate $SCROLL(Patient is healing!)
    lest darkened:
        reveal $SCROLL(Patient is fully healed!)"""
    
    print(f"\n📜 Original Code (Light Magic School):")
    print(base_code)
    
    # Generate variants
    print(f"\n🎨 Style Variants:")
    print("-" * 40)
    
    # Shadow magic version
    shadow_code = generator.convert_code(base_code, MagicSchool.SHADOW)
    print(f"\n🌑 Shadow Magic Style:")
    print(shadow_code)
    
    # Arcane magic version
    arcane_code = generator.convert_code(base_code, MagicSchool.ARCANE)
    print(f"\n🔮 Arcane Magic Style:")
    print(arcane_code)
    
    # Nature magic version
    nature_code = generator.convert_code(base_code, MagicSchool.NATURE)
    print(f"\n🌿 Nature Magic Style:")
    print(nature_code)
    
    print(f"\n🎭 All variants are functionally identical!")
    print("The choice depends on aesthetic preference and thematic consistency.")


if __name__ == "__main__":
    demonstrate_keyword_variants()