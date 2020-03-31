"""
Utility module for parsing args.
"""


def process_arg(val):
    """
    Convert a string into the correct value.
    e.g. "2" -> 2 (int)
         "false" -> False (bool)
         "1.8" -> 1.8 (float)
         "1.2, false" -> [1.2, False] (list)

    Args:
        val (string): The value to convert.

    Returns:
        (bool, int, float, string): The converted value.
    """
    if ',' in val:
        return [process_arg(v) for v in val.split(',')]

    val = val.strip()
    if val.lower() == 'true':
        return True
    if val.lower() == 'false':
        return False

    try:
        val = int(val)
        return val
    except ValueError:
        pass

    try:
        val = float(val)
        return val
    except ValueError:
        pass

    return val
