def get_second_of_day(t):
    """
    Converts a seconds since epoch timestamp to the number of seconds,
    that have elapsed on the current day of the timestamp.

    For example the timestamp 1619891033 represents Saturday, May 1, 2021 5:43:53 PM.
    This would be converted to 63833 since at this day, this number of seconds 
    have already elapsed of the 86400 seconds which one day has.
    """
    return t % (24 * 3600)

def get_normalized_daytime(t):
    """
    Converts a seconds since epoch timestamp to a normalized value,
    which represents the 'progress' the current day of the timestamp.
    
    For example the timestamp 1619891033 represents Saturday, May 1, 2021 5:43:53 PM.
    This would be converted to 0.7388078703703703 since the day is roughly 73% over.
    """
    return get_second_of_day(t) / 86400