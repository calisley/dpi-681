import requests
from bs4 import BeautifulSoup

# Base URL
url = "https://books.toscrape.com/"

# Send a GET request to the website
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all book entries
books = soup.find_all('article', class_='product_pod')

# Loop through each book and extract title and price
for book in books:
    # The title is stored in the 'title' attribute of the <a> tag inside <h3>
    title = book.h3.a['title']
    
    # The price is in a <p> tag with class 'price_color'
    price = book.find('p', class_='price_color').text

    print(f"{title}: {price}")
