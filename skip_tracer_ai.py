import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Skip Tracer AI", layout="centered")

st.title("📍 Skip Tracer AI")
st.write("Upload an Excel file with owner name and location info, and we'll help find matching contact info.")

API_KEY = "5a4d8cf64a39b467481f67f17d1091fe186ae55ab2923a953003e8d84f07a7c5"  # Replace with your actual People Data Labs API key

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Rename columns to expected format
    df = df.rename(columns={
        "Owner 1 First Name": "First Name",
        "Owner 1 Last Name": "Last Name",
        "Property City": "City",
        "Prop State": "State"
    })

    required_columns = ["First Name", "Last Name", "City", "State"]

    if not all(col in df.columns for col in required_columns):
        st.error("❌ Excel must contain columns: First Name, Last Name, City, State")
    else:
        results = []

        st.info("🔎 Searching for contact info...")

        for index, row in df.iterrows():
            first_name = str(row["First Name"]).strip()
            last_name = str(row["Last Name"]).strip()
            city = str(row["City"]).strip()
            state = str(row["State"]).strip()

            full_name = f"{first_name} {last_name}"

            params = {
                "api_key": API_KEY,
                "first_name": first_name,
                "last_name": last_name,
                "location": f"{city}, {state}"
            }

            try:
                response = requests.get("https://api.peopledatalabs.com/v5/person/enrich", params=params)
                data = response.json()

                phone = data.get("phone_numbers", [])
                email = data.get("emails", [])

                results.append({
                    "Name": full_name,
                    "City": city,
                    "State": state,
                    "Phone": phone[0] if phone else None,
                    "Email": email[0] if email else None
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
        st.success("✅ Skip trace complete!")

        st.dataframe(result_df)

        # Prepare download
        output = io.BytesIO()
        result_df.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Download Excel with Results",
            data=output,
            file_name="skip_traced_contacts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
