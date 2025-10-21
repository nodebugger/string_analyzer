# String utility functions

import hashlib
from collections import Counter
import re

def analyze_string(value: str):
    length = len(value)
    is_palindrome = value.lower() == value[::-1].lower()
    unique_characters = len(set(value))
    word_count = len(value.split())
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    character_frequency_map = dict(Counter(value))
    
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map
    }

def parse_natural_query(query: str) -> dict:
    filters = {}
    query_lower = query.lower()
    
    # Word count patterns
    if "single word" in query_lower or "one word" in query_lower:
        filters["word_count"] = 1
    
    # Palindrome patterns
    if "palindromic" in query_lower or "palindrome" in query_lower:
        filters["is_palindrome"] = True
    
    # Length patterns
    if "longer than" in query_lower:
        match = re.search(r'longer than (\d+) characters?', query_lower)
        if match:
            filters["min_length"] = int(match.group(1)) + 1
    
    # Character containment patterns
    if "containing the letter" in query_lower or "strings containing the letter" in query_lower:
        match = re.search(r'containing the letter (\w)', query_lower)
        if match:
            filters["contains_character"] = match.group(1)
    
    # Handle "first vowel" pattern
    if "first vowel" in query_lower or "contain the first vowel" in query_lower:
        filters["contains_character"] = "a"
    
    # Handle specific vowel mentions
    if "contain a" in query_lower or "contains a" in query_lower:
        filters["contains_character"] = "a"
    if "contain e" in query_lower or "contains e" in query_lower:
        filters["contains_character"] = "e"
    if "contain i" in query_lower or "contains i" in query_lower:
        filters["contains_character"] = "i"
    if "contain o" in query_lower or "contains o" in query_lower:
        filters["contains_character"] = "o"
    if "contain u" in query_lower or "contains u" in query_lower:
        filters["contains_character"] = "u"
    
    return filters
