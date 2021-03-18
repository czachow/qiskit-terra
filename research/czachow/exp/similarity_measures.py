

def hellinger_distance(p, q):
    """Hellinger distance between two discrete distributions."""
    list_of_squares = []
    for p_i, q_i in zip(p, q):

        # caluclate the square of the difference of ith distr elements
        s = (math.sqrt(p_i) - math.sqrt(q_i)) ** 2

        # append
        list_of_squares.append(s)

    # calculate sum of squares
    sosq = sum(list_of_squares)

    return math.sqrt(sosq / 2)


def total_variational_distance(p, q):
    """total variation distance"""
    list_of_diffs = []
    for bit_string in p:
        p_i = p[bit_string]
        q_i = q[bit_string]
        list_of_diffs.append(abs(p_i - q_i))
    return sum(list_of_diffs) / 2
