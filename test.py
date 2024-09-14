"""
from dhis2 import Api
from get_data import get_credentials
from io import StringIO
from tqdm import tqdm
from get_org_hier import get_org_heir

import pandas as pd
import json
import re
import os

PATH_TO_DATA_CSV = 'test.csv'

# If file doesn't exist, call get_org_unit_heir to create it
username, password = get_credentials()

# Initialize the API connection
api = Api('https://sl.dhis2.org/hmis23', username, password)

# Check if org_units.json exists
if not os.path.exists(PATH_TO_DATA_CSV):
    org_lvl = [
        "National",
        "District",
        "Council",
        "Chiefdom",
        "Clinic",
        'CHW'
    ]

    period='LAST_12_MONTHS'
    data_element='AnufVxEfy3Ps.ACTUAL_REPORTS%3BnufVxEfy3Ps.EXPECTED_REPORTS'
    org='LEVEL-6'

    s = f'analytics.csv?dimension=pe:{period}&dimension=dx:{data_element}&dimension=ou:{org};'

    r = api.get(s)
    df = pd.read_csv(StringIO(r.text))

    for i in org_lvl:
        df[i] = ' '
        df[i] = df[i].astype(object)  # Ensure dtype is object

        df.to_csv('test.csv', index=False)

# Load the DataFrame, ensuring that the org_lvl columns are read as object type
df = pd.read_csv(
    'test.csv',
    dtype={col: 'object' for col in ["National", "District", "Council", "Chiefdom", "Clinic", 'CHW']}
)

for index, row in tqdm(df.iterrows()):
    org_heir = get_org_heir(df.iloc[index]["Organisation unit"],api)

    temp = list(df.columns)

    for i in range(temp.index("National"),temp.index("National") + 6):
        df.loc[index,df.columns[i]] = org_heir[i - temp.index("National")]

    if index > 100:
        break

print(df.head())

df.to_csv('result.csv')
"""
