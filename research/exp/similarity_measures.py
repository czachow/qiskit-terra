import math

def hellinger_distance(p, q):
    """Hellinger distance between two discrete distributions."""
    if len(p) != len(q):
        raise ValueError("Arrays have different length")
    
    N = len(p)
    list_of_squares = [0] * N
    for i, (p_i, q_i) in enumerate(zip(p, q)):
        # caluclate the square of the difference of ith distr elements
        list_of_squares[i] = (math.sqrt(p_i) - math.sqrt(q_i)) ** 2

    # calculate sum of squares
    sosq = sum(list_of_squares)

    return math.sqrt(sosq / 2)


def total_variational_distance(p, q):
    """total variation distance"""
    if len(p) != len(q):
        raise ValueError("Arrays have different length")
    N = len(p)
    list_of_diffs = [0] * N
    for i, (p_i, q_i) in enumerate(zip(p, q)):
        list_of_diffs[i] = abs(p_i - q_i)
    return sum(list_of_diffs) / 2
