import streamlit as st
import pandas as pd
import requests
import json
from io import BytesIO

st.set_page_config(page_title="Skip Tracer AI", layout="centered")

st.title("📍 Skip Tracer AI")
st.markdown("Upload an Excel sheet with names and addresses to find relatives or executors.")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

API_KEY = st.secrets["API_KEY"]  # Make sure it's in Streamlit secrets

def skip_trace_person(first_name, last_name, city=None, state=None):
    url = "https://api.peopledatalabs.com/v5/person/enrich"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "location": f"{city}, {state}" if city and state else ""
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        return {}

@st.cache_data
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("✅ File Uploaded Successfully:")
    st.dataframe(df.head())

    if st.button("🚀 Start Skip Tracing"):
        result_data = []

        for _, row in df.iterrows():
            first = row.get("First Name", "")
            last = row.get("Last Name", "")
            city = row.get("City", "")
            state = row.get("State", "")

            if pd.notna(first) and pd.notna(last):
                info = skip_trace_person(first, last, city, state)
                result_data.append({
                    "First Name": first,
                    "Last Name": last,
                    "City": city,
                    "State": state,
                    "Relatives": info.get("relatives", []),
                    "Phones": info.get("phone_numbers", []),
                    "Emails": info.get("emails", [])
                })

        result_df = pd.DataFrame(result_data)
        st.write("📊 Skip Trace Results:")
        st.dataframe(result_df)

        st.download_button(
            label="📥 Download Results as Excel",
            data=convert_df(result_df),
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
