import streamlit as st
import requests

st.set_page_config(page_title="EcoScore AI Pro", page_icon="🌱", layout="wide")

st.title("🌍 Sustainability Compatibility Index")
st.markdown("Upload your project proposal or describe it to get an AI-driven suitability score.")

# Sidebar for Location
st.sidebar.header("📍 Project Location")
lat = st.sidebar.number_input("Latitude", value=13.08, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=80.27, format="%.4f")

# Main Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Project Details")
    project_desc = st.text_area("Project Description", placeholder="Describe your project here...")
    uploaded_file = st.file_uploader("Or upload a Project PDF", type=["pdf"])

with col2:
    st.subheader("Results")
    result_placeholder = st.empty()
    result_placeholder.info("Awaiting analysis...")

if st.button("Analyze Sustainability"):
    # Combine text and file info
    full_description = project_desc
    if uploaded_file:
        full_description += f"\n[File Uploaded: {uploaded_file.name}]"

    if full_description:
        with st.spinner('AI is analyzing weather patterns...'):
            # REPLACE WITH YOUR MAKE.COM URL
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu?lat=13.08&lon=80.27&project=SolarPowerPlant"
            
            payload = {
                "lat": lat,
                "lon": lon,
                "project": full_description
            }
            
            try:
                response = requests.get(webhook_url, params=payload)
                result_placeholder.success("Analysis Complete!")
                st.balloons()
                # This displays the score in a nice box
                st.markdown(f"### AI Analysis:\n{response.text}")
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")
    else:
        st.warning("Please provide a description or upload a PDF.")
