import pdfkit
import os
import glob
import bs4
import re

from urllib.request import urlopen
from PyPDF2 import PdfMerger

def insert_indicators(
        row
):
    html = edit_html(
        './Form_Templates/CHW_PAGE_TEMPLATE.html',
        row['CHW Name/Code'],
        'Name_of_CHW',
        'div'
    )
    html = edit_html(
        html,
        row['CHW'],
        'CHW_ID',
        'div'
    )
    html = edit_html(
        html,
        row["Fever case (suspected malaria) in HTR and ETR referred"],
        "Fever_case_(suspected_malaria)_in_HTR_amp;_ETR_Referred",
        'td'
    )
    html = edit_html(
        html,
        row["Fever case tested for Malaria (RDT) in HTR - Positive referred"],
        "Fever_case_tested_for_malaria_(RDT)_in_HTR_Positive_Referred",
        'td'
    )
    html = edit_html(
        html,
        row["Fever case tested for Malaria (RDT) in HTR - Negative referred"],
        "Fever_case_tested_for_malaria_(RDT)_in_HTR_Negative_Referred",
        'td'
    )
    html = edit_html(
        html,
        row["Malaria treated with ACT in HTR referred"],
        "Malaria_treated_with_ACT_in_HTR_referred",
        'td'
    )

    return html

# Function to edit the HTML file
def edit_html(string, new_text, id_to_find, element_type):
    """Edits the HTML file at the specified path, replacing the content of the element with ID 'chwname'."""

    # Check if the string matches the file name pattern
    if string.endswith('.html'):
        # Open the HTML file
        with open(string, 'r') as f:
            soup = bs4.BeautifulSoup(f, 'html.parser')
    else:
        soup = bs4.BeautifulSoup(string, 'html.parser')


    # Find the element with ID 'chwname'
    chwname_element = soup.find(element_type, id=id_to_find)

    if chwname_element:
        if chwname_element.string is None:
            chwname_element.string = ''

        chwname_element.string = f"{chwname_element.string} {new_text}"
    else:
        print(str(soup))
        print(f"Element with ID {id_to_find} not found.")

    # Return the edited HTML as a string
    return str(soup)

def gen_pdf(
        data,
        chc_name
):
    path_to_wkhtmltopdf = r'C:\Users\JLamers.sl\PycharmProjects\CBS_Supervision\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    for index, row in data.iterrows():
        html = insert_indicators(
            row
        )

        #print(html)

        pdfkit.from_string(
            html,
            f'./Output/{row['CHW']}.pdf',
            configuration=config
        )

    merger = PdfMerger()

    for pdf in glob.glob("./Output/*.pdf"):
        merger.append(pdf)

    merger.write(f"./Output/{chc_name}_report.pdf")
    merger.close()
