# Import necessary modules
from io import StringIO  # To handle string buffers
from tqdm import tqdm  # For progress bars
import json  # To parse and load JSON data
import os  # To check if files exist
import pandas as pd  # For data manipulation

# Import the function from another script to fetch and save organizational units
from get_org_unit_json import fetch_and_save_org_units
from in_dictlist import in_dictlist
# from get_data import get_credentials  # Uncomment if credentials fetching is needed

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
    # Check if 'org_units.json' exists
    if not os.path.exists('Data/org_units.json'):
        print("org_units.json not found, calling fetch_and_save_org_units...")
        fetch_and_save_org_units(api)  # Fetch and save organization units if the file doesn't exist

    # Load organization units from a JSON file
    with open('Data/org_units.json') as f:
        org_units = json.load(f)

    # Retrieve data for the given organization unit UID via API call
    r = api.get(f'organisationUnitProfile/{UID}/data?')
    data = json.load(StringIO(r.text))  # Parse the API response JSON

    # Recursively build the organizational hierarchy
    if data['info']["level"] > 1:  # If not at the top level
        result = in_dictlist('displayName', data['info']['parentName'], org_units["organisationUnits"])
        ar = get_org_heir(result['id'], api)  # Recursive call for the parent organization
        ar.append(data['info']["name"])  # Append the current organization unit to the hierarchy
        return ar
    else:
        return [data['info']["name"]]  # If at the top level, return the organization name in a list

# Function to retrieve and map the organizational hierarchy for Community Health Workers (CHWs)
def get_all_org_hier_chw(api):
    """
    Retrieves and organizes the hierarchical levels for Community Health Workers (CHWs) using the DHIS2 API.

    Args:
        api (obj): The API object used to interact with the DHIS2 system.
    """
    # Define the hierarchical levels of interest
    org_lvl = [
        "National",
        "District",
        "Council",
        "Chiefdom",
        "Clinic",
        'CHW'
    ]

    # Set query parameters for fetching data
    period = 'LAST_MONTH'  # Specify the time period as the last month
    org = 'LEVEL-6'  # Define the organizational unit level (e.g., level-6 in the hierarchy)
    data_element = 'nufVxEfy3Ps.EXPECTED_REPORTS'  # Define the data element for reports

    # Construct the query string for the DHIS2 analytics API
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Time period dimension
        f'&dimension=dx:{data_element}'  # Data element group dimension
        f'&dimension=ou:{org};'  # Organizational unit dimension
    )

    # Fetch data from DHIS2 API
    response = api.get(query_string)

    # Load the response data into a pandas DataFrame (assumes CSV format)
    df = pd.read_csv(StringIO(response.text))
    print(df.head())  # Display the first few rows of the DataFrame

    # Initialize columns for each level in the hierarchy
    for i in tqdm(org_lvl):
        df[i] = ' '  # Set default values as empty strings
        df[i] = df[i].astype(object)  # Ensure the column type is object

    # Map each organization unit to its hierarchy
    for index, row in tqdm(df.iterrows()):
        org_heir = get_org_heir(row["Organisation unit"], api)  # Retrieve the hierarchy for the unit
        for i, col in enumerate(org_lvl):
            df.loc[index, col] = org_heir[i]  # Assign the hierarchy levels to the respective columns

    # Save the resulting DataFrame to a JSON file
    df.to_csv('./Data/org_hierarchy.csv')

# Example usage (commented out for now):
# username, password = get_credentials()  # Fetch credentials if needed
# api = Api('https://sl.dhis2.org/hmis23', username, password)  # Initialize API connection
# result = get_org_heir('ObzxZzrPSoN', api)  # Call the function with a sample UID
# print(result)  # Print the result
