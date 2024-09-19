# Import required libraries
import pdfkit
import os
import glob
import bs4
import re
from urllib.request import urlopen
from PyPDF2 import PdfMerger
from datetime import datetime
from io import StringIO
import pandas as pd

def get_backlog_data(
        api,
        chw_code
):
    period = 'LAST_12_MONTHS'  # Define the time period as the last month

    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Add period dimension
        f'&dimension=dx:nufVxEfy3Ps.ACTUAL_REPORTS'  # Add data element group dimension
        f'&dimension=ou:{chw_code};'  # Add organizational unit dimension
    )

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    response = api.get(query_string)

    # Step 6: Load the API response into a pandas DataFrame
    # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
    df = pd.read_csv(StringIO(response.text))

    df.index = [datetime.strptime(str(value), '%Y%m') for value in df["Period"]]

    df = df.sort_index()

    df = df["Value"]

    return df

def insert_backlog_table(
        api,
        chw_code,
        html
):
    backlog_data = get_backlog_data(api,chw_code)

    backlog_table = '''
    <table class="chw-info-table">
        <th colspan="12">CBS Data Backlog</th>
        <tr id = "row 1">
        </tr>
        <tr id = "row 2">
        </tr>
    </table>
    '''

    backlog_table = backlog_table.replace(
        f'<tr id = "row 1">',
        f'<tr id="row 1">' + ''.join(f'\n\t\t<td>{value.strftime('%B %Y')}</td>' for value in backlog_data.index)
    )

    for value in backlog_data:
        if value == 0:
            backlog_table = backlog_table.replace(
                f'<tr id = "row 2">',
                f'<tr id = "row 2">' + ''.join(f'\n\t\t<td style="background-color: red;">{value}</td>')
            )
        elif value == 1:
            backlog_table = backlog_table.replace(
                f'<tr id = "row 2">',
                f'<tr id = "row 2">' + ''.join(f'\n\t\t<td style="background-color: green;">{value}</td>')
            )
        else:
            print(f'Value should be 1 or 0 but was {value}')

    soup = bs4.BeautifulSoup(html, 'html.parser')

    # Find the last table element
    last_table = soup.find_all('table')[-1]

    # Create a new BeautifulSoup object for the backlog table
    new_table_soup = bs4.BeautifulSoup(backlog_table, 'html.parser')

    # Insert the new table before the last table
    last_table.insert_before(new_table_soup)

    return str(soup)

def insert_indicators(row):
    """
    Insert indicator values into the HTML template for a given row of data.

    Args:
        row (dict): A dictionary containing CHW data and indicators.

    Returns:
        str: The modified HTML content as a string.
    """
    html = edit_html('./Form_Templates/CHW_PAGE_TEMPLATE.html', row['CHW Name/Code'], 'Name_of_CHW', 'div')
    html = edit_html(html, row['CHW'], 'CHW_ID', 'div')

    # Insert various indicator values
    indicators = [
        ("Fever_case_(suspected_malaria)_in_HTR_amp;_ETR_Referred",
         "Fever case (suspected malaria) in HTR and ETR referred"),
        ("Fever_case_tested_for_malaria_(RDT)_in_HTR_Positive_Referred",
         "Fever case tested for Malaria (RDT) in HTR - Positive referred"),
        ("Fever_case_tested_for_malaria_(RDT)_in_HTR_Negative_Referred",
         "Fever case tested for Malaria (RDT) in HTR - Negative referred"),
        ("Malaria_treated_with_ACT_in_HTR_referred", "Malaria treated with ACT in HTR referred")
    ]

    for id_to_find, key in indicators:
        html = edit_html(html, row[key], id_to_find, 'td')

    return html


def edit_html(string, new_text, id_to_find, element_type):
    """
    Edit HTML content by replacing or appending text in a specific element.

    Args:
        string (str): HTML content or file path.
        new_text (str): Text to be inserted or appended.
        id_to_find (str): ID of the element to be modified.
        element_type (str): Type of HTML element (e.g., 'div', 'td').

    Returns:
        str: Modified HTML content as a string.
    """
    # Determine if input is a file path or HTML string
    if string.endswith('.html'):
        with open(string, 'r') as f:
            soup = bs4.BeautifulSoup(f, 'html.parser')
    else:
        soup = bs4.BeautifulSoup(string, 'html.parser')

    # Find the element and modify its content
    target_element = soup.find(element_type, id=id_to_find)
    if target_element:
        if target_element.string is None:
            target_element.string = ''
        target_element.string = f"{target_element.string} {new_text}"
    else:
        print(str(soup))
        print(f"Element with ID {id_to_find} not found.")

    return str(soup)


def gen_pdf(api, data, chc_name):
    """
    Generate individual PDFs for each CHW and merge them into a single report.

    Args:
        data (pandas.DataFrame): DataFrame containing CHW data.
        chc_name (str): Name of the Community Health Center for the report title.
    """
    # Set path to wkhtmltopdf executable
    path_to_wkhtmltopdf = r'C:\Users\JLamers.sl\PycharmProjects\CBS_Supervision\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Generate individual PDFs for each CHW
    for index, row in data.iterrows():
        html = insert_indicators(row)
        html = insert_backlog_table(api, row["Organisation unit"],html)
        pdfkit.from_string(html, f'./Output/{row["CHW"]}.pdf', configuration=config)

    # Merge individual PDFs into a single report
    merger = PdfMerger()
    for pdf in glob.glob("./Output/*.pdf"):
        merger.append(pdf)

    merger.write(f"./Output/{chc_name}_report.pdf")
    merger.close()