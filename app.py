import streamlit as st
import requests
from pypdf import PdfReader
from streamlit_js_eval import get_geolocation

# Page Configuration
st.set_page_config(page_title="EcoScore AI India", page_icon="🌱", layout="wide")

# Helper function to extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- INDIAN CITIES DATABASE ---
indian_cities = {
    "Rajasthan": {"Jodhpur": (26.2389, 73.0243), "Jaipur": (26.9124, 75.7873)},
    "Maharashtra": {"Mumbai": (19.0760, 72.8777)},
    "Tamil Nadu": {"Chennai": (13.0827, 80.2707)},
    "Karnataka": {"Bengaluru": (12.9716, 77.5946)},
    "West Bengal": {"Kolkata": (22.5726, 88.3639)}
}

st.title("🌍 Sustainability Compatibility Index")
st.markdown("---")

# --- SIDEBAR: LOCATION ---
with st.sidebar:
    st.header("📍 Project Location")
    location_mode = st.selectbox("Method", ["Indian Cities", "Current Location"])
    lat, lon = 13.0827, 80.2707 

    if location_mode == "Indian Cities":
        state_choice = st.selectbox("State", list(indian_cities.keys()))
        city_choice = st.selectbox("City", list(indian_cities[state_choice].keys()))
        lat, lon = indian_cities[state_choice][city_choice]
    else:
        loc = get_geolocation()
        if loc: lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

# --- MAIN PAGE ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📋 Project Details")
    project_title = st.text_input("Project Name (Optional if PDF uploaded)")
    project_desc = st.text_area("Quick Summary (Optional if PDF uploaded)")
    uploaded_file = st.file_uploader("Upload Project PDF (AI will read the content)", type=["pdf"])

with col2:
    st.subheader("🎯 AI Analysis")
    result_placeholder = st.empty()

# --- EXECUTION LOGIC ---
if st.button("🚀 Analyze Sustainability Index"):
    if (project_title and project_desc) or uploaded_file:
        with st.spinner('Reading your PDF and fetching Weather Data...'):
            
            # --- THE MAGIC PART: EXTRACTING PDF TEXT ---
            pdf_content = ""
            if uploaded_file:
                pdf_content = extract_pdf_text(uploaded_file)
            
            # Combine everything to send to Gemini
            final_context = f"Title: {project_title}\nSummary: {project_desc}\n\nFULL PDF CONTENT:\n{pdf_content}"
            
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu"
            payload = {"lat": lat, "lon": lon, "project": final_context}
            
            try:
                response = requests.get(webhook_url, params=payload, timeout=60)
                if response.status_code == 200:
                    st.balloons()
                    st.markdown("### 📊 Final Compatibility Report")
                    st.success(response.text)
                else:
                    st.error("Make.com Scenario is not responding.")
            except Exception:
                st.error("Request timed out. The PDF might be too long for a quick response.")
    else:
        st.warning("Please upload a PDF or type project details.")
