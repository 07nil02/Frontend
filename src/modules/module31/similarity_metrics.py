import numpy as np

def euclidean_distance(vec1, vec2):
    """
    Calculates the Euclidean distance between two vectors.
    Assumes vectors are numpy arrays.
    """
    return np.linalg.norm(vec1 - vec2)

def jaccard_similarity(set1, set2):
    """
    Calculates the Jaccard similarity between two sets.
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def exact_or_fuzzy_match(str1, str2, method='exact'):
    """
    Performs an exact or fuzzy match on two strings.
    'exact': returns 1 if strings are identical, 0 otherwise.
    'fuzzy': can be extended with methods like Soundex, Levenshtein, etc.
    """
    if method == 'exact':
        return 1 if str1.lower() == str2.lower() else 0
    elif method == 'fuzzy':
        # Placeholder for a more advanced fuzzy matching, e.g., using a library
        # For now, using a simple substring check as a basic fuzzy match
        return 1 if str1.lower() in str2.lower() or str2.lower() in str1.lower() else 0
    return 0

