import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# Page Configuration
st.set_page_config(page_title="EcoScore AI India", page_icon="🌱", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Sustainability Compatibility Index")
st.markdown("---")

# --- INDIAN CITIES DATABASE ---
indian_cities = {
    "Andhra Pradesh": {"Visakhapatnam": (17.6868, 83.2185), "Vijayawada": (16.5062, 80.6480)},
    "Bihar": {"Patna": (25.5941, 85.1376)},
    "Gujarat": {"Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311)},
    "Karnataka": {"Bengaluru": (12.9716, 77.5946), "Mysuru": (12.2958, 76.6394)},
    "Maharashtra": {"Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567)},
    "Rajasthan": {"Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243)},
    "Tamil Nadu": {"Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558)},
    "Telangana": {"Hyderabad": (17.3850, 78.4867)},
    "West Bengal": {"Kolkata": (22.5726, 88.3639)},
    "Union Territories": {"Delhi": (28.6139, 77.2090), "Chandigarh": (30.7333, 76.7794)}
}

# --- SIDEBAR: LOCATION ---
with st.sidebar:
    st.header("📍 Project Location")
    location_mode = st.selectbox("Method", ["Indian Cities", "Current Location", "Manual"])
    
    lat, lon = 13.0827, 80.2707 

    if location_mode == "Indian Cities":
        state_choice = st.selectbox("State", list(indian_cities.keys()))
        city_choice = st.selectbox("City", list(indian_cities[state_choice].keys()))
        lat, lon = indian_cities[state_choice][city_choice]
    elif location_mode == "Current Location":
        loc = get_geolocation()
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.success(f"GPS Active")
        else:
            st.info("Waiting for GPS...")
    elif location_mode == "Manual":
        lat = st.number_input("Lat", value=13.0827)
        lon = st.number_input("Lon", value=80.2707)

# --- MAIN PAGE ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📋 Project Details")
    project_title = st.text_input("Project Name (Optional if PDF uploaded)")
    project_desc = st.text_area("Description (Optional if PDF uploaded)")
    uploaded_file = st.file_uploader("Upload Project PDF", type=["pdf"])

with col2:
    st.subheader("🎯 AI Analysis")
    result_placeholder = st.empty()
    result_placeholder.info("Ready for analysis. Please provide project details or a PDF.")

# --- EXECUTION LOGIC ---
if st.button("🚀 Analyze Sustainability Index"):
    # Check if we have at least SOME info to send
    if (project_title and project_desc) or uploaded_file:
        with st.spinner('Syncing with Gemini AI & Weather Data...'):
            # YOUR WEBHOOK URL
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu"
            
            # Construct the text payload
            combined_text = f"Title: {project_title}\nDescription: {project_desc}"
            if uploaded_file:
                combined_text += f"\n[ATTACHMENT: {uploaded_file.name}]"

            payload = {
                "lat": lat,
                "lon": lon,
                "project": combined_text
            }
            
            try:
                # 60 second timeout for deep AI analysis
                response = requests.get(webhook_url, params=payload, timeout=60)
                
                if response.status_code == 200:
                    # Success UI
                    st.balloons()
                    result_placeholder.empty()
                    st.markdown("### 📊 Final Compatibility Report")
                    st.success(response.text)
                else:
                    st.error(f"Error from Make.com: {response.status_code}. Ensure Scenario is ON.")
            except Exception as e:
                st.error("The request timed out. Gemini is taking a bit longer to process your PDF.")
    else:
        st.warning("⚠️ Please provide a Project Title/Description OR upload a PDF to proceed.")
