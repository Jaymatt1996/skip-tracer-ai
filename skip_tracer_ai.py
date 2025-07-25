import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Skip Tracer AI", layout="wide")

st.title("🔍 Skip Tracer AI")
st.markdown("Upload an Excel file with columns: `First Name`, `Last Name`, `City`, `State`")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

API_KEY = "5a4d8cf64a39b467481f67f17d1091fe186ae55ab2923a953003e8d84f07a7c5"

def query_people_data_labs(first_name, last_name, city, state):
    url = "https://api.peopledatalabs.com/v5/person/enrich"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "location": f"{city}, {state}"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("data", {})
    else:
        return {}

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    required_columns = {"First Name", "Last Name", "City", "State"}
    if not required_columns.issubset(set(df.columns)):
        st.error("Excel must contain columns: First Name, Last Name, City, State")
    else:
        results = []
        for index, row in df.iterrows():
            first_name = row["First Name"]
            last_name = row["Last Name"]
            city = row["City"]
            state = row["State"]
            
            person = query_people_data_labs(first_name, last_name, city, state)
            
            results.append({
                "First Name": first_name,
                "Last Name": last_name,
                "Location": f"{city}, {state}",
                "Phone": person.get("phone_numbers", [None])[0] if person.get("phone_numbers") else "",
                "Email": person.get("emails", [None])[0] if person.get("emails") else "",
                "LinkedIn": person.get("linkedin_url", ""),
                "Company": person.get("job_company_name", "")
            })

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)

        @st.cache_data
        def convert_df(df):
            return df.to_excel(index=False, engine="openpyxl")

        st.download_button(
            label="📥 Download Results as Excel",
            data=convert_df(result_df),
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
