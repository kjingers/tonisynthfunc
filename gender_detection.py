"""
Gender Detection Module

Uses Azure OpenAI to intelligently detect character genders and assign appropriate
voices based on story context and character name analysis.
"""

import os
import json
import logging
import hashlib
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

# Try to import openai, but allow fallback if not available
try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AzureOpenAI = None


@dataclass
class CharacterInfo:
    """Information about a detected character"""
    name: str
    gender: str  # "male", "female", "neutral"
    aliases: List[str]  # Other names for this character
    reasoning: str  # Why this gender was assigned


class GenderDetectionError(Exception):
    """Raised when gender detection fails"""
    pass


# Cache for story character analysis to avoid repeated API calls
_character_cache: Dict[str, Dict[str, CharacterInfo]] = {}


def get_cache_key(text: str) -> str:
    """Generate a cache key for a story text"""
    return hashlib.md5(text[:1000].encode()).hexdigest()


def get_openai_client() -> Optional[AzureOpenAI]:
    """
    Create and return an Azure OpenAI client.
    
    Returns:
        AzureOpenAI client or None if not configured
    """
    if not OPENAI_AVAILABLE:
        logging.warning("OpenAI SDK not installed. Install with: pip install openai")
        return None
    
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    
    if not endpoint or not api_key:
        logging.debug("Azure OpenAI not configured. Using fallback gender detection.")
        return None
    
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-08-01-preview"
    )


def analyze_characters_with_llm(text: str, character_names: List[str]) -> Dict[str, CharacterInfo]:
    """
    Use Azure OpenAI to analyze characters and determine their genders.
    
    Args:
        text: The story text for context
        character_names: List of character names found in the text
        
    Returns:
        Dict mapping character names to CharacterInfo
    """
    client = get_openai_client()
    if not client:
        return {}
    
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    
    # Build the prompt
    prompt = f"""Analyze the following story excerpt and determine the gender of each character listed.
Consider:
1. The character's name (common associations)
2. Pronouns used in the text
3. Titles and roles (king/queen, prince/princess, etc.)
4. Cultural and literary context

For each character, provide:
- gender: "male", "female", or "neutral" (for non-human or ambiguous)
- aliases: Other names or titles that refer to the same character
- reasoning: Brief explanation of your determination

Characters to analyze: {json.dumps(character_names)}

Story excerpt (first 2000 characters):
{text[:2000]}

Respond with valid JSON only, in this format:
{{
    "characters": {{
        "CharacterName": {{
            "gender": "male|female|neutral",
            "aliases": ["alias1", "alias2"],
            "reasoning": "Brief explanation"
        }}
    }}
}}"""

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a literary analyst specializing in character identification. You analyze stories to determine character genders based on names, pronouns, roles, and context. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        characters = {}
        for name, info in result.get("characters", {}).items():
            characters[name.lower()] = CharacterInfo(
                name=name,
                gender=info.get("gender", "neutral"),
                aliases=[a.lower() for a in info.get("aliases", [])],
                reasoning=info.get("reasoning", "")
            )
        
        logging.info(f"LLM analyzed {len(characters)} characters: {list(characters.keys())}")
        return characters
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse LLM response as JSON: {e}")
        return {}
    except Exception as e:
        logging.error(f"LLM character analysis failed: {e}")
        return {}


def detect_gender_with_llm(
    character_name: str,
    text: str,
    use_cache: bool = True
) -> Tuple[str, str]:
    """
    Detect gender for a character using LLM analysis.
    
    Args:
        character_name: The character name to analyze
        text: The full story text for context
        use_cache: Whether to use cached results
        
    Returns:
        Tuple of (gender, reasoning)
    """
    cache_key = get_cache_key(text)
    name_lower = character_name.lower().strip()
    
    # Check cache first
    if use_cache and cache_key in _character_cache:
        cached = _character_cache[cache_key]
        
        # Direct match
        if name_lower in cached:
            info = cached[name_lower]
            return info.gender, info.reasoning
        
        # Check aliases
        for char_name, info in cached.items():
            if name_lower in info.aliases:
                return info.gender, f"Alias of {info.name}: {info.reasoning}"
    
    # No cache hit - analyze all characters in the story
    # First, extract all character names from the text
    all_characters = extract_all_character_names(text)
    
    # Add the current character if not already in list
    if name_lower not in [c.lower() for c in all_characters]:
        all_characters.append(character_name)
    
    # Analyze with LLM
    results = analyze_characters_with_llm(text, all_characters)
    
    # Cache results
    if use_cache and results:
        _character_cache[cache_key] = results
    
    # Return result for requested character
    if name_lower in results:
        info = results[name_lower]
        return info.gender, info.reasoning
    
    # Check aliases in results
    for char_name, info in results.items():
        if name_lower in info.aliases:
            return info.gender, f"Alias of {info.name}: {info.reasoning}"
    
    # No result from LLM
    return "neutral", "Could not determine gender"


def extract_all_character_names(text: str) -> List[str]:
    """
    Extract potential character names from story text.
    
    Finds:
    - Capitalized names after dialogue
    - Names with titles (Sir, Princess, etc.)
    - Names before speech verbs
    """
    import re
    
    names = set()
    
    # Pattern for titled names
    titled_pattern = r'(?:Sir|Lord|Lady|King|Queen|Prince|Princess|Dr|Mr|Mrs|Ms)\s+([A-Z][a-z]+)'
    for match in re.finditer(titled_pattern, text):
        full_match = match.group(0)
        names.add(full_match)
    
    # Pattern for names with speech verbs
    speech_verbs = r'(?:said|asked|replied|whispered|shouted|exclaimed|cried|yelled|murmured|declared|called|laughed|roared)'
    name_verb_pattern = rf'([A-Z][a-z]+)\s+{speech_verbs}'
    for match in re.finditer(name_verb_pattern, text):
        names.add(match.group(1))
    
    # Pattern for names after speech verbs
    verb_name_pattern = rf'{speech_verbs}\s+([A-Z][a-z]+)'
    for match in re.finditer(verb_name_pattern, text):
        names.add(match.group(1))
    
    # Pattern for "the [role]" references
    role_pattern = r'the\s+(dragon|knight|wizard|witch|fairy|giant|queen|king|prince|princess|troll|ogre|dwarf|elf)'
    for match in re.finditer(role_pattern, text, re.IGNORECASE):
        names.add(f"the {match.group(1).lower()}")
    
    # Filter out common words that might be false positives
    common_words = {'the', 'and', 'but', 'for', 'not', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out'}
    names = {n for n in names if n.lower() not in common_words}
    
    return list(names)


def clear_cache() -> None:
    """Clear the character analysis cache"""
    global _character_cache
    _character_cache = {}


def is_llm_available() -> bool:
    """Check if LLM-based gender detection is available"""
    if not OPENAI_AVAILABLE:
        return False
    
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    return bool(endpoint and api_key)
