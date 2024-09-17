import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from dhis2 import Api
from get_credentials import get_credentials
from in_dictlist import in_dictlist, find_index_by_value
from get_CBS_data import merge_CBS_HF04_org_hierarchy
from io import StringIO

#@TODO add check for the time since the data downloaded last should be less than 7 days

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the given credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

if not os.path.exists('./Data/combined_CBS_data.csv'):
    merge_CBS_HF04_org_hierarchy(api)

#@TODO add check this json
# Open and read the JSON file
with open('Data/org_units.json', 'r') as file:
    data = json.load(file)

CBS_data = pd.read_csv('./Data/combined_CBS_data.csv')

# Ask the user to type in a CHC name
chc_name = input("Please enter the name of the Community Health Center (CHC): ")

# Store the result
print(f"CHC name '{chc_name}' has been stored.")

ID_for_chc = data["organisationUnits"][find_index_by_value(data["organisationUnits"],"displayName",chc_name)]["id"]

period = 'LAST_12_MONTHS'  # Define the time period as the last month
data_element = 'nufVxEfy3Ps.REPORTING_RATE'

# Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
query_string = (
    f'analytics.csv?dimension=pe:{period}'             # Add period dimension
    f'&dimension=dx:{data_element}'       # Add data element group dimension
    f'&dimension=ou:{ID_for_chc};'                        # Add organizational unit dimension
)

# Step 5: Fetch the data from DHIS2 API using the constructed query string
response = api.get(query_string)

# Step 6: Load the API response into a pandas DataFrame
# The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
df = pd.read_csv(StringIO(response.text))

columns_to_add = [
    'CHW',
    'nufVxEfy3Ps.REPORTING_RATE',
    'nufVxEfy3Ps.REPORTING_RATE_ON_TIME',
    'nufVxEfy3Ps.ACTUAL_REPORTS',
    'nufVxEfy3Ps.ACTUAL_REPORTS_ON_TIME',
    'nufVxEfy3Ps.EXPECTED_REPORTS'
]

# Filter rows where 'clinic' contains chc_name (case-insensitive)
filtered_df = CBS_data[CBS_data['Clinic'].str.contains(chc_name, case=False, na=False)][columns_to_add]

# Add a new column with random integers from 0 to 10
filtered_df['Data Quality Score'] = np.random.randint(0, 11, size=len(filtered_df))

# Sort the DataFrame by the 'Random_Int' column
filtered_df = filtered_df.sort_values(by='Data Quality Score',ascending=False)

filtered_df['CHW'] = filtered_df['CHW'].str.split(' - ').str[-1]
filtered_df.columns = filtered_df.columns.str.split('.').str[-1]
filtered_df.columns = filtered_df.columns.str.replace('_', '\n')

text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque congue non nisi sed pellentesque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce luctus lacus sed lorem tempor blandit. Cras placerat ipsum non libero consectetur sodales. Vestibulum mollis porta sapien in maximus. Nunc id sem ut justo imperdiet tempus quis ac urna. Integer pretium lorem turpis, eget sodales mi placerat vel. Aliquam ultricies ultricies tellus at tincidunt. Sed pharetra scelerisque risus sit amet pharetra. Ut urna velit, molestie id tellus a, pretium venenatis eros. Vestibulum aliquam, elit sit amet porta imperdiet, nulla nibh bibendum lectus, et luctus quam lacus mollis lectus. Ut luctus ac odio sed sagittis. Proin eros dui, euismod a faucibus in, egestas feugiat tortor. Nunc laoreet justo nunc, vel convallis libero tristique nec. Duis rutrum pulvinar ultrices.
"""

# Open PdfPages
with PdfPages('Output_test.pdf') as pdf:
    # Create a matplotlib figure with a 2x2 grid (2 plots on top, 1 table on bottom)
    fig, axs = plt.subplots(2, 2, figsize=(8.27, 11.69), gridspec_kw={'height_ratios': [0.5, 1]})

    fig.suptitle(f'CBS Report {chc_name}', fontsize=20)

    # Plot 1 (top-left)
    #axs[0, 0].plot([1, 2, 3], [4, 5, 6])  # Example plot (replace with your actual plot)
    #axs[0, 0].set_title('Plot 1')

    df.index = [datetime.strptime(str(value), '%Y%m') for value in df["Period"]]

    df = df.sort_index()

    print(df.head())

    df["Value"].plot(ax=axs[0, 0])

    # Plot 2 (top-right)
    #axs[0, 1].plot([1, 2, 3], [6, 5, 4])  # Example plot (replace with your actual plot)
    #axs[0, 1].set_title('Plot 2')

    axs[0, 1].axis('off')
    axs[1, 0].axis('off')
    axs[1, 1].axis('off')

    axs[0, 1].text(0,0,text, wrap=True)

    # Create a table spanning both columns in the bottom row
    table_ax = fig.add_subplot(2, 1, 2)  # Create a new subplot for the table
    table_ax.axis('off')  # Hide axes for the table


    # Create the table spanning both columns at the bottom
    table = table_ax.table(cellText=filtered_df.values, colLabels=filtered_df.columns, loc='center', cellLoc='center')
    cellDict = table.get_celld()
    for i in range(0, len(filtered_df.columns)):
        cellDict[(0, i)].set_height(.3)
        for j in range(1, len(filtered_df.values) + 1):
            cellDict[(j, i)].set_height(.1)


    for j in range(0, len(filtered_df["Data Quality Score"])):
        cell_j = j + 1

        if filtered_df.iloc[j]["Data Quality Score"] < 4:
            cellDict[(cell_j, len(filtered_df.columns) - 1)].set_facecolor("#ff4d4d")
        elif 8 > filtered_df.iloc[j]["Data Quality Score"] > 3:
            cellDict[(cell_j, len(filtered_df.columns) - 1)].set_facecolor("#ffff4d")
        elif filtered_df.iloc[j]["Data Quality Score"] > 7:
            cellDict[(cell_j, len(filtered_df.columns) - 1)].set_facecolor("#4dff4d")


    # Adjust font size and scale
    table.auto_set_column_width(col=list(range(len(filtered_df.columns))))
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Increase the font size
    table.scale(1, 1)  # Increase the scale for a bigger table

    # Save to PDF
    pdf.savefig(fig)

# Confirm the file has been saved
print(f"PDF file created and saved as Output_test.pdf")

