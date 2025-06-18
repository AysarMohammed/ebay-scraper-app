import requests
from bs4 import BeautifulSoup
import pandas as pd

def simple_ebay_scraper(query):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve page")
        return pd.DataFrame()
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".s-item")
    
    data = []
    for item in items:
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        if title and price:
            data.append({"title": title.text, "price": price.text})
    
    return pd.DataFrame(data)

df = simple_ebay_scraper("iphone")
print(df.head())
