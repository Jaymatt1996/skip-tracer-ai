import streamlit as st
import pandas as pd
import requests
import openpyxl

API_KEY = st.secrets["API_KEY"]
st.set_page_config(page_title="AI Skip Tracer", layout="wide")
st.title("🔍 AI Skip Tracing Assistant")
st.markdown(
    "Upload your Excel file with names and addresses. "
    "This assistant will help you find contact info, deceased status, and executor or relatives if applicable."
)

uploaded_file = st.file_uploader("Upload Excel file", type=[".xlsx", ".xls"])
results = []
result_df = None  # Initialize result variable

def real_skip_trace(name, city=None, state=None):
    api_key = os.getenv("API_KEY")
    if not api_key:
        st.error("API_KEY not set. Add your PeopleDataLabs key in Secrets.")
        return {}
    url = "https://api.peopledatalabs.com/v5/person/enrich"
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    params = {"name": name}
    if city and state:
        params["location"] = f"{city}, {state}"
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        return {
            "Full Name": data.get("full_name", name),
            "Phone": (data.get("phone_numbers") or ["N/A"])[0],
            "Email": (data.get("emails") or ["N/A"])[0],
            "Is Deceased": data.get("deceased", False),
            "Executor/Relative": (data.get("relatives") or ["N/A"])[0],
            "LinkedIn": data.get("linkedin_url", "N/A")
        }
    else:
        return {
            "Full Name": name,
            "Phone": "N/A",
            "Email": "N/A",
            "Is Deceased": "N/A",
            "Executor/Relative": "N/A",
            "LinkedIn": "N/A",
            "Error": resp.text
        }

@st.cache_data
def convert_df(df):
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### 📋 Uploaded Data Preview")
    st.dataframe(df.head())

    if st.button("🔍 Start Skip Tracing"):
        st.write("Working through your list…")
        progress = st.progress(0)
        for idx, row in df.iterrows():
            name = row.get("Name") or row.get("Full Name")
            city = row.get("City")
            state = row.get("State")
            if pd.isna(name):
                continue
            traced = real_skip_trace(name, city, state)
            results.append(traced)
            progress.progress((idx + 1) / len(df))
        result_df = pd.DataFrame(results)
        st.success("Skip tracing complete!")
        st.write(result_df)

if result_df is not None and not result_df.empty:
    st.download_button(
        label="📥 Download Results as Excel",
        data=convert_df(result_df),
        file_name="skip_traced_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument-spreadsheetml.sheet"
    )
