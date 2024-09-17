# Helper function to search for a dictionary entry in a list based on a key-value pair
def in_dictlist(key, value, my_dictlist):
    """
    Searches for an entry in a list of dictionaries where the specified key has a given value.

    Args:
        key (str): The dictionary key to match.
        value (str): The value to look for corresponding to the key.
        my_dictlist (list): A list of dictionaries to search through.

    Returns:
        dict: The dictionary entry that matches the key-value pair, or an empty dictionary if not found.
    """
    for entry in my_dictlist:
        if entry[key] == value:  # Check if the current entry matches the key-value pair
            return entry
    return {}  # Return an empty dictionary if no match is found

def find_index_by_value(data, key, value):
  """Finds the index of a dictionary in a list where a specified key matches a given value.

  Args:
    data: A list of dictionaries.
    key: The key to search for in the dictionaries.
    value: The value to match for the specified key.

  Returns:
    The index of the first dictionary where the key matches the value, or -1 if no match is found.
  """

  for i, d in enumerate(data):
    if d.get(key) == value:
      return i
  return -1