import pandas as pd

from io import StringIO
from get_credentials import get_credentials
from dhis2 import Api

def get_validation(
        api
):
    test = "?ou=Plmg8ikyfrK&pe=2024&notificationSent=true"
    str = f"""/validationResults.json{test};"""

    pages = api.get_paged(str, page_size=100, merge=True)

    print(pages)

    #period = 'LAST_MONTH'  # Define the time period as the last month
    #org = 'LEVEL-6'  # Specify organizational unit level (e.g., level-6 in the hierarchy)
    #data_element = 'nufVxEfy3Ps.EXPECTED_REPORTS'

    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    #query_string = (
    #    f'analytics.csv?dimension=pe:{period}'  # Add period dimension
    #    f'&dimension=dx:{data_element}'  # Add data element group dimension
    #    f'&dimension=ou:{org};'  # Add organizational unit dimension
    #)

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    #response = api.get(query_string)

    # Step 6: Load the API response into a pandas DataFrame
    # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
    #chw_codes = pd.read_csv(StringIO(response.text))
    #chw_codes = chw_codes["Organisation unit"]

    #return chw_codes

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the given credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

get_validation(api)