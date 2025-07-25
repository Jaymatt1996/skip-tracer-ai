import streamlit as st
import pandas as pd
import requests
import io

# Replace this with your actual PeopleDataLabs API Key
API_KEY = "5a4d8cf64a39b467481f67f17d1091fe186ae55ab2923a953003e8d84f07a7c5"


st.set_page_config(page_title="Skip Tracer AI", layout="wide")
st.title("📍 Skip Tracer AI")
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file and st.button("Start Skip Tracing"):
    df = pd.read_excel(uploaded_file)
    results = []

    for index, row in df.iterrows():
        first_name = str(row.get("Owner 1 First Name", "")).strip()
        last_name = str(row.get("Owner 1 Last Name", "")).strip()
        city = str(row.get("Property City", "")).strip()
        state = str(row.get("Prop State", "")).strip()

        if not first_name or not last_name:
            continue

        params = {
            "api_key": API_KEY,
            "first_name": first_name,
            "last_name": last_name,
            "location": f"{city}, {state}",
        }

        response = requests.get("https://api.peopledatalabs.com/v5/person/enrich", params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200 and "data" in data:
                person = data["data"]
                results.append({
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Location": f"{city}, {state}",
                    "Phone": person.get("phone_numbers", [None])[0],
                    "Email": person.get("emails", [None])[0],
                    "LinkedIn": person.get("linkedin_url", ""),
                    "Company": person.get("job_company_name", "")
                })

    if results:
        result_df = pd.DataFrame(results)

        @st.cache_data
        def convert_df(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button(
            label="📥 Download Results as Excel",
            data=convert_df(result_df),
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No results found. Try different names or locations.")
