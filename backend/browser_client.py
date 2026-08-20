import os
import json
from urllib.parse import urljoin
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BRIGHTDATA_ENDPOINT = os.getenv("BRIGHTDATA_ENDPOINT")

if not BRIGHTDATA_ENDPOINT:
    raise RuntimeError("BRIGHTDATA_ENDPOINT is missing from .env")


def test_browser_connection():
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

        os.makedirs("database", exist_ok=True)
        with open("database/products.json", "w", encoding="utf-8") as file:
            json.dump(products, file, indent=2, ensure_ascii=False)

        print("Saved", len(products), "products to database/products.json")

        browser.close()


if __name__ == "__main__":
    test_browser_connection() 