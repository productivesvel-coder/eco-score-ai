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
            content = page.extract_text()
            if content:
                text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- INDIAN CITIES DATABASE ---
indian_cities = {
    "Andhra Pradesh": {
        "Visakhapatnam": (17.6868, 83.2185), "Vijayawada": (16.5062, 80.6480),
        "Guntur": (16.3067, 80.4365), "Nellore": (14.4426, 79.9865),
        "Kurnool": (15.8281, 78.0373), "Rajahmundry": (17.0005, 81.7835)
    },
    "Assam": {
        "Guwahati": (26.1158, 91.7086), "Silchar": (24.8333, 92.7789),
        "Dibrugarh": (27.4728, 94.9120)
    },
    "Bihar": {
        "Patna": (25.5941, 85.1376), "Gaya": (24.7914, 85.0002),
        "Bhagalpur": (25.2425, 87.0145), "Muzaffarpur": (26.1209, 85.3647),
        "Purnia": (25.7771, 87.4753)
    },
    "Chhattisgarh": {
        "Raipur": (21.2514, 81.6296), "Bhilai": (21.1938, 81.3509),
        "Bilaspur": (22.0774, 82.1397)
    },
    "Delhi": {
        "New Delhi": (28.6139, 77.2090), "Najafgarh": (28.6092, 76.9798)
    },
    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311),
        "Vadodara": (22.3072, 73.1812), "Rajkot": (22.3039, 70.8022),
        "Bhavnagar": (21.7645, 72.1519), "Jamnagar": (22.4707, 70.0577),
        "Gandhinagar": (23.2156, 72.6369)
    },
    "Haryana": {
        "Faridabad": (28.4089, 77.3178), "Gurgaon": (28.4595, 77.0266),
        "Panipat": (29.3909, 76.9635), "Ambala": (30.3782, 76.7767)
    },
    "Himachal Pradesh": {
        "Shimla": (31.1048, 77.1734), "Dharamshala": (32.2190, 76.3234)
    },
    "Jammu & Kashmir": {
        "Srinagar": (34.0837, 74.7973), "Jammu": (32.7266, 74.8570)
    },
    "Jharkhand": {
        "Ranchi": (23.3441, 85.3096), "Jamshedpur": (22.8046, 86.2029),
        "Dhanbad": (23.7957, 86.4304), "Bokaro": (23.6693, 86.1511)
    },
    "Karnataka": {
        "Bengaluru": (12.9716, 77.5946), "Hubli": (15.3647, 75.1240),
        "Mysuru": (12.2958, 76.6394), "Belgaum": (15.8497, 74.4977),
        "Mangalore": (12.9141, 74.8560), "Gulbarga": (17.3297, 76.8343)
    },
    "Kerala": {
        "Thiruvananthapuram": (8.5241, 76.9366), "Kochi": (9.9312, 76.2673),
        "Kozhikode": (11.2588, 75.7804), "Thrissur": (10.5276, 76.2144),
        "Kollam": (8.8932, 76.6141)
    },
    "Madhya Pradesh": {
        "Indore": (22.7196, 75.8577), "Bhopal": (23.2599, 77.4126),
        "Jabalpur": (23.1815, 79.9864), "Gwalior": (26.2124, 78.1772),
        "Ujjain": (23.1762, 75.7885), "Sagar": (23.8388, 78.7378)
    },
    "Maharashtra": {
        "Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567),
        "Nagpur": (21.1458, 79.0882), "Thane": (19.2183, 72.9781),
        "Pimpri-Chinchwad": (18.6298, 73.7997), "Nashik": (19.9975, 73.7898),
        "Kalyan": (19.2403, 73.1305), "Aurangabad": (19.8762, 75.3433),
        "Solapur": (17.6599, 75.9064), "Amravati": (20.9374, 77.7796),
        "Kolhapur": (16.7050, 74.2433), "Sangli": (16.8524, 74.5815)
    },
    "Odisha": {
        "Bhubaneswar": (20.2961, 85.8245), "Cuttack": (20.4625, 85.8830),
        "Rourkela": (22.2604, 84.8536), "Brahmapur": (19.3150, 84.7941)
    },
    "Punjab": {
        "Ludhiana": (30.9010, 75.8573), "Amritsar": (31.6340, 74.8723),
        "Jalandhar": (31.3260, 75.5762), "Patiala": (30.3398, 76.3869)
    },
    "Rajasthan": {
        "Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243),
        "Kota": (25.1764, 75.8332), "Bikaner": (28.0229, 73.3119),
        "Ajmer": (26.4499, 74.6399), "Udaipur": (24.5854, 73.7125)
    },
    "Tamil Nadu": {
        "Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198), "Tiruchirappalli": (10.7905, 78.7047),
        "Salem": (11.6643, 78.1460), "Erode": (11.3410, 77.7172),
        "Tirunelveli": (8.7139, 77.7567), "Vellore": (12.9165, 79.1325)
    },
    "Telangana": {
        "Hyderabad": (17.3850, 78.4867), "Warangal": (17.9689, 79.5941),
        "Nizamabad": (18.6725, 78.0941), "Karimnagar": (18.4386, 79.1288)
    },
    "Uttar Pradesh": {
        "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319),
        "Ghaziabad": (28.6692, 77.4538), "Agra": (27.1767, 78.0081),
        "Meerut": (28.9845, 77.7064), "Varanasi": (25.3176, 83.0061),
        "Prayagraj": (25.4358, 81.8463), "Bareilly": (28.3670, 79.4304),
        "Aligarh": (27.8974, 78.0880), "Moradabad": (28.8351, 78.7733),
        "Gorakhpur": (26.7606, 83.3732), "Jhansi": (25.4484, 78.5685)
    },
    "Uttarakhand": {
        "Dehradun": (30.3165, 78.0322), "Haridwar": (29.9457, 78.1642),
        "Haldwani": (29.2183, 79.5130)
    },
    "West Bengal": {
        "Kolkata": (22.5726, 88.3639), "Howrah": (22.5851, 88.3107),
        "Asansol": (23.6739, 86.9524), "Siliguri": (26.7271, 88.3953),
        "Durgapur": (23.5204, 87.3119)
    },
    "Union Territories": {
        "Chandigarh": (30.7333, 76.7794), "Puducherry": (11.9416, 79.8083)
    }
}

st.title("🌍 Sustainability Compatibility Index")
st.markdown("---")

# --- SIDEBAR: LOCATION ---
with st.sidebar:
    st.header("📍 Project Location")
    location_mode = st.selectbox("Method", ["Indian Cities", "Current Location"])
    
    # Default values
    lat, lon = 13.0827, 80.2707 

    if location_mode == "Indian Cities":
        state_choice = st.selectbox("State", list(indian_cities.keys()))
        city_choice = st.selectbox("City", list(indian_cities[state_choice].keys()))
        lat, lon = indian_cities[state_choice][city_choice]
    else:
        # Note: get_geolocation requires browser permissions
        loc = get_geolocation()
        if loc: 
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
    
    st.info(f"Selected Coordinates: {lat}, {lon}")

# --- MAIN PAGE ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📋 Project Details")
    project_title = st.text_input("Project Name")
    project_desc = st.text_area("Quick Summary")
    uploaded_file = st.file_uploader("Upload Project PDF", type=["pdf"])

with col2:
    st.subheader("🎯 AI Analysis")
    # This area will update once the button is clicked

# --- EXECUTION LOGIC ---
if st.button("🚀 Analyze Sustainability Index"):
    if (project_title and project_desc) or uploaded_file:
        with st.spinner('Reading documentation and pulling live climate data...'):
            
            # 1. Extract and Sanitize PDF Text
            pdf_raw = ""
            if uploaded_file:
                pdf_raw = extract_pdf_text(uploaded_file)
            
            # Remove symbols that break URL parameters in a GET request
            clean_pdf = pdf_raw.replace("&", "and").replace("?", "").replace("#", "").strip()
            
            # Truncate to avoid "URL Too Long" error (GET limit is ~2000 chars)
            final_context = f"Title: {project_title} | Desc: {project_desc} | PDF: {clean_pdf[:1500]}"
            
            # 2. Webhook Setup
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu"
            
            # We send lat and lon first to ensure the Weather module reads them correctly
            payload = {
                "lat": lat,
                "lon": lon,
                "project": final_context
            }
            
            try:
                # requests.get with params handles URL encoding for us automatically
                response = requests.get(webhook_url, params=payload, timeout=60)
                
                if response.status_code == 200:
                    # Check for generic "Accepted" response
                    if response.text.lower() == "accepted":
                        st.warning("⚠️ Data received by Make.com, but no response was sent back. Ensure you have a 'Webhook Response' module in your scenario.")
                    else:
                        st.balloons()
                        st.markdown("### 📊 Final Compatibility Report")
                        st.success(response.text)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    st.info("Check if your Make.com Webhook URL is correct.")
            
            except Exception as e:
                st.error(f"Connection failed: {e}")
    else:
        st.warning("Please provide project details or upload a PDF to begin.")
