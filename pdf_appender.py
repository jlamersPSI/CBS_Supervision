import pdfkit
import os
import glob
import bs4
import re

from urllib.request import urlopen
from PyPDF2 import PdfMerger

# Function to edit the HTML file
def edit_html(string, new_text, id_to_find):
    """Edits the HTML file at the specified path, replacing the content of the element with ID 'chwname'."""

    # Check if the string matches the file name pattern
    if string.endswith('.html'):
        # Open the HTML file
        with open(string, 'r') as f:
            soup = bs4.BeautifulSoup(f, 'html.parser')
    else:
        soup = bs4.BeautifulSoup(string, 'html.parser')


    # Find the element with ID 'chwname'
    chwname_element = soup.find('div', id=id_to_find)

    # If the element is found, replace its content
    if chwname_element:
        chwname_element.string = f"{chwname_element.string} {new_text}"
    else:
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
        html = edit_html(
            './Form_Templates/CHW_PAGE_TEMPLATE.html',
            row['CHW Name/Code'],
            'Name_of_CHW'
        )
        html = edit_html(
            html,
            row['CHW'],
            'CHW_ID'
        )

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
