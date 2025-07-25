import streamlit as st
import pandas as pd
import requests

st.title("Skip Tracer AI")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
API_KEY = "5a4d8cf64a39b467481f67f17d1091fe186ae55ab2923a953003e8d84f07a7c5"

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = ["Owner 1 First Name", "Owner 1 Last Name", "Property City", "Prop State"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"Excel must contain columns: {', '.join(required_columns)}")
    else:
        results = []

        for _, row in df.iterrows():
            first_name = row["Owner 1 First Name"]
            last_name = row["Owner 1 Last Name"]
            city = row["Property City"]
            state = row["Prop State"]

            full_name = f"{first_name} {last_name}".strip()

            response = requests.get(
                "https://api.peopledatalabs.com/v5/person/enrich",
                headers={"Content-Type": "application/json"},
                params={
                    "api_key": API_KEY,
                    "first_name": first_name,
                    "last_name": last_name,
                    "location": f"{city}, {state}"
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") != 404:
                    person = data
                    results.append({
                        "Full Name": full_name,
                        "Phone": person.get("phone_numbers", [None])[0],
                        "Email": person.get("emails", [None])[0],
                        "LinkedIn": person.get("linkedin_url"),
                        "Location": person.get("location")
                    })
                else:
                    results.append({
                        "Full Name": full_name,
                        "Phone": None,
                        "Email": None,
                        "LinkedIn": None,
                        "Location": None
                    })
            else:
                results.append({
                    "Full Name": full_name,
                    "Phone": None,
                    "Email": None,
                    "LinkedIn": None,
                    "Location": None
                })

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)

        st.download_button(
            label="Download Results as Excel",
            data=result_df.to_excel(index=False),
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
