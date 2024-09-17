# Import necessary modules
import json  # JSON library to handle data storage

def fetch_and_save_org_units(api):
    """
    Fetches organization units from the DHIS2 API and saves them to a JSON file.

    Args:
        api (obj): An API object used to make the necessary GET requests.

    - Retrieves the username and password using `get_credentials()`.
    - Initializes the DHIS2 API connection.
    - Fetches all organization units with pagination.
    - Saves the data to 'org_units.json' in JSON format.
    """

    # Fetch all organization units with pagination and merge them into a single response
    org_units = api.get_paged('organisationUnits', page_size=100, merge=True)

    # Save the fetched organization units to a JSON file
    with open('Data/org_units.json', 'w', encoding='utf-8') as f:
        json.dump(org_units, f, ensure_ascii=False, indent=4)

# Example usage (uncomment the line below to use):
# fetch_and_save_org_units()
