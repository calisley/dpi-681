import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the Massachusetts General Laws Title I page
base_url = 'https://malegislature.gov'
start_path = '/Laws/GeneralLaws/PartII/TitleI/'

# Directory to save the section files
output_dir = '../admin/sections_output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Range of base chapter numbers we want to crawl: 183 to 189 (inclusive)
chapter_numbers = range(183, 190)

# Headers for requests to simulate a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def get_soup(url):
    """Fetch content from the URL and return a BeautifulSoup object."""
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if the request failed
    return BeautifulSoup(response.text, 'html.parser')

def get_next_page_url(soup):
    """
    Given a BeautifulSoup object of a chapter page, look for the Next button and extract 
    its target URL from the onclick attribute. Before following the link, the button's
    link text is retrieved and printed.
    
    The button is expected to look like:
      <button class="btn btn-sm btn-secondary nextButton" onclick="location.href = '/Laws/GeneralLaws/PartII/TitleI/Chapter183A';">Next <span class="fa fa-angle-right"></span></button>
    Returns the full URL if found; otherwise returns None.
    """
    next_button = soup.find("button", class_="nextButton", onclick=True)
    if next_button:
        # Get the displayed text of the button
        button_text = next_button.get_text(strip=True)
        print(f"Next button text: '{button_text}'")
        # Extract the URL from the onclick attribute
        onclick_text = next_button.get("onclick", "")
        m = re.search(r"location\.href\s*=\s*'([^']+)'", onclick_text)
        if m:
            next_path = m.group(1)
            return urljoin(base_url, next_path)
    return None

def get_chapter_variant_links(chapter_number):
    """
    For a given base chapter number (e.g., 183), start with the base chapter URL
    and then iteratively follow the Next button (after verifying its link text)
    until no further Next page is found. Returns a sorted list of unique chapter variant URLs.
    """
    variant_links = set()
    base_chapter_path = f'Chapter{chapter_number}'
    current_url = urljoin(base_url, start_path + base_chapter_path)
    variant_links.add(current_url)
    while True:
        try:
            soup = get_soup(current_url)
        except Exception as e:
            print(f"Error accessing {current_url}: {e}")
            break

        next_url = get_next_page_url(soup)
        if next_url and next_url not in variant_links:
            variant_links.add(next_url)
            current_url = next_url
        else:
            break

    return sorted(list(variant_links))

def extract_section_links(chapter_soup, chapter_url):
    """
    Extracts all section links from a chapter page.
    Only links that start with the chapter URL and contain '/Section'
    (which may include letter suffixes) are returned.
    """
    section_links = set()
    for link in chapter_soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(chapter_url) and '/Section' in full_url:
            section_links.add(full_url)
    return list(section_links)

def extract_section_content(section_url):
    """
    Extracts the section title and text content from a given section URL.
    Searches through all <div class="col-xs-12"> elements until it finds one 
    that contains an <h2 id="skipTo"> element starting with "Section ".
    
    Duplicate paragraphs (based on stripped text) are removed.
    """
    soup = get_soup(section_url)
    candidate_divs = soup.find_all('div', class_='col-xs-12')
    target_div = None

    for div in candidate_divs:
        header = div.find('h2', id='skipTo')
        if header:
            header_text = ' '.join(header.stripped_strings)
            if header_text.startswith("Section "):
                target_div = div
                break

    if target_div is None:
        print(f"Section container with valid header not found in {section_url}")
        return None, None

    title = ' '.join(target_div.find('h2', id='skipTo').stripped_strings)

    paragraphs = target_div.find_all('p')
    seen = set()
    unique_paragraphs = []
    for p in paragraphs:
        txt = p.get_text(strip=True)
        if txt and txt not in seen:
            unique_paragraphs.append(txt)
            seen.add(txt)
    text_content = "\n\n".join(unique_paragraphs)
    return title, text_content

def sanitize_filename(name):
    """
    Sanitizes the filename by removing or replacing characters not allowed in file names.
    This version allows alphanumeric characters, dashes, underscores, spaces, and periods.
    """
    return re.sub(r'[^\w\-. ]', '', name).strip().replace(' ', '_')

def main():
    # For each base chapter number, iterate through its variant pages via the Next button.
    for chapter_number in chapter_numbers:
        chapter_variants = get_chapter_variant_links(chapter_number)
        print(f"\nFor Chapter {chapter_number}, found {len(chapter_variants)} variant(s):")
        for variant in chapter_variants:
            print(f"  {variant}")

        # Process each chapter variant.
        for chapter_url in chapter_variants:
            print(f"\nProcessing {chapter_url}")
            try:
                chapter_soup = get_soup(chapter_url)
            except Exception as e:
                print(f"Error accessing {chapter_url}: {e}")
                continue

            # Extract section links on this chapter page.
            section_links = extract_section_links(chapter_soup, chapter_url)
            print(f"Found {len(section_links)} section links in {chapter_url}")

            for section_link in section_links:
                try:
                    print(f"Processing section: {section_link}")
                    title, text_content = extract_section_content(section_link)
                    if title is None or text_content is None:
                        print(f"Skipping {section_link} due to missing content")
                        continue

                    # Build a filename from the chapter and section parts.
                    chapter_part = chapter_url.rstrip('/').split('/')[-1]
                    section_part = section_link.rstrip('/').split('/')[-1]
                    filename = f"{chapter_part}_{section_part}.txt"
                    filename = sanitize_filename(filename)
                    filepath = os.path.join(output_dir, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(title + "\n\n")
                        f.write(text_content)
                    print(f"Saved content to {filepath}")
                except Exception as e:
                    print(f"Error processing {section_link}: {e}")

if __name__ == '__main__':
    main()
