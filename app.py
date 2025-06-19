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

st.title("🛒 eBay Product Scraper")

def simple_ebay_scraper(query, max_pages=1):
    data = []
    bad_titles = [
        "Shop on eBay", 
        "Shop by Brand", 
        "Tap item to see current price", 
        "See price", 
        "Explore More", 
        "Sponsored"
    ]
    for page in range(1, max_pages + 1):
        url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_pgn={page}"
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to retrieve data from eBay on page {page}.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".s-item")

        for item in items:
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            if title and price:
                cleaned_title = title.text.strip()
                if cleaned_title not in bad_titles:
                    data.append({"title": cleaned_title, "price": price.text.strip()})

    return pd.DataFrame(data)

# 🔎 Inputfält
query = st.text_input("Enter product name (e.g. 'iPhone', 'TV', 'Laptop')", value="iphone")
max_pages = st.number_input("Number of pages to scrape", min_value=1, max_value=5, value=1)

if st.button("Fetch Data"):
    with st.spinner("Fetching data from eBay..."):
        # Försök använda din egen scraper först
        try:
            df = get_clean_ebay_data(query, max_pages)
        except Exception as e:
            st.warning(f"Din scraper gav fel: {e}\nFörsöker med enklare scraper istället.")
            df = pd.DataFrame()

        # Fallback
        if df.empty:
            df = simple_ebay_scraper(query, max_pages)

    if df.empty:
        st.warning("No results found.")
    else:
        st.success(f"✅ {len(df)} products found.")
        st.dataframe(df)

        # 💾 Nedladdningsknappar
        col1, col2 = st.columns(2)
        with col1:
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            st.download_button(
                label="📥 Download Excel",
                data=towrite,
                file_name=f"ebay_{query}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"ebay_{query}.csv",
                mime="text/csv"
            )

# 📌 Versionstext
st.caption("🧪 This is a demo version. Full version includes multi-page scraping and advanced export options.")
