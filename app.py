import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# Page Configuration
st.set_page_config(page_title="EcoScore AI India", page_icon="🌱", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Sustainability Compatibility Index")
st.markdown("---")

# --- INDIAN CITIES DATABASE (70+ Cities) ---
indian_cities = {
    "Andhra Pradesh": {"Visakhapatnam": (17.6868, 83.2185), "Vijayawada": (16.5062, 80.6480), "Tirupati": (13.6285, 79.4192)},
    "Arunachal Pradesh": {"Itanagar": (27.0844, 93.6053)},
    "Assam": {"Guwahati": (26.1445, 91.7362), "Dibrugarh": (27.4728, 94.9120)},
    "Bihar": {"Patna": (25.5941, 85.1376), "Gaya": (24.7914, 85.0002)},
    "Chhattisgarh": {"Raipur": (21.2514, 81.6296), "Bhilai": (21.1938, 81.3509)},
    "Goa": {"Panaji": (15.4909, 73.8278), "Margao": (15.2832, 73.9862)},
    "Gujarat": {"Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311), "Vadodara": (22.3072, 73.1812), "Rajkot": (22.3039, 70.8022)},
    "Haryana": {"Gurugram": (28.4595, 77.0266), "Faridabad": (28.4089, 77.3178), "Ambala": (30.3782, 76.7767)},
    "Himachal Pradesh": {"Shimla": (31.1048, 77.1734), "Manali": (32.2396, 77.1887)},
    "Jharkhand": {"Ranchi": (23.3441, 85.3096), "Jamshedpur": (22.8046, 86.2029)},
    "Karnataka": {"Bengaluru": (12.9716, 77.5946), "Mysuru": (12.2958, 76.6394), "Hubballi": (15.3647, 75.1240), "Mangaluru": (12.9141, 74.8560)},
    "Kerala": {"Thiruvananthapuram": (8.5241, 76.9366), "Kochi": (9.9312, 76.2673), "Kozhikode": (11.2588, 75.7804)},
    "Madhya Pradesh": {"Bhopal": (23.2599, 77.4126), "Indore": (22.7196, 75.8577), "Gwalior": (26.2183, 78.1828), "Jabalpur": (23.1815, 79.9864)},
    "Maharashtra": {"Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567), "Nagpur": (21.1458, 79.0882), "Nashik": (19.9975, 73.7898), "Aurangabad": (19.8762, 75.3433), "Thane": (19.2183, 72.9781)},
    "Manipur": {"Imphal": (24.8170, 93.9368)},
    "Meghalaya": {"Shillong": (25.5788, 91.8933)},
    "Mizoram": {"Aizawl": (23.7271, 92.7176)},
    "Nagaland": {"Kohima": (25.6751, 94.1086)},
    "Odisha": {"Bhubaneswar": (20.2961, 85.8245), "Cuttack": (20.4625, 85.8830), "Rourkela": (22.2604, 84.8536)},
    "Punjab": {"Ludhiana": (30.9010, 75.8573), "Amritsar": (31.6340, 74.8723), "Jalandhar": (31.3256, 75.5792), "Patiala": (30.3398, 76.3869)},
    "Rajasthan": {"Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243), "Udaipur": (24.5854, 73.7125), "Kota": (25.2138, 75.8648), "Ajmer": (26.4499, 74.6399), "Bikaner": (28.0229, 73.3119)},
    "Sikkim": {"Gangtok": (27.3314, 88.6138)},
    "Tamil Nadu": {"Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558), "Madurai": (9.9252, 78.1198), "Tiruchirappalli": (10.7905, 78.7047), "Salem": (11.6643, 78.1460)},
    "Telangana": {"Hyderabad": (17.3850, 78.4867), "Warangal": (17.9689, 79.5941)},
    "Tripura": {"Agartala": (23.8315, 91.2868)},
    "Uttar Pradesh": {"Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319), "Varanasi": (25.3176, 82.9739), "Agra": (27.1767, 78.0081), "Meerut": (28.9845, 77.7064), "Prayagraj": (25.4358, 81.8463), "Ghaziabad": (28.6692, 77.4538), "Noida": (28.5355, 77.3910)},
    "Uttarakhand": {"Dehradun": (30.3165, 78.0322), "Haridwar": (29.9457, 78.1642)},
    "West Bengal": {"Kolkata": (22.5726, 88.3639), "Howrah": (22.5851, 88.3107), "Durgapur": (23.4846, 87.3105), "Siliguri": (26.7271, 88.3953)},
    "Union Territories": {"Delhi": (28.6139, 77.2090), "Chandigarh": (30.7333, 76.7794), "Puducherry": (11.9416, 79.8083), "Srinagar": (34.0837, 74.7973), "Jammu": (32.7266, 74.8570)}
}

# --- SIDEBAR: LOCATION SETTINGS ---
with st.sidebar:
    st.header("📍 Project Location")
    location_mode = st.selectbox("Select Location Method", ["Indian Cities", "Current Location", "Manual Coordinates"])
    
    # Default values
    lat, lon = 13.0827, 80.2707 

    if location_mode == "Indian Cities":
        state_choice = st.selectbox("Select State", list(indian_cities.keys()))
        city_choice = st.selectbox("Select City", list(indian_cities[state_choice].keys()))
        lat, lon = indian_cities[state_choice][city_choice]
        st.info(f"Lat: {lat}, Lon: {lon}")

    elif location_mode == "Current Location":
        st.warning("Ensure browser GPS is enabled.")
        loc = get_geolocation()
        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            st.success(f"GPS Active: {lat:.4f}, {lon:.4f}")
        else:
            st.info("Waiting for GPS data...")

    elif location_mode == "Manual Coordinates":
        lat = st.number_input("Latitude", value=13.0827, format="%.4f")
        lon = st.number_input("Longitude", value=80.2707, format="%.4f")

# --- MAIN PAGE: PROJECT INPUT ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📋 Project Details")
    project_title = st.text_input("Project Name", placeholder="e.g., Solar Microgrid for Village X")
    project_desc = st.text_area("Detailed Description", height=150, placeholder="Describe the energy/sustainability goals...")
    uploaded_file = st.file_uploader("Attach Project Document (PDF)", type=["pdf"])

with col2:
    st.subheader("🎯 Result")
    result_card = st.empty()
    result_card.info("Enter details and click 'Analyze' to generate score.")

# --- EXECUTION BUTTON ---
if st.button("🚀 Analyze Sustainability Index"):
    if project_title and project_desc:
        with st.spinner('Accessing Meteorological Data & Running Gemini 3.1...'):
            # REPLACE WITH YOUR ACTUAL MAKE.COM WEBHOOK URL
            webhook_url = "https://hook.eu1.make.com/8t8duu1vrxtai37lpa8tnqdulxo9mgeu?lat=13.08&lon=80.27&project=SolarPowerPlant"
            
            # Prepare data
            full_context = f"Title: {project_title}\nDescription: {project_desc}"
            if uploaded_file:
                full_context += f"\n[Attachment: {uploaded_file.name}]"

            payload = {
                "lat": lat,
                "lon": lon,
                "project": full_context
            }
            
            try:
                # Sending data to Make.com
                response = requests.get(webhook_url, params=payload)
                
                if response.status_code == 200:
                    st.balloons()
                    result_card.success("Analysis Complete")
                    st.markdown("### AI Report:")
                    st.write(response.text)
                else:
                    st.error("Make.com is not responding. Check your Scheduling Switch.")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
    else:
        st.warning("Please provide both a Project Name and a Description.")
