import streamlit as st
import requests

st.set_page_config(page_title="EcoScore AI", page_icon="🌱")

st.title("🌍 Sustainability Compatibility Index")
st.markdown("Enter your project details to see if the local climate supports your goals.")

# User Inputs
project_name = st.text_input("Project Name", placeholder="e.g., Solar Farm, Wind Turbine, Hydro Plant")
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", value=13.08)
with col2:
    lon = st.number_input("Longitude", value=80.27)

if st.button("Analyze Sustainability"):
    if project_name:
        with st.spinner('AI is analyzing weather patterns...'):
            # REPLACE THE URL BELOW WITH YOUR MAKE.COM WEBHOOK URL
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu?lat=13.08&lon=80.27&project=SolarPowerPlant"
            
            payload = {
                "lat": lat,
                "lon": lon,
                "project": project_name
            }
            
            try:
                response = requests.get(webhook_url, params=payload)
                st.success("Analysis Complete!")
                st.info(response.text)
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")
    else:
        st.warning("Please enter a project name.")
