from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import json
import concurrent.futures
import threading

def crawl_allrecipes():
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

    with open("recipe_page_urls.txt", "w", encoding="utf-8") as f:
        for cur_url in urls:
            cur_response = requests.get(cur_url)
            cur_soup = bs(cur_response.content, 'html.parser')

            # Get divs from main content of page
            cur_divs = cur_soup.find_all("div", class_="loc fixedContent")

            for div in cur_divs:
                a_tags = div.find_all("a", id=re.compile(r"^mntl-card-list-items_"), href=True)
                for a in a_tags:
                    f.write(a['href'] + "\n")

def scrape_recipe(url):
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')

    # Recipe name
    name_tag = soup.find('h1', class_='article-heading text-headline-400')
    recipe_name = name_tag.get_text(strip=True) if name_tag else None

    # Ingredients
    ingredient_items = soup.select('li.mm-recipes-structured-ingredients__list-item')
    structured_ingredients = []

    for item in ingredient_items:
        quantity = item.find('span', attrs={'data-ingredient-quantity': 'true'})
        unit = item.find('span', attrs={'data-ingredient-unit': 'true'})
        name = item.find('span', attrs={'data-ingredient-name': 'true'})

        structured_ingredients.append({
            'quantity': quantity.get_text(strip=True) if quantity else None,
            'unit': unit.get_text(strip=True) if unit else None,
            'ingredient': name.get_text(strip=True) if name else None
        })


    # Cooking time and servings
    total_time = servings = None
    details_items = soup.select('div.mm-recipes-details__item')
    for item in details_items:
        label = item.find('div', class_='mm-recipes-details__label')
        value = item.find('div', class_='mm-recipes-details__value')
        if label and value:
            label_text = label.get_text(strip=True).lower()
            value_text = value.get_text(strip=True)
            if 'total time' in label_text:
                total_time = value_text
            elif 'servings' in label_text:
                servings = value_text

    return {
        'url': url,
        'recipe_name': recipe_name,
        'ingredients': structured_ingredients,
        'total_time': total_time,
        'servings': servings
    }


def scrape_and_write(url):
    result = scrape_recipe(url.strip())
    with open("recipes_raw.txt", "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

def scrape_to_csv(num_threads):
    with open("recipe_page_urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Multithreaded scraping
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(scrape_and_write, urls)

    # create csv
    with open("recipes_raw.txt", "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    df = pd.DataFrame(data)
    df.to_csv("recipes.csv", index=False)

scrape_to_csv(15)