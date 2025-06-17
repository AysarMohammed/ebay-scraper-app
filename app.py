import asyncio
import sys
import streamlit as st
from scraper import get_clean_ebay_data
import io

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.title("eBay Product Scraper")

query = st.text_input("What do you want to search for?", value="iphone")
max_pages = st.number_input("Number of pages to scrape", min_value=1, max_value=5, value=1)

if st.button("Fetch Data"):
    with st.spinner("Fetching data from eBay..."):
        df = get_clean_ebay_data(query, max_pages)

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
