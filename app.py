import asyncio
import sys
import streamlit as st
import io
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Om du har egen scraper:
from scraper import get_clean_ebay_data

# Fix för Windows asyncio-eventloop
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.title("eBay Product Scraper")

def simple_ebay_scraper(query):
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to retrieve data from eBay.")
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

query = st.text_input("What do you want to search for?", value="iphone")
max_pages = st.number_input("Number of pages to scrape", min_value=1, max_value=5, value=1)

if st.button("Fetch Data"):
    with st.spinner("Fetching data from eBay..."):
        # Försök använda din egna scraper först
        try:
            df = get_clean_ebay_data(query, max_pages)
        except Exception as e:
            st.warning(f"Din scraper gav fel: {e}\nFörsöker med enklare scraper istället.")
            df = pd.DataFrame()

        # Om egen scraper misslyckas eller är tom, använd fallback
        if df.empty:
            df = simple_ebay_scraper(query)
    
    if df.empty:
        st.warning("No results found.")
    else:
        st.success(f"Found {len(df)} items.")
        st.dataframe(df)

        # Excel download
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)

        st.download_button(
            label="Download as Excel",
            data=towrite,
            file_name=f"ebay_{query}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # CSV download
        st.download_button(
            label="Download as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"ebay_{query}.csv",
            mime="text/csv"
        )
