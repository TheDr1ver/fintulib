def flatten_list(li):
    """flatten a list by one level"""
    return [item for sublist in li for item in sublist]
