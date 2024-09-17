from io import StringIO

from matplotlib.font_manager import json_dump
from tqdm import tqdm
import pandas as pd
import json

from get_org_hier import get_all_org_hier_chw

def get_all_chw_codes(
        api
):
    period = 'LAST_MONTH'  # Define the time period as the last month
    org = 'LEVEL-6'  # Specify organizational unit level (e.g., level-6 in the hierarchy)
    data_element = 'nufVxEfy3Ps.EXPECTED_REPORTS'

    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Add period dimension
        f'&dimension=dx:{data_element}'  # Add data element group dimension
        f'&dimension=ou:{org};'  # Add organizational unit dimension
    )

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    response = api.get(query_string)

    # Step 6: Load the API response into a pandas DataFrame
    # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
    chw_codes = pd.read_csv(StringIO(response.text))
    chw_codes = chw_codes["Organisation unit"]

    return chw_codes


def fetch_cbs_data(
        api
):
    """
    Fetch Community Based Services (CBS) data from DHIS2 API.

    This function retrieves data elements from a specific group,
    and then fetches data for each element for the last month at organization level 6.

    Args:
        api (dhis2.Api): An initialized DHIS2 API object.

    Returns:
        pandas.DataFrame: A dataframe containing the fetched CBS data.
    """

    # Constants
    CBS_DATA_UID = {
        "name": "HF04 - Community Based Services",
        "id": "j3ghXQXN65o"
    }
    PERIOD = 'LAST_MONTH'
    ORG_LEVEL = 'LEVEL-6'

    # Step 2: Get all dataElement IDs in the group
    query_string = f'dataElementGroups/{CBS_DATA_UID["id"]}?fields=dataElements[]'
    response = api.get(query_string)
    dataElements = json.loads(response.text)

    # Step 3: Fetch initial data to get organization units
    initial_data_element = 'nufVxEfy3Ps.EXPECTED_REPORTS'
    query_string = (
        f'analytics.csv?dimension=pe:{PERIOD}'
        f'&dimension=dx:{initial_data_element}'
        f'&dimension=ou:{ORG_LEVEL};'
    )
    response = api.get(query_string)
    CBS_data = pd.read_csv(StringIO(response.text))
    CBS_data = pd.DataFrame({"Organisation unit": CBS_data["Organisation unit"]})

    # Step 4: Fetch data for each data element
    for element in tqdm(dataElements["dataElements"]):
        try:
            # Get data element name
            name_query_string = f'dataElements/{element["id"]}?fields=name[]'
            response = api.get(name_query_string)
            name = json.loads(response.text)["name"]

            # Fetch data for the element
            query_string = (
                f'analytics.csv?dimension=pe:{PERIOD}'
                f'&dimension=dx:{element["id"]}'
                f'&dimension=ou:{ORG_LEVEL};'
            )
            response = api.get(query_string)
            indicator_data = pd.read_csv(StringIO(response.text))

            # Merge new data with existing dataframe
            CBS_data = pd.merge(CBS_data, indicator_data[['Organisation unit', 'Value']],
                                on='Organisation unit', how='left')
            CBS_data.rename(columns={"Value": name}, inplace=True)

        except Exception as e:
            print(f"Error fetching data for element {element['id']}: {e}")

    # Save data to CSV
    CBS_data.to_csv('./Data/CBS_data.csv', index=False)

    return CBS_data

def fetch_HF04_data(
    api
):
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

    HF04_Data = get_all_chw_codes(api)
    org_hierarchy = pd.read_csv('./Data/org_hierarchy.csv')

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
        HF04_indicator_data = pd.read_csv(StringIO(response.text))

        # Merge df1 and df2 based on the 'Period' column
        HF04_Data = pd.merge(
            HF04_Data, HF04_indicator_data[['Organisation unit', 'Value']],
            on='Organisation unit',
            how='left'
        )

        HF04_Data[f'{data_element_ID}'] = HF04_Data['Value']
        HF04_Data = HF04_Data.drop(columns=['Value'])

    HF04_Data.to_csv('./Data/HF04_data.csv')

def merge_CBS_HF04_org_hierarchy(
        api
):
    # Tests to see if Data contains the org heirarchy json file if not downloads it
    if not os.path.exists('./Data/org_hierarchy.csv'):
        get_all_org_hier_chw(api)

    if not os.path.exists('./Data/CBS_data.csv'):
        fetch_cbs_data(api)

    if not os.path.exists('./Data/HF04_data.csv'):
        fetch_HF04_data(api)

    HF04_data = pd.read_csv('./Data/HF04_data.csv')
    CBS_data = pd.read_csv('./Data/CBS_data.csv')
    org_hierarchy = pd.read_csv('./Data/org_hierarchy.csv')

    combined_CBS_data = pd.merge(
        HF04_data,
        org_hierarchy,
        on='Organisation unit',
        how='left'
    )

    combined_CBS_data = pd.merge(
        combined_CBS_data,
        CBS_data,
        on='Organisation unit',
        how='left'
    )

    combined_CBS_data.to_csv('./Data/combined_CBS_data.csv')

# Example usage
#if __name__ == "__main__":
#    result = fetch_cbs_data()
#    print(result.head())