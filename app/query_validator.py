
from difflib import get_close_matches
from typing import Set

def get_fuzzy_matches(word: str, vocabulary: Set[str], cutoff: float = 0.75) -> bool:
    """
    Check if a word closely matches any word in the vocabulary using fuzzy matching
    """
    return bool(get_close_matches(word, vocabulary, n=1, cutoff=cutoff))

def is_flight_related_query(query: str) -> bool:
    """
    Enhanced check for flight-related queries using fuzzy matching for typo tolerance
    """
    # Core flight-related keywords
    flight_keywords = {
        'flight', 'air', 'airline', 'airport', 'airways',
        'travel', 'trip', 'journey',
        'destination', 'dest',
        'origin', 'route', 'path', 'connection',
        'price', 'fare', 'cost', 'expensive', 'cheap',
        'direct', 'nonstop', 'connecting',
        'departure', 'arrive', 'arriving', 'departing',
        'domestic', 'international'
    }

    # Location indicators that strongly suggest a flight query
    location_indicators = {'from', 'to', 'between', 'via'}

    # Clean and tokenize the query
    query = query.lower().strip()
    query_words = query.split()

    # Check each word in the query for fuzzy matches
    for word in query_words:
        # Exact match for location indicators
        if word in location_indicators:
            return True

        # Fuzzy match for flight keywords
        if get_fuzzy_matches(word, flight_keywords):
            return True

    # Check for price indicators
    if any(char in query for char in ['₹', '$', '€']):
        return True

    return False

def is_luggage_related_query(query: str) -> bool:
    """
    Check if a query is related to luggage/baggage using fuzzy matching
    """
    # Core luggage-related keywords
    luggage_keywords = {
        'luggage', 'baggage', 'bag', 'suitcase', 'carry-on',
        'carry on', 'check-in', 'checked bag', 'hand baggage',
        'weight', 'kg', 'kilos', 'pounds', 'lbs',
        'dimensions', 'size', 'allowance', 'restriction',
        'prohibited', 'forbidden', 'allowed', 'limit',
        'overweight', 'excess', 'cabin', 'hold', 'storage',
        'pack', 'bring', 'carry', 'transport', 'stow'
    }

    # Clean and tokenize the query
    query = query.lower().strip()
    query_words = query.split()

    # Check each word in the query for fuzzy matches
    for word in query_words:
        if get_fuzzy_matches(word, luggage_keywords):
            return True

    return False