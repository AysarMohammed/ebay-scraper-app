from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_ebay_products(query, max_pages=1):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_pgn={page_num}"
            print(f"Visiting: {url}")
            page.goto(url)
            page.wait_for_timeout(5000)

            items = page.locator("li.s-item")
            count = items.count()
            print(f"Page {page_num}: Found {count} items")

            for i in range(count):
                try:
                    title = items.nth(i).locator("div.s-item__title > span[role='heading']").inner_text(timeout=1000)
                except:
                    title = "N/A"

                try:
                    price = items.nth(i).locator(".s-item__price").inner_text(timeout=1000)
                except:
                    price = "N/A"

                try:
                    link = items.nth(i).locator("a.s-item__link").get_attribute("href")
                except:
                    link = "N/A"

                results.append({"Title": title, "Price": price, "Link": link})

            time.sleep(2)  # Reduce load on eBay

        browser.close()

    print(f"Total items scraped: {len(results)}")
    return results

def get_clean_ebay_data(query, max_pages=1):
    raw_data = scrape_ebay_products(query, max_pages)
    df = pd.DataFrame(raw_data)
    return df
