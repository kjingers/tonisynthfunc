"""
Character Voice Expressions Module

Parses story text to detect characters and dialogue, then generates SSML
with appropriate voice and expression changes for each character.

Enable with: enable_character_voices=True in API request
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CharacterVoice:
    """Configuration for a character's voice"""
    voice_name: str
    default_style: Optional[str] = None
    gender: str = "neutral"  # male, female, neutral


@dataclass
class DialogueSegment:
    """A segment of text with associated voice/style"""
    text: str
    voice_name: str
    style: Optional[str] = None
    is_dialogue: bool = False
    character: Optional[str] = None


# ===========================================
# Default Character Voice Mappings
# ===========================================

# Female voices (with style support)
FEMALE_VOICES = [
    "en-US-JennyNeural",   # Versatile, many styles
    "en-US-AriaNeural",    # Expressive
    "en-US-SaraNeural",    # Warm
]

# Male voices (with style support)
MALE_VOICES = [
    "en-US-GuyNeural",     # Deep, versatile
    "en-US-DavisNeural",   # Expressive
    "en-US-TonyNeural",    # Friendly
]

# Child voices
CHILD_VOICES = [
    "en-US-AnaNeural",     # Child female
]

# Default narrator voice
DEFAULT_NARRATOR_VOICE = "en-US-GuyNeural"
DEFAULT_NARRATOR_STYLE = "friendly"

# ===========================================
# Expression Detection Patterns
# ===========================================

EXPRESSION_PATTERNS = {
    "whispering": [
        r'\bwhispered?\b',
        r'\bwhispering\b',
        r'\bquietly\b',
        r'\bsoftly\b',
        r'\bin a low voice\b',
        r'\bhushed\b',
    ],
    "shouting": [
        r'\bshouted?\b',
        r'\bshouting\b',
        r'\byelled?\b',
        r'\byelling\b',
        r'\bscreamed?\b',
        r'\bscreaming\b',
        r'\bcried out\b',
        r'\bexclaimed\b',
    ],
    "excited": [
        r'\bexcitedly\b',
        r'\bexclaimed\b',
        r'\benthusiastically\b',
        r'\beagerly\b',
        r'\bjoyfully\b',
    ],
    "sad": [
        r'\bsadly\b',
        r'\bsorrowfully\b',
        r'\btearfully\b',
        r'\bweeping\b',
        r'\bsobbed?\b',
        r'\bsobbing\b',
        r'\bmournfully\b',
    ],
    "angry": [
        r'\bangrily\b',
        r'\bfuriously\b',
        r'\bsnarled?\b',
        r'\bgrowled?\b',
        r'\braged?\b',
    ],
    "terrified": [
        r'\bterrified\b',
        r'\bfrightened\b',
        r'\bscared\b',
        r'\btrembling\b',
        r'\bfearfully\b',
        r'\bwith fear\b',
    ],
    "cheerful": [
        r'\bcheerfully\b',
        r'\bhappily\b',
        r'\bbrightly\b',
        r'\bwith a smile\b',
        r'\blaughed?\b',
        r'\blaughing\b',
        r'\bgiggled?\b',
    ],
    "hopeful": [
        r'\bhopefully\b',
        r'\boptimistically\b',
        r'\bwith hope\b',
    ],
}

# Common character name patterns (for gender detection)
FEMALE_NAME_PATTERNS = [
    r'\b(she|her|mother|mom|mommy|grandmother|grandma|queen|princess|'
    r'aunt|sister|daughter|wife|girl|woman|lady|miss|mrs|ms)\b',
]

MALE_NAME_PATTERNS = [
    r'\b(he|him|his|father|dad|daddy|grandfather|grandpa|king|prince|'
    r'uncle|brother|son|husband|boy|man|gentleman|mr|sir)\b',
]

# Common female names
FEMALE_NAMES = {
    'mary', 'anna', 'emma', 'sophia', 'olivia', 'ava', 'isabella', 'mia',
    'charlotte', 'amelia', 'harper', 'evelyn', 'abigail', 'emily', 'elizabeth',
    'sarah', 'rachel', 'rebecca', 'ruth', 'esther', 'miriam', 'hannah', 'leah',
    'martha', 'maria', 'lucy', 'alice', 'rose', 'grace', 'lily', 'ella',
    'mom', 'mommy', 'mother', 'grandmother', 'grandma', 'princess', 'queen',
    'elena', 'aurora', 'belle', 'cinderella', 'ariel', 'elsa', 'anna',
    'she', 'her', 'witch', 'fairy', 'goddess',
}

# Common male names
MALE_NAMES = {
    'james', 'john', 'robert', 'michael', 'david', 'william', 'joseph', 'thomas',
    'charles', 'daniel', 'matthew', 'anthony', 'mark', 'paul', 'peter', 'luke',
    'adam', 'noah', 'abraham', 'moses', 'jacob', 'isaac', 'samuel', 'joshua',
    'dad', 'daddy', 'father', 'grandfather', 'grandpa', 'prince', 'king',
    'jesus', 'god', 'lord', 'sir', 'cedric', 'arthur', 'lancelot', 'merlin',
    'he', 'him', 'dragon', 'wizard', 'knight', 'giant', 'troll', 'ogre',
}


def detect_gender(character_name: str, context: str = "") -> str:
    """
    Detect likely gender of a character based on name and context.
    Returns: 'male', 'female', or 'neutral'
    """
    name_lower = character_name.lower().strip()
    
    # Check known names
    if name_lower in FEMALE_NAMES:
        return "female"
    if name_lower in MALE_NAMES:
        return "male"
    
    # Check context for pronouns
    context_lower = context.lower()
    
    # Look for nearby gender indicators
    female_score = sum(1 for pattern in FEMALE_NAME_PATTERNS 
                       if re.search(pattern, context_lower))
    male_score = sum(1 for pattern in MALE_NAME_PATTERNS 
                     if re.search(pattern, context_lower))
    
    if female_score > male_score:
        return "female"
    elif male_score > female_score:
        return "male"
    
    return "neutral"


def detect_expression(text: str) -> Optional[str]:
    """
    Detect speaking expression/style from dialogue attribution.
    Returns style name or None.
    """
    text_lower = text.lower()
    
    for style, patterns in EXPRESSION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return style
    
    return None


def get_voice_for_gender(gender: str, voice_index: int = 0) -> str:
    """Get appropriate voice for gender"""
    if gender == "female":
        return FEMALE_VOICES[voice_index % len(FEMALE_VOICES)]
    elif gender == "male":
        return MALE_VOICES[voice_index % len(MALE_VOICES)]
    else:
        # Alternate between male and female for variety
        all_voices = MALE_VOICES + FEMALE_VOICES
        return all_voices[voice_index % len(all_voices)]


class CharacterVoiceParser:
    """
    Parses story text and assigns voices/expressions to characters.
    """
    
    def __init__(self, 
                 narrator_voice: str = DEFAULT_NARRATOR_VOICE,
                 narrator_style: str = DEFAULT_NARRATOR_STYLE,
                 character_overrides: Dict[str, CharacterVoice] = None):
        """
        Initialize parser with optional character voice overrides.
        
        Args:
            narrator_voice: Voice for narration (non-dialogue)
            narrator_style: Default style for narration
            character_overrides: Dict mapping character names to CharacterVoice
        """
        self.narrator_voice = narrator_voice
        self.narrator_style = narrator_style
        self.character_overrides = character_overrides or {}
        self.character_cache: Dict[str, CharacterVoice] = {}
        self.voice_index = 0
    
    def get_character_voice(self, character: str, context: str = "") -> CharacterVoice:
        """Get or create voice configuration for a character"""
        char_lower = character.lower().strip()
        
        # Check overrides first
        if char_lower in self.character_overrides:
            return self.character_overrides[char_lower]
        
        # Check cache
        if char_lower in self.character_cache:
            return self.character_cache[char_lower]
        
        # Create new voice assignment
        gender = detect_gender(character, context)
        voice = get_voice_for_gender(gender, self.voice_index)
        self.voice_index += 1
        
        char_voice = CharacterVoice(
            voice_name=voice,
            gender=gender
        )
        self.character_cache[char_lower] = char_voice
        return char_voice
    
    def parse_dialogue(self, text: str) -> List[DialogueSegment]:
        """
        Parse text into segments with dialogue attribution.
        
        Detects patterns like:
        - "Hello," said Mary.
        - "Hello," Mary said.
        - "Hello!" she exclaimed.
        - Mary said, "Hello."
        - The dragon laughed. "Hello!"
        - Princess Elena called, "Hello!"
        """
        segments = []
        
        # Speech verbs for pattern matching (including actions that can precede dialogue)
        speech_verbs = r'(?:said|asked|replied|whispered|shouted|exclaimed|cried|yelled|murmured|muttered|declared|called|laughed|roared|growled|hissed|screamed|bellowed|demanded|answered|responded|snapped|snarled|cooed|sighed|smiled|grinned|frowned|nodded)'
        
        # Pattern for dialogue with attribution after
        # Matches: "dialogue" [attribution with speaker]
        pattern_after = r'"([^"]+)"[\s,]*([^"]*?)(?="|$|\n\n|\n[A-Z])'
        
        # Pattern for dialogue with attribution before (with comma before quote)
        # Matches: [speaker] said/called/etc, "dialogue"
        # Handles: "Princess Elena called from the tower, \"dialogue\""
        pattern_before_comma = rf'((?:Sir|Lord|Lady|King|Queen|Prince|Princess|The|Dr|Mr|Mrs|Ms)\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+{speech_verbs}[^"]*,\s*"([^"]+)"'
        
        # Pattern for dialogue with attribution before (direct)
        # Matches: [speaker] said "dialogue"
        pattern_before_direct = rf'((?:Sir|Lord|Lady|King|Queen|Prince|Princess|The|Dr|Mr|Mrs|Ms)\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+{speech_verbs}\s*"([^"]+)"'
        
        # Pattern for action then dialogue (sentence boundary)
        # Matches: "[Someone] [action]. "dialogue""
        # E.g., "The dragon laughed menacingly. \"You shall not pass!\""
        # Requires the character to perform a speech-related action (laughed, smiled, etc.)
        # The action must be followed by period, then dialogue
        action_verbs = r'(?:laughed|smiled|grinned|frowned|nodded|sighed|growled|roared|hissed|snarled|chuckled|giggled|snickered|cackled|bellowed|thundered|boomed)'
        pattern_action_dialogue = rf'(The\s+[a-z]+|[A-Z][a-z]+)\s+{action_verbs}[^"\.]*\.\s*"([^"]+)"'
        
        # Split text into chunks, preserving structure
        last_end = 0
        matches = []
        
        # IMPORTANT: Process more specific patterns FIRST to get proper character attribution
        # Then use generic pattern_after only for remaining unmatched dialogue
        
        # 1. Find dialogue with attribution before (comma style)
        # E.g., "Princess Elena called from the tower, "dialogue""
        for match in re.finditer(pattern_before_comma, text, re.DOTALL):
            character = match.group(1)
            dialogue = match.group(2)
            
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'dialogue': dialogue,
                'attribution': f"{character} said",
                'character': character,
                'expression': None,
            })
        
        # 2. Find dialogue with attribution before (direct style)
        # E.g., "Mary said "dialogue""
        for match in re.finditer(pattern_before_direct, text, re.DOTALL):
            character = match.group(1)
            dialogue = match.group(2)
            
            # Skip if overlaps with existing match
            if any(m['start'] <= match.start() < m['end'] or 
                   match.start() <= m['start'] < match.end() for m in matches):
                continue
            
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'dialogue': dialogue,
                'attribution': f"{character} said",
                'character': character,
                'expression': None,
            })
        
        # 3. Find action-then-dialogue patterns
        # E.g., "The dragon laughed menacingly. "dialogue""
        for match in re.finditer(pattern_action_dialogue, text, re.DOTALL):
            character = match.group(1)
            dialogue = match.group(2)
            
            # Skip if overlaps with existing match
            if any(m['start'] <= match.start() < m['end'] or 
                   match.start() <= m['start'] < match.end() for m in matches):
                continue
            
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'dialogue': dialogue,
                'attribution': f"{character}",
                'character': character,
                'expression': None,
            })
        
        # 4. LAST: Find remaining dialogue with attribution after (generic fallback)
        # E.g., "dialogue" said Mary. or "dialogue" she whispered.
        for match in re.finditer(pattern_after, text, re.DOTALL):
            dialogue = match.group(1)
            attribution = match.group(2).strip()
            
            # Skip if this dialogue was already matched by a more specific pattern
            if any(m['start'] <= match.start() < m['end'] or 
                   match.start() <= m['start'] < match.end() for m in matches):
                continue
            
            # Extract character name from attribution
            character = self._extract_character(attribution)
            expression = detect_expression(attribution)
            
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'dialogue': dialogue,
                'attribution': attribution,
                'character': character,
                'expression': expression,
            })
        
        # Sort matches by position
        matches.sort(key=lambda x: x['start'])
        
        # Build segments
        for match in matches:
            # Add narration before this dialogue
            if match['start'] > last_end:
                narration = text[last_end:match['start']].strip()
                if narration:
                    segments.append(DialogueSegment(
                        text=narration,
                        voice_name=self.narrator_voice,
                        style=self.narrator_style,
                        is_dialogue=False
                    ))
            
            # Add dialogue segment
            character = match['character']
            if character:
                char_voice = self.get_character_voice(character, match['attribution'])
                voice = char_voice.voice_name
            else:
                voice = self.narrator_voice
            
            segments.append(DialogueSegment(
                text=match['dialogue'],
                voice_name=voice,
                style=match['expression'] or char_voice.default_style if character else None,
                is_dialogue=True,
                character=character
            ))
            
            # Add attribution as narration if substantial
            attr_text = match['attribution'].strip()
            if attr_text and len(attr_text) > 20:
                segments.append(DialogueSegment(
                    text=attr_text,
                    voice_name=self.narrator_voice,
                    style=self.narrator_style,
                    is_dialogue=False
                ))
            
            last_end = match['end']
        
        # Add remaining narration
        if last_end < len(text):
            remaining = text[last_end:].strip()
            if remaining:
                segments.append(DialogueSegment(
                    text=remaining,
                    voice_name=self.narrator_voice,
                    style=self.narrator_style,
                    is_dialogue=False
                ))
        
        # If no dialogue found, treat entire text as narration
        if not segments:
            segments.append(DialogueSegment(
                text=text,
                voice_name=self.narrator_voice,
                style=self.narrator_style,
                is_dialogue=False
            ))
        
        return segments
    
    def _extract_character(self, attribution: str) -> Optional[str]:
        """Extract character name from dialogue attribution"""
        # Common patterns: "said Mary", "Mary said", "she whispered"
        # Also handles: "Sir Cedric declared", "The dragon laughed", "Princess Elena called"
        
        # Speech verbs for pattern matching
        speech_verbs = r'(?:said|asked|replied|whispered|shouted|exclaimed|cried|yelled|murmured|muttered|declared|called|laughed|roared|growled|hissed|screamed|bellowed|demanded|answered|responded|snapped|snarled|cooed|sighed)'
        
        # Try to find multi-word name before verb (e.g., "Sir Cedric declared", "The dragon laughed")
        # Match: Title/The + Name + verb, or Name Name + verb
        match = re.search(rf'^((?:Sir|Lord|Lady|King|Queen|Prince|Princess|The|Dr|Mr|Mrs|Ms)\s+[A-Z][a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+{speech_verbs}', attribution)
        if match:
            return match.group(1).strip()
        
        # Try single capitalized name before verb (e.g., "Mary said")
        match = re.search(rf'^([A-Z][a-z]+)\s+{speech_verbs}', attribution)
        if match:
            return match.group(1)
        
        # Try to find name after verb (e.g., "said Sir Cedric", "said Mary", "replied the knight")
        # Handles both capitalized names and "the [role]" patterns
        match = re.search(rf'{speech_verbs}\s+((?:Sir|Lord|Lady|King|Queen|Prince|Princess|The|Dr|Mr|Mrs|Ms)\s+[A-Z][a-z]+|the\s+[a-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', attribution, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try single name after verb
        match = re.search(rf'{speech_verbs}\s+([A-Z][a-z]+)', attribution)
        if match:
            return match.group(1)
        
        # Check for pronouns
        if re.search(r'\bshe\b', attribution.lower()):
            return "she"  # Will be mapped to female voice
        if re.search(r'\bhe\b', attribution.lower()):
            return "he"  # Will be mapped to male voice
        
        return None


def generate_character_ssml(text: str, 
                           narrator_voice: str = DEFAULT_NARRATOR_VOICE,
                           narrator_style: str = DEFAULT_NARRATOR_STYLE,
                           character_overrides: Dict[str, Dict] = None) -> str:
    """
    Generate SSML with character voice expressions.
    
    Args:
        text: Story text with dialogue
        narrator_voice: Voice for narration
        narrator_style: Style for narration
        character_overrides: Dict of character name -> {voice, style, gender}
    
    Returns:
        SSML string with voice/style changes
    """
    # Convert overrides to CharacterVoice objects
    overrides = {}
    if character_overrides:
        for name, config in character_overrides.items():
            overrides[name.lower()] = CharacterVoice(
                voice_name=config.get('voice', DEFAULT_NARRATOR_VOICE),
                default_style=config.get('style'),
                gender=config.get('gender', 'neutral')
            )
    
    parser = CharacterVoiceParser(
        narrator_voice=narrator_voice,
        narrator_style=narrator_style,
        character_overrides=overrides
    )
    
    segments = parser.parse_dialogue(text)
    
    # Build SSML
    ssml_parts = [
        "<speak version='1.0' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>"
    ]
    
    current_voice = None
    
    for segment in segments:
        # Escape special XML characters in text
        escaped_text = escape_ssml_text(segment.text)
        
        # Open voice tag if different from current
        if segment.voice_name != current_voice:
            if current_voice is not None:
                ssml_parts.append("</voice>")
            ssml_parts.append(f"<voice name='{segment.voice_name}'>")
            current_voice = segment.voice_name
        
        # Add style if specified
        if segment.style:
            ssml_parts.append(f"<mstts:express-as style='{segment.style}'>")
            ssml_parts.append(escaped_text)
            ssml_parts.append("</mstts:express-as>")
        else:
            ssml_parts.append(escaped_text)
    
    # Close final voice tag
    if current_voice is not None:
        ssml_parts.append("</voice>")
    
    ssml_parts.append("</speak>")
    
    return "\n".join(ssml_parts)


def escape_ssml_text(text: str) -> str:
    """Escape special characters for SSML"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


def generate_simple_ssml(text: str, voice: str, style: Optional[str] = None) -> str:
    """Generate simple SSML without character parsing (original behavior)"""
    escaped_text = escape_ssml_text(text)
    
    if style:
        return f"""<speak version='1.0' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
    <voice name='{voice}'>
        <mstts:express-as style='{style}'>
            {escaped_text}
        </mstts:express-as>
    </voice>
</speak>"""
    else:
        return f"""<speak version='1.0' xml:lang='en-US'>
    <voice xml:lang='en-US' name='{voice}'>
        {escaped_text}
    </voice>
</speak>"""
