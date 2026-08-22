import os
import json
import time 
from datetime import datetime
from urllib.parse import urljoin
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BRIGHTDATA_ENDPOINT = os.getenv("BRIGHTDATA_ENDPOINT")

if not BRIGHTDATA_ENDPOINT:
    raise RuntimeError("BRIGHTDATA_ENDPOINT is missing from .env")


def scrape_books():
    print("Connecting to Bright Data Browser API...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            BRIGHTDATA_ENDPOINT,
            timeout=120000
        )

        print("Connected!")

        page = browser.new_page()

        print("Opening Books to Scrape...")

        page.goto(
            "https://books.toscrape.com/",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("Navigated!")
        print("Title:", page.title())
        print("URL:", page.url)

        books = page.locator("article.product_pod")
        print("Books found:", books.count())

        products = []
        for i in range(books.count()):
            book = books.nth(i)

            name = book.locator("h3 a").get_attribute("title")
            price = book.locator(".price_color").inner_text()
            availability = book.locator(".availability").inner_text().strip()
            rating_class = book.locator("p.star-rating").get_attribute("class")
            rating = rating_class.replace("star-rating", "").strip()
            relative_url = book.locator("h3 a").get_attribute("href")
            url = urljoin(page.url, relative_url)

            products.append({
                "name": name,
                "price": price,
                "availability": availability,
                "rating": rating,
                "url": url
            })

            print(products[-1])

        browser.close()

    # Everything below runs after the browser closes, still inside scrape_books()

    os.makedirs("database", exist_ok=True)

    # Save latest snapshot
    with open("database/products.json", "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2, ensure_ascii=False)

    print("Saved", len(products), "products to database/products.json")

    # Save price history
    history_file = "database/price_history.json"

    try:
        with open(history_file, "r", encoding="utf-8") as file:
            price_history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        price_history = {}

    timestamp = datetime.now().isoformat(timespec="seconds")

    for product in products:
        product_name = product["name"]

        if product_name not in price_history:
            price_history[product_name] = []

        price_history[product_name].append({
            "price": product["price"],
            "timestamp": timestamp
        })

    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(price_history, file, indent=2, ensure_ascii=False)

    print("Price history updated!")

    return products

def scrape_with_self_healing(max_retries=3):
    for attempt in range(1, max_retries + 1):

        try:
            print(f"\n🤖 Scraper attempt {attempt}/{max_retries}")

            products = scrape_books()

            print("✅ Scraper completed successfully!")
            return products

        except Exception as error:

            print(f"⚠️ Scraper error: {error}")

            if attempt < max_retries:
                wait_time = attempt * 3

                print(
                    f"🔧 Self-healing activated. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                print("❌ Scraper failed after all retry attempts.")
                return [] 

if __name__ == "__main__":
    scrape_with_self_healing() 
