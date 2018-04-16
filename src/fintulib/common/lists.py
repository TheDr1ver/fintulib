def flatten_list(li):
    """Flatten a list by one level.
    :param li: a lists of lists
    """
    return [item for sublist in li for item in sublist]
