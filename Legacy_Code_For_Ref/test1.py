from dhis2 import Api
from get_credentials import get_credentials
from io import StringIO
from get_org_hier import get_org_heir
from tqdm import tqdm

import pandas as pd

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the given credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

HF04_IDs = [
    'nufVxEfy3Ps.REPORTING_RATE',
    'nufVxEfy3Ps.REPORTING_RATE_ON_TIME',
    'nufVxEfy3Ps.ACTUAL_REPORTS',
    'nufVxEfy3Ps.ACTUAL_REPORTS_ON_TIME',
    'nufVxEfy3Ps.EXPECTED_REPORTS'
]

org_lvl = [
        "National",
        "District",
        "Council",
        "Chiefdom",
        "Clinic",
        'CHW'
]

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
df = pd.read_csv(StringIO(response.text))

print(df.head())

for i in tqdm(org_lvl):
    df[i] = ' '
    df[i] = df[i].astype(object)  # Ensure dtype is object

for index, row in tqdm(df.iterrows()):
    org_heir = get_org_heir(
        row["Organisation unit"],
        api
    )

    for i, col in enumerate(org_lvl):
        df.loc[index,col] = org_heir[i]

for data_element_ID in tqdm(HF04_IDs):
    print(data_element_ID)

    period = 'LAST_MONTH'  # Define the time period as the last month
    org = 'LEVEL-6'  # Specify organizational unit level (e.g., level-6 in the hierarchy)

    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Add period dimension
        f'&dimension=dx:{data_element_ID}'  # Add data element group dimension
        f'&dimension=ou:{org};'  # Add organizational unit dimension
    )

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    response = api.get(query_string)

    # Step 6: Load the API response into a pandas DataFrame
    # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
    df_stinky = pd.read_csv(StringIO(response.text))

    # Merge df1 and df2 based on the 'Period' column
    merged_df = pd.merge(df, df_stinky[['Organisation unit', 'Value']], on='Organisation unit', how='left', suffixes=('_df1', '_df2'))

    print(merged_df.columns)

    # Add the values from df2 to the values in df1
    merged_df[f'{data_element_ID}'] = merged_df['Value_df2']

    # Drop the temporary 'Value_df2' column and rename 'Value_df1' back to 'Value'
    merged_df = merged_df.drop(columns=['Value_df2'])
    merged_df = merged_df.rename(columns={'Value_df1': 'Value'})

    df = merged_df

df.to_csv('res.csv')
