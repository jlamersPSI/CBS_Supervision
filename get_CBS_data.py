from logging import exception

from dhis2 import Api
from get_credentials import get_credentials
from io import StringIO
from tqdm import tqdm

import pandas as pd
import json

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the given credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

CBS_DATA_UID = {
    "name": "HF04 - Community Based Services",
    "id": "j3ghXQXN65o"
}

# Get all dataElement Id's in the group

query_string = f'dataElementGroups/{CBS_DATA_UID["id"]}?fields=dataElements[]'

# Step 5: Fetch the data from DHIS2 API using the constructed query string
response = api.get(query_string)

# Step 6: Load the API response into a pandas DataFrame
# The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
dataElements = json.load(StringIO(response.text))

period = 'LAST_MONTH'  # Define the time period as the last month
org = 'LEVEL-6'  # Specify organizational unit level (e.g., level-6 in the hierarchy)
data_element = 'nufVxEfy3Ps.EXPECTED_REPORTS'

# Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
query_string = (
    f'analytics.csv?dimension=pe:{period}'             # Add period dimension
    f'&dimension=dx:{data_element}'       # Add data element group dimension
    f'&dimension=ou:{org};'                        # Add organizational unit dimension
)

# Step 5: Fetch the data from DHIS2 API using the constructed query string
response = api.get(query_string)

# Step 6: Load the API response into a pandas DataFrame
# The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
CBS_data = pd.read_csv(StringIO(response.text))
CBS_data = pd.DataFrame({"Organisation unit":CBS_data["Organisation unit"]})

for index, element in tqdm(enumerate(dataElements["dataElements"])):
    name_query_string = f'dataElements/{element["id"]}?fields=name[]'

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    response = api.get(name_query_string)

    name = json.load(StringIO(response.text))["name"]

    period = 'LAST_MONTH'  # Define the time period as the last month
    org = 'LEVEL-6'  # Specify organizational unit level (e.g., level-6 in the hierarchy)

    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Add period dimension
        f'&dimension=dx:{element["id"]}'  # Add data element group dimension
        f'&dimension=ou:{org};'  # Add organizational unit dimension
    )

    try:
        # Step 5: Fetch the data from DHIS2 API using the constructed query string
        response = api.get(query_string)

        indicator_data = pd.read_csv(StringIO(response.text))

        CBS_data = pd.merge(CBS_data, indicator_data[['Organisation unit', 'Value']], on='Organisation unit',
                            how='left')
        CBS_data.rename(columns={"Value": name}, inplace=True)

        print(CBS_data.columns)
    except Exception as e:
        print(e)

CBS_data.to_csv('CBS_data.csv')

print(CBS_data.head())