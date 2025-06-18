import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_ebay_products(query, max_pages=1):
    results = []

    for page_num in range(1, max_pages + 1):
        url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_pgn={page_num}"
        print(f"Visiting: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("li.s-item")

        print(f"Page {page_num}: Found {len(items)} items")

        for item in items:
            title_tag = item.select_one(".s-item__title")
            price_tag = item.select_one(".s-item__price")
            link_tag = item.select_one("a.s-item__link")

            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            price = price_tag.get_text(strip=True) if price_tag else "N/A"
            link = link_tag["href"] if link_tag else "N/A"

            results.append({
                "Title": title,
                "Price": price,
                "Link": link
            })

        time.sleep(1)  # Respektfull crawl-hastighet

    print(f"Total items scraped: {len(results)}")
    return results

def get_clean_ebay_data(query, max_pages=1):
    raw_data = scrape_ebay_products(query, max_pages)
    df = pd.DataFrame(raw_data)
    return df
