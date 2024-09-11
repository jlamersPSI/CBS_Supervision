import json
from dhis2 import Api
from get_data import get_credentials
from io import StringIO
from tqdm import tqdm

import pandas as pd
import json

def in_dictlist(key, value, my_dictlist):
    for entry in tqdm(my_dictlist):
        if entry[key] == value:
            return entry
    return {}

def get_org_heir(
        UID,
        api
):
    #data_hier = [None] * 6

    with open('org_units.json') as f:
        org_units = json.load(f)

    r = api.get(f'organisationUnitProfile/{UID}/data?')
    data = json.load(StringIO(r.text))

    #data_hier[data['info']["level"] - 1] = data['info']["name"]

    if data['info']["level"] > 1:
        result = in_dictlist('displayName', data['info']['parentName'], org_units["organisationUnits"])

        ar = get_org_heir(result['id'],api)

        ar.append(data['info']["name"])

        return ar
    else:
        return [ data['info']["name"] ]

username, password = get_credentials()

# Initialize the API connection
api = Api('https://sl.dhis2.org/hmis23', username, password)

result = get_org_heir(
        'dfaHk9YiXVe',
        api
    )

print(result)
