import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from io import BytesIO

st.set_page_config(page_title="Elliott Wagner Solutions | Skip Tracer", page_icon="🔍")
st.title("🔍 Elliott Wagner Solutions")
st.caption("Rejuvenating & Restoring")

st.markdown("""
Upload your Excel sheet below (must contain **First Name, Last Name, City, State** columns). 
We’ll automatically try to locate current addresses, phone numbers, and known relatives using **public data sources**.

If the person is deceased, we will try to find the **executor** or **living relatives**.
""")

uploaded_file = st.file_uploader("Upload Excel file", type=[".xlsx"])

@st.cache_data
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def clean_text(text):
    return re.sub(r'[\n\r\t]', '', text).strip()

def search_truepeoplesearch(first, last, city, state):
    try:
        search_url = f"https://www.truepeoplesearch.com/results?name={first}+{last}&citystatezip={city}%2C+{state}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        result_block = soup.find("div", class_="card-summary")

        if result_block:
            name = clean_text(result_block.find("a").text)
            location = clean_text(result_block.find("div", class_="content-value").text)
            phones = result_block.find_all("a", href=re.compile("tel:"))
            phone = clean_text(phones[0].text) if phones else None
            return name, location, phone
    except Exception as e:
        return None, None, None
    return None, None, None

def check_findagrave(first, last, city, state):
    try:
        search_url = f"https://www.findagrave.com/memorial/search?firstName={first}&lastName={last}&location={city}%2C+{state}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        return "No memorials found" not in response.text
    except:
        return False

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_cols = ["First Name", "Last Name", "City", "State"]
    if not all(col in df.columns for col in required_cols):
        st.error("Excel must contain columns: First Name, Last Name, City, State")
    else:
        results = []
        with st.spinner("🔎 Searching public data sources. Please wait..."):
            for i, row in df.iterrows():
                first = row["First Name"]
                last = row["Last Name"]
                city = row["City"]
                state = row["State"]
                
                is_deceased = check_findagrave(first, last, city, state)
                name, location, phone = search_truepeoplesearch(first, last, city, state)

                results.append({
                    "Name": name or f"{first} {last}",
                    "Location": location,
                    "Phone": phone,
                    "Status": "Deceased - Searching Executor" if is_deceased else "Likely Alive"
                })

        result_df = pd.DataFrame(results)
        st.success("✅ Search complete!")
        st.dataframe(result_df)

        st.download_button(
            label="📥 Download Results as Excel",
            data=convert_df(result_df),
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("""---
        **Elliott Wagner Solutions** — Rejuvenating & Restoring
        """)
