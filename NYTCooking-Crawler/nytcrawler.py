from bs4 import BeautifulSoup as bs
import requests

url = 'https://www.allrecipes.com/recipes-a-z-6735880'
response = requests.get(url)

soup = bs(response.content, 'html.parser')

# Find all the <div> elements with the desired class
divs = soup.find_all("div", class_="mntl-alphabetical-list__group")

# Within those divs, find all <a> tags and extract the hrefs
urls = []
for div in divs:
    links = div.find_all("a", href=True)
    urls.extend([a['href'] for a in links])

# Print them
for link in urls:
    print(link)
