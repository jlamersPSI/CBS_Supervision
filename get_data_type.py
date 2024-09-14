# Import necessary libraries and modules
from dhis2 import Api              # DHIS2 API library to handle requests
from get_credentials import get_credentials  # Function to retrieve credentials
from io import StringIO            # Allows us to treat strings as file-like objects
from tqdm import tqdm              # Progress bar for iterations

import pandas as pd                # Pandas for data handling (not used here but can be useful)
import json                        # To handle JSON formatted data

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the provided credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

# Step 3: Define the Community Based Services (CBS) data element group details
CBS_DATA_UID = {
    "name": "HF04 - Community Based Services",   # Name of the data element group
    "id": "j3ghXQXN65o"                          # Unique ID for the group
}

# Step 4: Construct the query string to get all data element IDs within the specified group
query_string = f'dataElementGroups/{CBS_DATA_UID["id"]}?fields=dataElements[]'

# Step 5: Fetch the data from the DHIS2 API using the constructed query string
response = api.get(query_string)

# Step 6: Load the API response (in JSON format) into a variable
# Note: The response is JSON, not CSV, so no need for StringIO. Parsing JSON directly.
dataElements = response.json()   # Correct method to parse JSON response

# Step 7: Iterate over each data element in the response to fetch its `valueType`
for index, element in tqdm(enumerate(dataElements["dataElements"])):
    # Construct the query string for each data element to get its valueType
    query_string = f'dataElements/{element["id"]}?fields=valueType[]'

    # Fetch the valueType data for the current data element
    response = api.get(query_string)

    # Parse the valueType JSON response
    valueType_json = response.json()

    # Store the valueType inside the corresponding data element in the list
    dataElements["dataElements"][index]["valueType"] = valueType_json["valueType"]

# Step 8: Print the final dataElements dictionary with valueTypes included
print(dataElements)

