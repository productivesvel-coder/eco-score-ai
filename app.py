import streamlit as st
import requests
from pypdf import PdfReader
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EcoScore AI | Sustainability Index", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM PROFESSIONAL CSS ---
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    /* Typography */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0rem;
        letter-spacing: -0.02em;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    /* Button enhancements */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        background-color: #2563EB;
        color: white;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
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
        "Kurnool": (15.8281, 78.0373), "Rajahmundry": (17.0005, 81.7835),
        "Tirupati": (13.6288, 79.4192), "Anantapur": (14.6819, 77.6006),
        "Eluru": (16.7107, 81.1035), "Vizianagaram": (18.1067, 83.3956),
        "Machilipatnam": (16.1875, 81.1389), "Tenali": (16.2351, 80.6487),
        "Adoni": (15.6268, 77.2730), "Kadapa": (14.4673, 78.8242),
        "Kakinada": (16.9891, 82.2475)
    },
    "Arunachal Pradesh": {
        "Itanagar": (27.102, 93.692), "Tawang": (27.585, 91.859),
        "Pasighat": (28.062, 95.326), "Ziro": (27.592, 93.840),
        "Naharlagun": (27.108, 93.702)
    },
    "Assam": {
        "Guwahati": (26.1158, 91.7086), "Silchar": (24.8333, 92.7789),
        "Dibrugarh": (27.4728, 94.9120), "Nagaon": (26.3481, 92.6841),
        "Tinsukia": (27.4922, 95.3558), "Jorhat": (26.7509, 94.2037),
        "Tezpur": (26.6528, 92.7926), "Bongaigaon": (26.4716, 90.5584),
        "Diphu": (25.845, 93.431)
    },
    "Bihar": {
        "Patna": (25.5941, 85.1376), "Gaya": (24.7914, 85.0002),
        "Bhagalpur": (25.2425, 87.0145), "Muzaffarpur": (26.1209, 85.3647),
        "Purnia": (25.7771, 87.4753), "Arrah": (25.5560, 84.6603),
        "Begusarai": (25.4182, 86.1273), "Katihar": (25.5516, 87.5720),
        "Munger": (25.3753, 86.4735), "Chapra": (25.7848, 84.7274),
        "Bihar Sharif": (25.1982, 85.5149), "Darbhanga": (26.1542, 85.8918)
    },
    "Chhattisgarh": {
        "Raipur": (21.2514, 81.6296), "Bhilai": (21.1938, 81.3509),
        "Bilaspur": (22.0774, 82.1397), "Korba": (22.3595, 82.7501),
        "Durg": (21.1904, 81.2849), "Rajnandgaon": (21.0972, 81.0348),
        "Jagdalpur": (19.0734, 82.0223), "Ambikapur": (23.1200, 83.1800),
        "Dhamtari": (20.707, 81.549)
    },
    "Delhi": {
        "New Delhi": (28.6139, 77.2090), "Najafgarh": (28.6092, 76.9798),
        "Rohini": (28.7041, 77.1025), "Dwarka": (28.5823, 77.0500)
    },
    "Goa": {
        "Panaji": (15.4909, 73.8278), "Margao": (15.2707, 73.9590),
        "Vasco da Gama": (15.3959, 73.8143), "Mapusa": (15.5937, 73.8142),
        "Ponda": (15.399, 74.012)
    },
    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311),
        "Vadodara": (22.3072, 73.1812), "Rajkot": (22.3039, 70.8022),
        "Bhavnagar": (21.7645, 72.1519), "Jamnagar": (22.4707, 70.0577),
        "Gandhinagar": (23.2156, 72.6369), "Anand": (22.5645, 72.9289),
        "Navsari": (20.9467, 72.9520), "Morbi": (22.8120, 70.8322),
        "Nadiad": (22.6916, 72.8633), "Bharuch": (21.7051, 72.9959),
        "Junagadh": (21.5222, 70.4579), "Vapi": (20.371, 72.910),
        "Surendranagar": (22.722, 71.637)
    },
    "Haryana": {
        "Faridabad": (28.4089, 77.3178), "Gurgaon": (28.4595, 77.0266),
        "Panipat": (29.3909, 76.9635), "Ambala": (30.3782, 76.7767),
        "Rohtak": (28.8909, 76.5796), "Hisar": (29.1492, 75.7217),
        "Karnal": (29.6857, 76.9907), "Sonipat": (28.9931, 77.0151),
        "Yamunanagar": (30.1290, 77.2674), "Panchkula": (30.694, 76.860)
    },
    "Himachal Pradesh": {
        "Shimla": (31.1048, 77.1734), "Dharamshala": (32.2190, 76.3234),
        "Solan": (30.9045, 77.0967), "Mandi": (31.7087, 76.9320),
        "Hamirpur": (31.686, 76.521), "Kullu": (31.957, 77.109),
        "Palampur": (32.110, 76.536)
    },
    "Jammu & Kashmir": {
        "Srinagar": (34.0837, 74.7973), "Jammu": (32.7266, 74.8570),
        "Anantnag": (33.7311, 75.1487), "Baramulla": (34.2023, 74.3481),
        "Kathua": (32.3768, 75.5229), "Udhampur": (32.9172, 75.1416),
        "Poonch": (33.766, 74.093)
    },
    "Jharkhand": {
        "Ranchi": (23.3441, 85.3096), "Jamshedpur": (22.8046, 86.2029),
        "Dhanbad": (23.7957, 86.4304), "Bokaro": (23.6693, 86.1511),
        "Deoghar": (24.4827, 86.6976), "Hazaribagh": (23.9961, 85.3693),
        "Giridih": (24.1873, 86.3051), "Phusro": (23.7675, 85.9902),
        "Ramgarh": (23.633, 85.511), "Sahibganj": (25.244, 87.644)
    },
    "Karnataka": {
        "Bengaluru": (12.9716, 77.5946), "Hubli": (15.3647, 75.1240),
        "Mysuru": (12.2958, 76.6394), "Belgaum": (15.8497, 74.4977),
        "Mangalore": (12.9141, 74.8560), "Gulbarga": (17.3297, 76.8343),
        "Davanagere": (14.4666, 75.9242), "Ballari": (15.1394, 76.9214),
        "Vijayapura": (16.8302, 75.7100), "Shivamogga": (13.9299, 75.5681),
        "Tumakuru": (13.3392, 77.1140), "Raichur": (16.2120, 77.3439),
        "Bidar": (17.910, 77.530), "Hassan": (13.007, 76.102),
        "Udupi": (13.340, 74.742)
    },
    "Kerala": {
        "Thiruvananthapuram": (8.5241, 76.9366), "Kochi": (9.9312, 76.2673),
        "Kozhikode": (11.2588, 75.7804), "Thrissur": (10.5276, 76.2144),
        "Kollam": (8.8932, 76.6141), "Alappuzha": (9.4981, 76.3388),
        "Palakkad": (10.7867, 76.6547), "Malappuram": (11.0735, 76.0740),
        "Kannur": (11.8745, 75.3704), "Kottayam": (9.5889, 76.5213),
        "Kasargod": (12.498, 74.989)
    },
    "Madhya Pradesh": {
        "Indore": (22.7196, 75.8577), "Bhopal": (23.2599, 77.4126),
        "Jabalpur": (23.1815, 79.9864), "Gwalior": (26.2124, 78.1772),
        "Ujjain": (23.1762, 75.7885), "Sagar": (23.8388, 78.7378),
        "Satna": (24.5764, 80.8322), "Ratlam": (23.3315, 75.0367),
        "Rewa": (24.5362, 81.3037), "Katni": (23.8343, 80.3893),
        "Singrauli": (24.2000, 82.6700), "Dewas": (22.962, 76.050),
        "Khandwa": (21.825, 76.350), "Morena": (26.496, 78.001)
    },
    "Maharashtra": {
        "Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567),
        "Nagpur": (21.1458, 79.0882), "Thane": (19.2183, 72.9781),
        "Pimpri-Chinchwad": (18.6298, 73.7997), "Nashik": (19.9975, 73.7898),
        "Kalyan": (19.2403, 73.1305), "Aurangabad": (19.8762, 75.3433),
        "Solapur": (17.6599, 75.9064), "Amravati": (20.9374, 77.7796),
        "Kolhapur": (16.7050, 74.2433), "Sangli": (16.8524, 74.5815),
        "Malegaon": (20.5517, 74.5086), "Akola": (20.7002, 77.0082),
        "Latur": (18.4088, 76.5603), "Dhule": (20.9042, 74.7749),
        "Ahmednagar": (19.0948, 74.7480), "Chandrapur": (19.9615, 79.2961),
        "Parbhani": (19.264, 76.774), "Jalgaon": (21.007, 75.562),
        "Satara": (17.680, 73.992)
    },
    "Manipur": {
        "Imphal": (24.817, 93.936), "Churachandpur": (24.333, 93.666),
        "Thoubal": (24.630, 93.995)
    },
    "Meghalaya": {
        "Shillong": (25.578, 91.893), "Tura": (25.513, 90.220),
        "Jowai": (25.447, 92.203)
    },
    "Mizoram": {
        "Aizawl": (23.727, 92.717), "Lunglei": (22.880, 92.730),
        "Champhai": (23.456, 93.328)
    },
    "Nagaland": {
        "Kohima": (25.674, 94.108), "Dimapur": (25.906, 93.727),
        "Mokokchung": (26.327, 94.508)
    },
    "Odisha": {
        "Bhubaneswar": (20.2961, 85.8245), "Cuttack": (20.4625, 85.8830),
        "Rourkela": (22.2604, 84.8536), "Brahmapur": (19.3150, 84.7941),
        "Sambalpur": (21.4669, 83.9812), "Puri": (19.8135, 85.8312),
        "Balasore": (21.4862, 86.9246), "Bhadrak": (21.0570, 86.5029),
        "Baripada": (21.932, 86.751), "Jharsuguda": (21.850, 83.960)
    },
    "Punjab": {
        "Ludhiana": (30.9010, 75.8573), "Amritsar": (31.6340, 74.8723),
        "Jalandhar": (31.3260, 75.5762), "Patiala": (30.3398, 76.3869),
        "Bathinda": (30.2110, 74.9455), "Hoshiarpur": (31.5143, 75.9115),
        "Mohali": (30.7046, 76.7179), "Pathankot": (32.2733, 75.6522),
        "Moga": (30.817, 75.173), "Batala": (31.818, 75.202)
    },
    "Rajasthan": {
        "Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243),
        "Kota": (25.1764, 75.8332), "Bikaner": (28.0229, 73.3119),
        "Ajmer": (26.4499, 74.6399), "Udaipur": (24.5854, 73.7125),
        "Bhilwara": (25.3407, 74.6313), "Alwar": (27.5530, 76.6346),
        "Bharatpur": (27.2152, 77.4892), "Sriganganagar": (29.9197, 73.8760),
        "Pali": (25.7711, 73.3234), "Sikar": (27.609, 75.139),
        "Churu": (28.291, 74.960)
    },
    "Sikkim": {
        "Gangtok": (27.331, 88.613), "Namchi": (27.167, 88.353),
        "Geyzing": (27.288, 88.270)
    },
    "Tamil Nadu": {
        "Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198), "Tiruchirappalli": (10.7905, 78.7047),
        "Salem": (11.6643, 78.1460), "Erode": (11.3410, 77.7172),
        "Tirunelveli": (8.7139, 77.7567), "Vellore": (12.9165, 79.1325),
        "Thoothukudi": (8.7642, 78.1348), "Thanjavur": (10.7870, 79.1378),
        "Dindigul": (10.3673, 77.9803), "Ranipet": (12.9271, 79.3333),
        "Sivakasi": (9.4532, 77.8024), "Nagercoil": (8.183, 77.411),
        "Kanchipuram": (12.834, 79.703)
    },
    "Telangana": {
        "Hyderabad": (17.3850, 78.4867), "Warangal": (17.9689, 79.5941),
        "Nizamabad": (18.6725, 78.0941), "Karimnagar": (18.4386, 79.1288),
        "Khammam": (17.2473, 80.1514), "Ramagundam": (18.7634, 79.4754),
        "Mahbubnagar": (16.7367, 77.9889), "Nalgonda": (17.0575, 79.2684),
        "Adilabad": (19.676, 78.532), "Siddipet": (18.102, 78.852)
    },
    "Tripura": {
        "Agartala": (23.831, 91.282), "Dharmanagar": (24.366, 92.162),
        "Udaipur": (23.533, 91.483)
    },
    "Uttar Pradesh": {
        "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319),
        "Ghaziabad": (28.6692, 77.4538), "Agra": (27.1767, 78.0081),
        "Meerut": (28.9845, 77.7064), "Varanasi": (25.3176, 83.0061),
        "Prayagraj": (25.4358, 81.8463), "Bareilly": (28.3670, 79.4304),
        "Aligarh": (27.8974, 78.0880), "Moradabad": (28.8351, 78.7733),
        "Gorakhpur": (26.7606, 83.3732), "Jhansi": (25.4484, 78.5685),
        "Muzaffarnagar": (29.4727, 77.7085), "Mathura": (27.4924, 77.6737),
        "Firozabad": (27.1592, 78.3957), "Saharanpur": (29.9680, 77.5452),
        "Noida": (28.5355, 77.3910), "Hapur": (28.725, 77.780),
        "Etawah": (26.778, 79.023), "Mirzapur": (25.146, 82.569)
    },
    "Uttarakhand": {
        "Dehradun": (30.3165, 78.0322), "Haridwar": (29.9457, 78.1642),
        "Haldwani": (29.2183, 79.5130), "Roorkee": (29.8667, 77.8833),
        "Kashipur": (29.2104, 78.9619), "Rishikesh": (30.0869, 78.2676),
        "Rudrapur": (28.976, 79.412)
    },
    "West Bengal": {
        "Kolkata": (22.5726, 88.3639), "Howrah": (22.5851, 88.3107),
        "Asansol": (23.6739, 86.9524), "Siliguri": (26.7271, 88.3953),
        "Durgapur": (23.5204, 87.3119), "Kharagpur": (22.3302, 87.3237),
        "Bardhaman": (23.2324, 87.8615), "English Bazar": (25.0031, 88.1396),
        "Baharampur": (24.0981, 88.2497), "Haldia": (22.066, 88.069),
        "Habra": (22.844, 88.632)
    },
    "Union Territories": {
        "Chandigarh": (30.7333, 76.7794), "Puducherry": (11.9416, 79.8083),
        "Port Blair": (11.6234, 92.7265), "Kavaratti": (10.5667, 72.6417),
        "Silvassa": (20.2765, 73.0083), "Daman": (20.4147, 72.8324),
        "Diu": (20.7144, 70.9874)
    }
}

# --- HEADER SECTION ---
st.markdown('<p class="main-title">🌍 Sustainability Compatibility Index</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced AI evaluation of project viability against localized real-time climate data.</p>', unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: LOCATION ---
with st.sidebar:
    st.header("📍 Project Location")
    
    # Added "Manual Entry" to the options
    location_mode = st.selectbox("Method", ["Indian Cities", "Interactive Map", "Current Location", "Manual Entry"])
    
    lat, lon = 13.0827, 80.2707 # Default Chennai

    if location_mode == "Indian Cities":
        state_choice = st.selectbox("State", list(indian_cities.keys()))
        city_choice = st.selectbox("City", list(indian_cities[state_choice].keys()))
        lat, lon = indian_cities[state_choice][city_choice]
    
    elif location_mode == "Interactive Map":
        st.write("Click on the map to set project coordinates:")
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=4)
        m.add_child(folium.LatLngPopup()) 
        
        map_data = st_folium(m, height=300, width=250)
        
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            
    elif location_mode == "Manual Entry":
        st.write("Enter exact coordinates:")
        # Streamlit number inputs for precise manual entry
        lat = st.number_input("Latitude", value=13.0827, format="%.4f")
        lon = st.number_input("Longitude", value=80.2707, format="%.4f")
            
    else:
        loc = get_geolocation()
        if loc: 
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
    
    st.success(f"**Target Coordinates:** \n\nLat: `{lat:.4f}` | Lon: `{lon:.4f}`")

# --- MAIN PAGE LAYOUT ---
col1, col2 = st.columns([1, 1.2], gap="large")

# UI Polish: Wrapping the inputs in a neat container card
with col1:
    with st.container(border=True):
        st.subheader("📋 Project Details")
        project_title = st.text_input("Project Name", placeholder="e.g., Solar Array Alpha")
        project_desc = st.text_area("Quick Summary", placeholder="Briefly describe the energy goals and requirements...", height=150)
        
        st.markdown("**(Optional) Deep Analysis:**")
        uploaded_file = st.file_uploader("Upload Project PDF", type=["pdf"], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🚀 Run AI Analysis")

# UI Polish: Wrapping the outputs in a container 
with col2:
    with st.container(border=True):
        st.subheader("🎯 AI Analysis Report")
        
        if analyze_button:
            if (project_title and project_desc) or uploaded_file:
                
                # Replaced st.status with st.spinner so the text isn't trapped in a dropdown
                with st.spinner("Extracting documents and syncing with Climate APIs..."):
                    
                    pdf_raw = extract_pdf_text(uploaded_file) if uploaded_file else ""
                    clean_pdf = pdf_raw.replace("&", "and").replace("?", "").replace("#", "").strip()
                    final_context = f"Title: {project_title} | Desc: {project_desc} | PDF: {clean_pdf[:800]}"
                    
                    try:
                        webhook_url = st.secrets["MAKE_WEBHOOK_URL"]
                    except KeyError:
                        st.error("❌ Error: MAKE_WEBHOOK_URL not found in Streamlit Secrets.")
                        st.stop()
                    
                    safe_lat = f"{float(lat):.4f}"
                    safe_lon = f"{float(lon):.4f}"
                    payload = {"lat": safe_lat, "lon": safe_lon, "project": final_context}
                    
                    try:
                        response = requests.get(webhook_url, params=payload, timeout=60)
                        
                        if response.status_code == 200:
                            if "wrong latitude" in response.text.lower():
                                st.error("❌ Location Error: Make sure your coordinates represent a valid geographic location.")
                            else:
                                st.balloons()
                                st.success("Analysis Complete!")
                                st.markdown("---")
                                st.markdown(response.text) 
                        else:
                            st.error(f"Make.com Error {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")
            else:
                st.warning("⚠️ Please provide a Project Name and Summary, or upload a PDF to begin.")
        else:
            # Idle state UI
            st.info("👈 Fill out the project details on the left and click the button to generate your climate compatibility report.")
