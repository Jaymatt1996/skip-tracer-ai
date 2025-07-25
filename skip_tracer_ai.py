import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Skip Tracer AI", layout="centered")

st.title("📍 Skip Tracer AI")
st.write("Upload an Excel file with owner name and location info, and we'll help find matching contact info.")

API_KEY = "YOUR_API_KEY_HERE"  # Replace this with your actual People Data Labs API key

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Rename columns to match what the app expects
    df = df.rename(columns={
        "Owner 1 First Name": "First Name",
        "Owner 1 Last Name": "Last Name",
        "Property City": "City",
        "Prop State": "State"
    })

    required_columns = ["First Name", "Last Name", "City", "State"]

    if not all(col in df.columns for col in required_columns):
        st.error("Your file must contain these columns: First Name, Last Name, City, State")
    else:
        results = []

        st.info("🔎 Searching... Please wait a few moments.")

        for index, row in df.iterrows():
            first_name = str(row["First Name"]).strip()
            last_name = str(row["Last Name"]).strip()
            city = str(row["City"]).strip()
            state = str(row["State"]).strip()

            full_name = f"{first_name} {last_name}"

            query = {
                "api_key": API_KEY,
                "first_name": first_name,
                "last_name": last_name,
                "location": f"{city}, {state}"
            }

            try:
                response = requests.get("https://api.peopledatalabs.com/v5/person/enrich", params=query)
                if response.status_code == 200:
                    person = response.json()
                    results.append({
                        "Name": full_name,
                        "City": city,
                        "State": state,
                        "Phone": person.get("phone_numbers", [None])[0],
                        "Email": person.get("emails", [None])[0]
                    })
                else:
                    results.append({
                        "Name": full_name,
                        "City": city,
                        "State": state,
                        "Phone": None,
                        "Email": None
                    })
            except Exception as e:
                results.append({
                    "Name": full_name,
                    "City": city,
                    "State": state,
                    "Phone": None,
                    "Email": None
                })

        result_df = pd.DataFrame(results)
        st.success("✅ Search complete!")

        st.dataframe(result_df)

        # Save to Excel
        output = io.BytesIO()
        result_df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Download Results as Excel",
            data=output,
            file_name="skip_traced_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
