# Import necessary modules
# from dhis2 import Api  # DHIS2 API module
from io import StringIO  # Used to handle string buffers
from tqdm import tqdm  # Used to display progress bars
import json  # JSON library to parse and load data
import os  # To check file existence

# Import the function from another script
from get_org_unit_json import fetch_and_save_org_units
# from get_data import get_credentials

# Helper function to find an entry in a list of dictionaries based on a key-value pair
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
    # Iterate through the list with a progress bar
    for entry in tqdm(my_dictlist):
        if entry[key] == value:  # Return the matching dictionary
            return entry
    return {}  # Return an empty dictionary if no match is found


# Recursive function to get organizational hierarchy
def get_org_heir(UID, api):
    """
    Retrieves the organizational hierarchy for a given unit ID (UID) by making API calls.

    Args:
        UID (str): The unique ID of the organization unit.
        api (obj): An API object used to make the necessary GET requests.

    Returns:
        list: A list of organization names in the hierarchy from the top level to the current level.
    """
    # Check if org_units.json exists
    if not os.path.exists('org_units.json'):
        # If file doesn't exist, call get_org_unit_heir to create it
        print("org_units.json not found, calling get_org_unit_heir...")
        fetch_and_save_org_units(api)

    # Load organizational units from a JSON file
    with open('org_units.json') as f:
        org_units = json.load(f)

    # Make an API call to retrieve the data for the given organization unit UID
    r = api.get(f'organisationUnitProfile/{UID}/data?')
    data = json.load(StringIO(r.text))  # Parse the JSON response

    # If the organizational unit is not at the top level, keep finding its parent
    if data['info']["level"] > 1:
        # Find the parent organization unit based on the parent name
        result = in_dictlist('displayName', data['info']['parentName'], org_units["organisationUnits"])

        # Recursively get the parent's hierarchy
        ar = get_org_heir(result['id'], api)

        # Append the current organization unit's name to the hierarchy list
        ar.append(data['info']["name"])

        return ar
    else:
        # If at the top level, return the organization name in a list
        return [data['info']["name"]]


# Example usage (commented out for now):
#username, password = get_credentials()  # Assuming there’s a function to get credentials
#api = Api('https://sl.dhis2.org/hmis23', username, password)  # Initialize API connection
#result = get_org_heir('ObzxZzrPSoN', api)  # Call the function with a sample UID
#print(result)  # Print the result
