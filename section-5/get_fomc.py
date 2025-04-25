import requests
from bs4 import BeautifulSoup
import re

# Base URL for constructing complete links
base_url = "https://www.federalreserve.gov"

# URL of the historical FOMC page for 2018 meetings
url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2018.htm"

# Send an HTTP GET request to the page
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Locate all meeting panels by finding <h5> elements with the specific class.
panels = soup.find_all("h5", class_="panel-heading panel-heading--shaded")

if not panels:
    raise Exception("No meeting panels found on the page.")

for panel in panels:
    # Get the text from the panel heading, e.g., "Jul/Aug Meeting - 2018" or "March 20-21 Meeting - 2018"
    meeting_text = panel.get_text(strip=True)
    print(f"Processing meeting: {meeting_text}")

    # Extract the first segment (assumed to be the month or months).
    # For example, for "Jul/Aug Meeting - 2018", it takes "Jul/Aug" and then splits by '/' to keep only "Jul"
    raw_month = meeting_text.split()[0]
    # If the month is expressed with a slash, use only the first part.
    first_month = raw_month.split("/")[0]
    # Sanitize the extracted month to remove any characters not allowed in filenames.
    month = re.sub(r'[\\/:"*?<>|]+', '', first_month)

    # The related links are in a sibling <div> with class "row divided-row".
    container_div = panel.find_next_sibling("div", class_="row divided-row")
    if not container_div:
        print(f"No meeting details container found for: {meeting_text}")
        continue

    # Find the anchor with a href that contains "tealbooka" (case insensitive).
    tealbook_a_link = container_div.find("a", href=lambda href: href and "tealbooka" in href.lower())
    if not tealbook_a_link:
        print(f"No Tealbook A link found for: {meeting_text}")
        continue

    # Build the complete URL for the PDF.
    pdf_relative_url = tealbook_a_link['href']
    pdf_url = base_url + pdf_relative_url

    print(f"Downloading Tealbook A from: {pdf_url}")

    # Download the PDF file
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code == 200:
        # Save the file as "MONTH_TBA.pdf" (e.g., "Jul_TBA.pdf" or "March_TBA.pdf")
        filename = f"{month}_TBA.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_response.content)
        print(f"Saved PDF as {filename}")
    else:
        print(f"Failed to download PDF from {pdf_url} (Status code: {pdf_response.status_code})")
