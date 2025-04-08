import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
CATEGORY_PAGE = "Recipes A-Z _ Allrecipes.com.html"  # Local file from Allrecipes A–Z

def load_categories_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    categories = []
    ul_blocks = soup.select("ul.comp.list__list.mntl-list-unstyled")

    for ul in ul_blocks:
        for li in ul.select("li a[href]"):
            name = li.get_text(strip=True)
            url = li["href"]
            if url.startswith("https://www.allrecipes.com/recipes/"):
                categories.append({"name": name, "url": url})

    print(f"✅ Found {len(categories)} categories.")
    return categories

def scrape_recipes_from_category(cat_name, cat_url, max_pages=3):
    recipes = []

    for page in range(1, max_pages + 1):
        paginated_url = f"{cat_url}?page={page}"
        try:
            r = requests.get(paginated_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            cards = soup.select("div.card__detailsContainer")

            if not cards:
                break  # Stop early if no cards (e.g., end of results)

            for card in cards:
                title_tag = card.select_one("h3.card__title")
                link_tag = card.select_one("a.card__titleLink")
                desc_tag = card.select_one("div.card__summary")
                rating_tag = card.select_one("span.review-star-text")

                if title_tag and link_tag:
                    recipe = {
                        "category": cat_name,
                        "title": title_tag.get_text(strip=True),
                        "url": link_tag["href"],
                        "description": desc_tag.get_text(strip=True) if desc_tag else "",
                        "rating": rating_tag.get_text(strip=True) if rating_tag else "No rating"
                    }
                    recipes.append(recipe)

            print(f"🔍 {cat_name} - Page {page}: {len(cards)} recipes")
            time.sleep(1)  # polite crawling
        except Exception as e:
            print(f"❌ Error scraping {paginated_url}: {e}")
            continue

    return recipes

# Step 1: Load categories
categories = load_categories_from_file(CATEGORY_PAGE)

# Step 2: Scrape each category
all_recipes = []

# TESTING: Limit to first 10 categories for speed
for cat in categories[:10]:
    cat_recipes = scrape_recipes_from_category(cat["name"], cat["url"], max_pages=3)
    all_recipes.extend(cat_recipes)

# Step 3: Save to CSV
df = pd.DataFrame(all_recipes)
df.to_csv("allrecipes_full.csv", index=False)

print(f"✅ DONE: Scraped {len(df)} total recipes. Saved to allrecipes_full.csv.")
