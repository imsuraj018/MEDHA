import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

st.set_page_config(
    page_title="Newborn Health Surveillance",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(20,184,166,.10), transparent 28%),
            radial-gradient(circle at 95% 5%, rgba(59,130,246,.08), transparent 25%),
            #f6f9fc;
    }
    [data-testid="stHeader"] {
        background: rgba(246,249,252,.82);
        backdrop-filter: blur(12px);
    }
    .block-container {
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#073b4c 0%,#075e67 55%,#0a7470 100%);
        border-right: 0;
    }
    section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }
    section[data-testid="stSidebar"] * { color: rgba(255,255,255,.94); }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,.07);
        color: white;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 12px;
        text-align: left;
        transition: all .18s ease;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,.17);
        transform: translateX(3px);
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,.10);
        border-color: rgba(255,255,255,.18);
        border-radius: 10px;
    }
    .page-hero {
        position: relative;
        overflow: hidden;
        padding: 28px 30px;
        margin-bottom: 24px;
        border-radius: 22px;
        color: white;
        background: linear-gradient(135deg,#075e67 0%,#0b7c76 58%,#159a91 100%);
        box-shadow: 0 14px 35px rgba(7,94,103,.18);
    }
    .page-hero::after {
        content: "✚";
        position: absolute;
        right: 34px;
        top: -28px;
        font-size: 150px;
        opacity: .08;
        transform: rotate(10deg);
    }
    .hero-kicker {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        opacity: .78;
        font-weight: 700;
    }
    .hero-title {
        font-size: 32px;
        font-weight: 800;
        margin: 5px 0 4px;
        letter-spacing: -.6px;
    }
    .hero-subtitle { font-size: 14px; opacity: .86; margin: 0; }
    .dashboard-card {
        position: relative;
        overflow: hidden;
        padding: 20px;
        border-radius: 18px;
        background: rgba(255,255,255,.94);
        border: 1px solid rgba(15,23,42,.07);
        box-shadow: 0 8px 24px rgba(15,23,42,.055);
        min-height: 132px;
        transition: transform .18s ease, box-shadow .18s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 30px rgba(15,23,42,.09);
    }
    .dashboard-card::after {
        content: "";
        position: absolute;
        width: 90px; height: 90px;
        right: -32px; bottom: -35px;
        border-radius: 50%;
        background: rgba(20,184,166,.08);
    }
    .dashboard-card h4 {
        margin: 0 0 9px;
        font-size: 13px;
        color: #64748b;
        font-weight: 700;
    }
    .dashboard-number {
        font-size: 34px;
        line-height: 1.1;
        font-weight: 800;
        color: #0f172a;
    }
    .dashboard-icon {
        float: right;
        width: 38px; height: 38px;
        display: flex;
        align-items: center; justify-content: center;
        border-radius: 11px;
        background: #e6fffb;
        font-size: 19px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 26px;
        margin-bottom: 13px;
    }
    .baby-header {
        background: rgba(255,255,255,.94);
        border-radius: 18px;
        padding: 24px;
        border: 1px solid rgba(15,23,42,.07);
        box-shadow: 0 8px 24px rgba(15,23,42,.05);
        margin-bottom: 20px;
    }
    .small-text { color: #64748b; font-size: 13px; }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.92);
        padding: 15px 17px;
        border-radius: 15px;
        border: 1px solid rgba(15,23,42,.07);
        box-shadow: 0 6px 18px rgba(15,23,42,.045);
    }
    .stButton > button { border-radius: 10px; font-weight: 600; transition: all .15s ease; }
    .stButton > button:hover { transform: translateY(-1px); }
    .stButton > button[kind="primary"] { border-radius: 11px; font-weight: 700; }
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea { border-radius: 10px !important; }
    button[data-baseweb="tab"] { font-weight: 650; }
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(15,23,42,.07);
    }
    div[data-testid="stAlert"] { border-radius: 13px; border: 0; }
    div[data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,.90);
        border-radius: 17px;
        padding: 8px;
        border: 1px solid rgba(15,23,42,.06);
        box-shadow: 0 7px 22px rgba(15,23,42,.045);
    }
    div[role="radiogroup"] {
        gap: 7px;
        padding: 7px;
        background: rgba(255,255,255,.78);
        border: 1px solid rgba(15,23,42,.06);
        border-radius: 14px;
    }
    .status-normal {
        background: #dcfce7;
        color: #166534;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .status-warning {
        background: #fef3c7;
        color: #92400e;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .status-danger {
        background: #fee2e2;
        color: #991b1b;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .status-info {
        background: #dbeafe;
        color: #1e40af;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    @media (max-width: 900px) {
        .hero-title { font-size: 25px; }
        .page-hero { padding: 22px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TRANSLATIONS
# ============================================================

TRANSLATIONS = {
    "app_title": {
        "en": "Newborn Health Surveillance",
        "mr": "नवजात आरोग्य निरीक्षण प्रणाली",
        "hi": "नवजात स्वास्थ्य निगरानी प्रणाली"
    },
    "dashboard": {
        "en": "Dashboard",
        "mr": "डॅशबोर्ड",
        "hi": "डैशबोर्ड"
    },
    "newborns": {
        "en": "Newborns",
        "mr": "नवजात बाळे",
        "hi": "नवजात शिशु"
    },
    "register_newborn": {
        "en": "Register Newborn",
        "mr": "नवजात बाळाची नोंदणी",
        "hi": "नवजात शिशु का पंजीकरण"
    },
    "followups": {
        "en": "Follow-ups",
        "mr": "पाठपुरावा",
        "hi": "फॉलो-अप"
    },
    "referrals": {
        "en": "Referrals",
        "mr": "रेफरल",
        "hi": "रेफरल"
    },
    "alerts": {
        "en": "Alerts",
        "mr": "सूचना",
        "hi": "अलर्ट"
    },
    "reports": {
        "en": "Reports",
        "mr": "अहवाल",
        "hi": "रिपोर्ट"
    },
    "data_quality": {
        "en": "Data Quality",
        "mr": "डेटा गुणवत्ता",
        "hi": "डेटा गुणवत्ता"
    },
    "research": {
        "en": "Research & Analytics",
        "mr": "संशोधन आणि विश्लेषण",
        "hi": "अनुसंधान और विश्लेषण"
    },
    "administration": {
        "en": "Administration",
        "mr": "प्रशासन",
        "hi": "प्रशासन"
    },
    "settings": {
        "en": "Settings",
        "mr": "सेटिंग्ज",
        "hi": "सेटिंग्स"
    },
    "language": {
        "en": "Language",
        "mr": "भाषा",
        "hi": "भाषा"
    },
    "role": {
        "en": "Role",
        "mr": "भूमिका",
        "hi": "भूमिका"
    },
    "asha_worker": {
        "en": "ASHA Worker",
        "mr": "आशा कार्यकर्ता",
        "hi": "आशा कार्यकर्ता"
    },
    "taluka_officer": {
        "en": "Taluka Officer",
        "mr": "तालुका अधिकारी",
        "hi": "तालुका अधिकारी"
    },
    "district_officer": {
        "en": "District Officer",
        "mr": "जिल्हा अधिकारी",
        "hi": "जिला अधिकारी"
    },
    "state_admin": {
        "en": "State Admin",
        "mr": "राज्य प्रशासक",
        "hi": "राज्य प्रशासक"
    },
    "super_admin": {
        "en": "Super Admin",
        "mr": "सुपर प्रशासक",
        "hi": "सुपर एडमिन"
    },
    "total_newborns": {
        "en": "Total Newborns",
        "mr": "एकूण नवजात बाळे",
        "hi": "कुल नवजात शिशु"
    },
    "today_visits": {
        "en": "Today's Visits",
        "mr": "आजच्या भेटी",
        "hi": "आज की मुलाकातें"
    },
    "pending_followups": {
        "en": "Pending Follow-ups",
        "mr": "प्रलंबित पाठपुरावा",
        "hi": "लंबित फॉलो-अप"
    },
    "pending_referrals": {
        "en": "Pending Referrals",
        "mr": "प्रलंबित रेफरल",
        "hi": "लंबित रेफरल"
    },
    "needs_attention": {
        "en": "Needs Attention",
        "mr": "लक्ष देणे आवश्यक",
        "hi": "ध्यान आवश्यक"
    },
    "birth_details": {
        "en": "Birth Details",
        "mr": "जन्माची माहिती",
        "hi": "जन्म विवरण"
    },
    "mother_details": {
        "en": "Mother Details",
        "mr": "आईची माहिती",
        "hi": "माता की जानकारी"
    },
    "newborn_assessment": {
        "en": "Newborn Assessment",
        "mr": "नवजात तपासणी",
        "hi": "नवजात मूल्यांकन"
    },
    "conditions": {
        "en": "Conditions",
        "mr": "आरोग्य स्थिती",
        "hi": "स्वास्थ्य स्थितियां"
    },
    "referral_details": {
        "en": "Referral Details",
        "mr": "रेफरल माहिती",
        "hi": "रेफरल विवरण"
    },
    "followup_schedule": {
        "en": "Follow-up Schedule",
        "mr": "पाठपुरावा वेळापत्रक",
        "hi": "फॉलो-अप अनुसूची"
    },
    "newborn_name": {
        "en": "Newborn Name",
        "mr": "नवजात बाळाचे नाव",
        "hi": "नवजात शिशु का नाम"
    },
    "date_of_birth": {
        "en": "Date of Birth",
        "mr": "जन्म तारीख",
        "hi": "जन्म तिथि"
    },
    "time_of_birth": {
        "en": "Time of Birth",
        "mr": "जन्माची वेळ",
        "hi": "जन्म का समय"
    },
    "sex": {
        "en": "Sex",
        "mr": "लिंग",
        "hi": "लिंग"
    },
    "male": {
        "en": "Male",
        "mr": "मुलगा",
        "hi": "लड़का"
    },
    "female": {
        "en": "Female",
        "mr": "मुलगी",
        "hi": "लड़की"
    },
    "other": {
        "en": "Other",
        "mr": "इतर",
        "hi": "अन्य"
    },
    "birth_weight": {
        "en": "Birth Weight (kg)",
        "mr": "जन्म वजन (किलो)",
        "hi": "जन्म वजन (किलो)"
    },
    "gestational_age": {
        "en": "Gestational Age (weeks)",
        "mr": "गर्भधारणेचे वय (आठवडे)",
        "hi": "गर्भकालीन आयु (सप्ताह)"
    },
    "place_of_birth": {
        "en": "Place of Birth",
        "mr": "जन्माचे ठिकाण",
        "hi": "जन्म स्थान"
    },
    "delivery_type": {
        "en": "Delivery Type",
        "mr": "प्रसूतीचा प्रकार",
        "hi": "प्रसव का प्रकार"
    },
    "mother_name": {
        "en": "Mother's Name",
        "mr": "आईचे नाव",
        "hi": "माता का नाम"
    },
    "mother_age": {
        "en": "Mother's Age",
        "mr": "आईचे वय",
        "hi": "माता की आयु"
    },
    "phone": {
        "en": "Phone Number",
        "mr": "फोन नंबर",
        "hi": "फोन नंबर"
    },
    "address": {
        "en": "Address",
        "mr": "पत्ता",
        "hi": "पता"
    },
    "village": {
        "en": "Village",
        "mr": "गाव",
        "hi": "गांव"
    },
    "taluka": {
        "en": "Taluka",
        "mr": "तालुका",
        "hi": "तालुका"
    },
    "district": {
        "en": "District",
        "mr": "जिल्हा",
        "hi": "जिला"
    },
    "temperature": {
        "en": "Temperature (°C)",
        "mr": "तापमान (°C)",
        "hi": "तापमान (°C)"
    },
    "feeding_difficulty": {
        "en": "Feeding Difficulty",
        "mr": "दूध पिण्यात अडचण",
        "hi": "दूध पीने में कठिनाई"
    },
    "breathing_difficulty": {
        "en": "Breathing Difficulty",
        "mr": "श्वास घेण्यास त्रास",
        "hi": "सांस लेने में कठिनाई"
    },
    "jaundice_observed": {
        "en": "Jaundice Observed",
        "mr": "कावीळ दिसून आली",
        "hi": "पीलिया देखा गया"
    },
    "yes": {
        "en": "Yes",
        "mr": "होय",
        "hi": "हाँ"
    },
    "no": {
        "en": "No",
        "mr": "नाही",
        "hi": "नहीं"
    },
    "submit": {
        "en": "Submit",
        "mr": "सबमिट करा",
        "hi": "सबमिट करें"
    },
    "save": {
        "en": "Save",
        "mr": "जतन करा",
        "hi": "सहेजें"
    },
    "search": {
        "en": "Search",
        "mr": "शोधा",
        "hi": "खोजें"
    },
    "status": {
        "en": "Status",
        "mr": "स्थिती",
        "hi": "स्थिति"
    },
    "normal": {
        "en": "Normal",
        "mr": "सामान्य",
        "hi": "सामान्य"
    },
    "attention": {
        "en": "Needs Attention",
        "mr": "लक्ष देणे आवश्यक",
        "hi": "ध्यान आवश्यक"
    },
    "urgent": {
        "en": "Urgent",
        "mr": "तातडीचे",
        "hi": "तत्काल"
    },
    "referred": {
        "en": "Referred",
        "mr": "रेफर केले",
        "hi": "रेफर किया गया"
    },
    "pending": {
        "en": "Pending",
        "mr": "प्रलंबित",
        "hi": "लंबित"
    },
    "register_success": {
        "en": "Newborn registered successfully.",
        "mr": "नवजात बाळाची नोंदणी यशस्वी झाली.",
        "hi": "नवजात शिशु का पंजीकरण सफल रहा।"
    }
}

LANGUAGES = {
    "English": "en",
    "मराठी": "mr",
    "हिन्दी": "hi"
}

def local_translate(key, language):
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(language, TRANSLATIONS[key]["en"])
    return key

@st.cache_data(show_spinner=False)
def google_translate(text, target_language, source_language="en"):
    if not text or target_language == source_language or not GOOGLE_TRANSLATE_API_KEY:
        return text

    url = "https://translation.googleapis.com/language/translate/v2"
    params = {"key": GOOGLE_TRANSLATE_API_KEY}
    data = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text"
    }
    try:
        response = requests.post(url, params=params, json=data, timeout=5)
        response.raise_for_status()
        result = response.json()
        return result["data"]["translations"][0]["translatedText"]
    except Exception:
        return text

def dynamic_translate(text, language):
    if language == "en":
        return text
    return google_translate(text, language, "en")

def t(key):
    return local_translate(key, st.session_state.language)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "en"

if "role" not in st.session_state:
    st.session_state.role = "ASHA Worker"

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "registration_step" not in st.session_state:
    st.session_state.registration_step = "1. Birth Details"

if "newborns" not in st.session_state:
    st.session_state.newborns = [
        {
            "id": "NB-2026-001",
            "name": "Aarav Sharma",
            "dob": date(2026, 9, 10),
            "sex": "Male",
            "weight": 2.4,
            "gestational_age": 38,
            "village": "Kharadi",
            "taluka": "Haveli",
            "district": "Pune",
            "asha": "Sunita Patil",
            "status": "Needs Attention",
            "conditions": ["Jaundice", "Low Birth Weight"],
            "next_followup": date.today(),
            "referral": True
        },
        {
            "id": "NB-2026-002",
            "name": "Anaya Joshi",
            "dob": date(2026, 9, 12),
            "sex": "Female",
            "weight": 3.1,
            "gestational_age": 39,
            "village": "Wagholi",
            "taluka": "Haveli",
            "district": "Pune",
            "asha": "Sunita Patil",
            "status": "Normal",
            "conditions": [],
            "next_followup": date.today() + timedelta(days=2),
            "referral": False
        },
        {
            "id": "NB-2026-003",
            "name": "Vihaan Patil",
            "dob": date(2026, 9, 5),
            "sex": "Male",
            "weight": 1.9,
            "gestational_age": 35,
            "village": "Manjari",
            "taluka": "Haveli",
            "district": "Pune",
            "asha": "Sunita Patil",
            "status": "Urgent",
            "conditions": ["Prematurity", "Low Birth Weight", "Feeding Difficulty"],
            "next_followup": date.today(),
            "referral": True
        },
        {
            "id": "NB-2026-004",
            "name": "Ishita Deshmukh",
            "dob": date(2026, 9, 14),
            "sex": "Female",
            "weight": 2.9,
            "gestational_age": 39,
            "village": "Hadapsar",
            "taluka": "Haveli",
            "district": "Pune",
            "asha": "Sunita Patil",
            "status": "Normal",
            "conditions": [],
            "next_followup": date.today() + timedelta(days=4),
            "referral": False
        }
    ]

# Default values for registration state
def init_registration_fields():
    defaults = {
        "reg_name": "",
        "reg_dob": date.today(),
        "reg_time": datetime.now().time(),
        "reg_sex": "Male",
        "reg_weight": 2.5,
        "reg_gestational_age": 38,
        "reg_place": "PHC",
        "reg_delivery": "Normal",
        "reg_district": "Pune",
        "reg_taluka": "Haveli",
        "reg_village": "",
        "reg_mother_name": "",
        "reg_mother_age": 25,
        "reg_phone": "",
        "reg_address": "",
        "reg_temperature": 36.5,
        "reg_feeding": "No",
        "reg_breathing": "No",
        "reg_jaundice": "No",
        "reg_breastfeeding": "Yes",
        "reg_danger_signs": "No",
        "reg_conditions": [],
        "reg_referral": "No",
        "reg_facility": "Nearest PHC",
        "reg_reason": "",
        "reg_transport": "No"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_registration_fields()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def status_html(status):
    if status == "Normal":
        return '<span class="status-normal">🟢 Normal</span>'
    if status == "Needs Attention":
        return '<span class="status-warning">🟡 Needs Attention</span>'
    if status == "Urgent":
        return '<span class="status-danger">🔴 Urgent</span>'
    if status == "Referred":
        return '<span class="status-info">🔵 Referred</span>'
    return status

def generate_newborn_id():
    return f"NB-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"

def calculate_status(weight, gestational_age, conditions):
    risk_conditions = {
        "Jaundice", "Low Birth Weight", "Prematurity",
        "Respiratory Problem", "Feeding Difficulty",
        "Suspected Infection", "Hypothermia", "Convulsions"
    }
    risk_count = len(set(conditions).intersection(risk_conditions))
    if weight < 2.0 or gestational_age < 37 or risk_count >= 2:
        return "Urgent"
    if risk_count == 1:
        return "Needs Attention"
    return "Normal"

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Arial, sans-serif", color="#334155"),
        title=dict(font=dict(size=15, color="#0f172a")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=50, b=35),
        legend=dict(bgcolor="rgba(255,255,255,.75)", borderwidth=0)
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#edf2f7", zeroline=False)
    return fig

def metric_card(title, value, icon):
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-icon">{icon}</div>
            <h4>{title}</h4>
            <div class="dashboard-number">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(f"<h2>👶 {t('app_title')}</h2>", unsafe_allow_html=True)
    st.divider()

    lang_labels = list(LANGUAGES.keys())
    current_lang_idx = list(LANGUAGES.values()).index(st.session_state.language)
    selected_language_name = st.selectbox(
        t("language"),
        lang_labels,
        index=current_lang_idx,
        key="sb_language_select"
    )
    st.session_state.language = LANGUAGES[selected_language_name]

    st.divider()

    role_options = [
        "ASHA Worker",
        "Taluka Officer",
        "District Officer",
        "State Admin",
        "Super Admin"
    ]
    role = st.selectbox(
        t("role"),
        role_options,
        index=role_options.index(st.session_state.role),
        key="sb_role_select"
    )
    st.session_state.role = role

    st.divider()
    st.markdown("### Navigation")

    if st.button(f"🏠 {t('dashboard')}", use_container_width=True, key="nav_dash"):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button(f"👶 {t('newborns')}", use_container_width=True, key="nav_nb"):
        st.session_state.page = "newborns"
        st.rerun()

    if st.button(f"➕ {t('register_newborn')}", use_container_width=True, key="nav_reg"):
        st.session_state.page = "register"
        st.rerun()

    if st.button(f"📅 {t('followups')}", use_container_width=True, key="nav_fu"):
        st.session_state.page = "followups"
        st.rerun()

    if st.button(f"🏥 {t('referrals')}", use_container_width=True, key="nav_ref"):
        st.session_state.page = "referrals"
        st.rerun()

    if st.button(f"⚠️ {t('alerts')}", use_container_width=True, key="nav_al"):
        st.session_state.page = "alerts"
        st.rerun()

    if role != "ASHA Worker":
        if st.button(f"📊 {t('research')}", use_container_width=True, key="nav_res"):
            st.session_state.page = "research"
            st.rerun()

        if st.button(f"🧹 {t('data_quality')}", use_container_width=True, key="nav_dq"):
            st.session_state.page = "quality"
            st.rerun()

    if role in ["State Admin", "Super Admin"]:
        if st.button(f"⚙️ {t('administration')}", use_container_width=True, key="nav_admin"):
            st.session_state.page = "admin"
            st.rerun()

    st.divider()
    st.caption("Newborn Health Surveillance System")
    if GOOGLE_TRANSLATE_API_KEY:
        st.success("Google Translate API Connected")
    else:
        st.info("Using Built-in Translations")

# ============================================================
# DASHBOARD PAGE
# ============================================================

def dashboard():
    role = st.session_state.role
    if role == "ASHA Worker":
        greeting = "नमस्कार, Sunita Patil 👋" if st.session_state.language == "mr" else "Welcome, Sunita Patil 👋"
        st.subheader(greeting)
        st.caption("ASHA Worker • Kharadi Village • Haveli Taluka")
    elif role == "Taluka Officer":
        st.subheader("Haveli Taluka")
    elif role == "District Officer":
        st.subheader("Pune District")
    elif role == "State Admin":
        st.subheader("Maharashtra State Level")
    else:
        st.subheader("System Administration")

    role_context = {
        "ASHA Worker": "Community-level newborn monitoring • Kharadi",
        "Taluka Officer": "Taluka-level monitoring • Haveli",
        "District Officer": "District surveillance • Pune",
        "State Admin": "State-wide surveillance • Maharashtra",
        "Super Admin": "System administration & oversight"
    }.get(role, "Newborn health surveillance")

    st.markdown(
        f"""
        <div class="page-hero">
            <div class="hero-kicker">Newborn Health Surveillance</div>
            <div class="hero-title">👶 {t('dashboard')}</div>
            <p class="hero-subtitle">{role_context} · Real-time care overview</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    newborns = st.session_state.newborns
    total = len(newborns)
    attention = len([x for x in newborns if x["status"] in ["Needs Attention", "Urgent"]])
    referrals = len([x for x in newborns if x["referral"]])
    today = len([x for x in newborns if x["next_followup"] <= date.today()])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(t("total_newborns"), total, "👶")
    with c2:
        metric_card(t("today_visits"), today, "📅")
    with c3:
        metric_card(t("needs_attention"), attention, "⚠️")
    with c4:
        metric_card(t("pending_referrals"), referrals, "🏥")

    st.markdown('<div class="section-title">Health Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    status_df = pd.DataFrame({
        "Status": ["Normal", "Needs Attention", "Urgent"],
        "Count": [
            len([x for x in newborns if x["status"] == "Normal"]),
            len([x for x in newborns if x["status"] == "Needs Attention"]),
            len([x for x in newborns if x["status"] == "Urgent"])
        ]
    })

    with col1:
        fig_status = px.pie(
            status_df,
            names="Status",
            values="Count",
            title="Newborn Status Breakdown",
            color="Status",
            color_discrete_map={"Normal": "#10b981", "Needs Attention": "#f59e0b", "Urgent": "#ef4444"}
        )
        st.plotly_chart(style_chart(fig_status), use_container_width=True)

    condition_counter = {}
    for baby in newborns:
        for condition in baby["conditions"]:
            condition_counter[condition] = condition_counter.get(condition, 0) + 1

    condition_df = pd.DataFrame(list(condition_counter.items()), columns=["Condition", "Count"])

    with col2:
        if not condition_df.empty:
            fig_cond = px.bar(
                condition_df,
                x="Condition",
                y="Count",
                title="Condition Distribution",
                color="Count",
                color_continuous_scale="Teal"
            )
            st.plotly_chart(style_chart(fig_cond), use_container_width=True)
        else:
            st.info("No active medical conditions recorded across active cohorts.")

    if role == "ASHA Worker":
        st.markdown('<div class="section-title">Today\'s Priority Actions</div>', unsafe_allow_html=True)
        due = [x for x in newborns if x["next_followup"] <= date.today()]
        if due:
            for baby in due:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2.5, 2, 1])
                    with c1:
                        st.markdown(f"### 👶 {baby['name']}")
                        st.caption(f"ID: {baby['id']} | Village: {baby['village']}")
                    with c2:
                        st.markdown(status_html(baby["status"]), unsafe_allow_html=True)
                    with c3:
                        if st.button("Open Record", key=f"open_dash_{baby['id']}"):
                            st.session_state.selected_baby = baby
                            st.session_state.page = "profile"
                            st.rerun()
        else:
            st.success("No urgent follow-up visits pending for today.")

# ============================================================
# NEWBORN REGISTRY LIST
# ============================================================

def newborn_list():
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="hero-kicker">Patient Registry</div>
            <div class="hero-title">👶 {t('newborns')}</div>
            <p class="hero-subtitle">Search, inspect and triage registered infant health records.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input(f"🔎 {t('search')}", placeholder="Search by name, ID or village...", key="nb_search")
    with col2:
        status_filter = st.selectbox("Filter Status", ["All", "Normal", "Needs Attention", "Urgent"], key="nb_filter")

    data = st.session_state.newborns
    filtered = []
    for baby in data:
        text = f"{baby['name']} {baby['id']} {baby['village']}".lower()
        if search.lower() not in text:
            continue
        if status_filter != "All" and baby["status"] != status_filter:
            continue
        filtered.append(baby)

    st.caption(f"Displaying {len(filtered)} matching infant records")

    for baby in filtered:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.5, 1])
            with c1:
                st.markdown(f"### 👶 {baby['name']}")
                st.caption(f"{baby['id']} • {baby['village']}, {baby['taluka']}")
            with c2:
                st.write(f"**{baby['weight']} kg**")
                st.caption(f"GA: {baby['gestational_age']} wks")
            with c3:
                st.markdown(status_html(baby["status"]), unsafe_allow_html=True)
            with c4:
                if st.button("View", key=f"view_list_{baby['id']}"):
                    st.session_state.selected_baby = baby
                    st.session_state.page = "profile"
                    st.rerun()

# ============================================================
# REGISTER NEWBORN (PERSISTENT FORM WIZARD)
# ============================================================

def register_newborn():
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="hero-kicker">New Patient Registration</div>
            <div class="hero-title">➕ {t('register_newborn')}</div>
            <p class="hero-subtitle">Capture complete birth demographics, physical indicators, and referral criteria.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    steps = [
        "1. Birth Details",
        "2. Mother Details",
        "3. Assessment",
        "4. Conditions",
        "5. Referral",
        "6. Review"
    ]

    selected_step = st.radio(
        "Workflow Step",
        steps,
        index=steps.index(st.session_state.registration_step),
        horizontal=True,
        key="reg_step_selector"
    )
    st.session_state.registration_step = selected_step

    # Step 1: Birth Details
    if selected_step.startswith("1"):
        st.subheader(f"1️⃣ {t('birth_details')}")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(t("newborn_name"), key="reg_name")
            st.date_input(t("date_of_birth"), key="reg_dob")
            st.time_input(t("time_of_birth"), key="reg_time")
            st.selectbox(t("sex"), [t("male"), t("female"), t("other")], key="reg_sex")
        with col2:
            st.number_input(t("birth_weight"), min_value=0.5, max_value=6.0, step=0.1, key="reg_weight")
            st.number_input(t("gestational_age"), min_value=20, max_value=45, key="reg_gestational_age")
            st.selectbox(t("place_of_birth"), ["PHC", "CHC", "District Hospital", "Private Hospital", "Home", "Other"], key="reg_place")
            st.selectbox(t("delivery_type"), ["Normal", "C-Section", "Assisted"], key="reg_delivery")

        c_dist, c_tal, c_vil = st.columns(3)
        with c_dist:
            st.selectbox(t("district"), ["Pune", "Mumbai", "Nagpur", "Nashik", "Other"], key="reg_district")
        with c_tal:
            st.selectbox(t("taluka"), ["Haveli", "Mulshi", "Maval", "Khed", "Other"], key="reg_taluka")
        with c_vil:
            st.text_input(t("village"), key="reg_village")

        if st.button("Save & Proceed to Mother Details →", type="primary"):
            st.session_state.registration_step = "2. Mother Details"
            st.rerun()

    # Step 2: Mother Details
    elif selected_step.startswith("2"):
        st.subheader(f"2️⃣ {t('mother_details')}")
        st.text_input(t("mother_name"), key="reg_mother_name")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(t("mother_age"), min_value=12, max_value=60, key="reg_mother_age")
        with col2:
            st.text_input(t("phone"), key="reg_phone")
        st.text_area(t("address"), key="reg_address")

        if st.button("Save & Proceed to Assessment →", type="primary"):
            st.session_state.registration_step = "3. Assessment"
            st.rerun()

    # Step 3: Assessment
    elif selected_step.startswith("3"):
        st.subheader(f"3️⃣ {t('newborn_assessment')}")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(t("temperature"), min_value=30.0, max_value=45.0, step=0.1, key="reg_temperature")
            st.radio(t("feeding_difficulty"), [t("no"), t("yes")], horizontal=True, key="reg_feeding")
            st.radio(t("breathing_difficulty"), [t("no"), t("yes")], horizontal=True, key="reg_breathing")
        with col2:
            st.radio(t("jaundice_observed"), [t("no"), t("yes")], horizontal=True, key="reg_jaundice")
            st.radio("Breastfeeding initiated?", [t("yes"), t("no")], horizontal=True, key="reg_breastfeeding")
            st.radio("Danger signs observed?", [t("no"), t("yes")], horizontal=True, key="reg_danger_signs")

        if st.button("Save & Proceed to Conditions →", type="primary"):
            st.session_state.registration_step = "4. Conditions"
            st.rerun()

    # Step 4: Conditions
    elif selected_step.startswith("4"):
        st.subheader(f"4️⃣ {t('conditions')}")
        condition_options = [
            "Jaundice", "Low Birth Weight", "Prematurity",
            "Feeding Difficulty", "Respiratory Problem",
            "Suspected Infection", "Hypothermia", "Convulsions",
            "Birth Defect", "Other"
        ]
        st.multiselect("Select observed or suspected conditions", condition_options, key="reg_conditions")
        st.info("Field entries flag observations. Clinical diagnosis must be confirmed by an authorized medical officer.")

        if st.session_state.reg_conditions:
            for cond in st.session_state.reg_conditions:
                with st.expander(f"🩺 {cond} - Details"):
                    st.selectbox("Clinical Status", ["Observed", "Suspected", "Clinically Confirmed", "Resolved"], key=f"cond_status_{cond}")
                    st.text_area("Observations / Remarks", key=f"cond_rem_{cond}")

        if st.button("Save & Proceed to Referral →", type="primary"):
            st.session_state.registration_step = "5. Referral"
            st.rerun()

    # Step 5: Referral
    elif selected_step.startswith("5"):
        st.subheader(f"5️⃣ {t('referral_details')}")
        st.radio("Is a health facility referral required?", ["No", "Yes"], horizontal=True, key="reg_referral")

        if st.session_state.reg_referral == "Yes":
            st.selectbox("Referral Destination", ["Nearest PHC", "CHC", "District Hospital", "Medical College Hospital", "Private Hospital"], key="reg_facility")
            st.text_area("Reason for Facility Referral", key="reg_reason")
            st.radio("Emergency Transport Arranged?", ["Yes", "No"], horizontal=True, key="reg_transport")

        if st.button("Proceed to Final Review →", type="primary"):
            st.session_state.registration_step = "6. Review"
            st.rerun()

    # Step 6: Review & Final Submission
    elif selected_step.startswith("6"):
        st.subheader("6️⃣ Review & Final Submission")
        st.write("Review collected health parameters before formal registry commit.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Infant Demographics")
            st.write(f"**Name:** {st.session_state.reg_name or 'Unregistered'}")
            st.write(f"**DOB:** {st.session_state.reg_dob} ({st.session_state.reg_time})")
            st.write(f"**Weight:** {st.session_state.reg_weight} kg")
            st.write(f"**Gestational Age:** {st.session_state.reg_gestational_age} weeks")
            st.write(f"**Sex:** {st.session_state.reg_sex}")
        with col2:
            st.markdown("### Administrative Details")
            st.write(f"**Mother:** {st.session_state.reg_mother_name or 'N/A'}")
            st.write(f"**Phone:** {st.session_state.reg_phone or 'N/A'}")
            st.write(f"**Location:** {st.session_state.reg_village or 'N/A'}, {st.session_state.reg_taluka}, {st.session_state.reg_district}")
            st.write(f"**Referral Required:** {st.session_state.reg_referral}")

        st.markdown("### Clinical Indicators")
        st.write(f"**Selected Conditions:** {', '.join(st.session_state.reg_conditions) if st.session_state.reg_conditions else 'None'}")

        if st.button(f"✓ {t('submit')} Record", type="primary", key="btn_final_submit"):
            conditions = st.session_state.reg_conditions
            weight = float(st.session_state.reg_weight)
            gestational_age = int(st.session_state.reg_gestational_age)
            status = calculate_status(weight, gestational_age, conditions)
            is_referral = st.session_state.reg_referral == "Yes"

            new_baby = {
                "id": generate_newborn_id(),
                "name": st.session_state.reg_name if st.session_state.reg_name else "Unknown",
                "dob": st.session_state.reg_dob,
                "sex": st.session_state.reg_sex,
                "weight": weight,
                "gestational_age": gestational_age,
                "village": st.session_state.reg_village if st.session_state.reg_village else "Unknown",
                "taluka": st.session_state.reg_taluka,
                "district": st.session_state.reg_district,
                "asha": "Sunita Patil",
                "status": status,
                "conditions": conditions,
                "next_followup": date.today() + timedelta(days=3),
                "referral": is_referral
            }

            st.session_state.newborns.append(new_baby)
            st.success(f"{t('register_success')} Generated ID: **{new_baby['id']}**")

            # Reset wizard values
            init_registration_fields()
            st.session_state.registration_step = "1. Birth Details"
            if st.button("View Registered Profile"):
                st.session_state.selected_baby = new_baby
                st.session_state.page = "profile"
                st.rerun()

# ============================================================
# NEWBORN PROFILE (DETAILED VIEW)
# ============================================================

def newborn_profile():
    baby = st.session_state.get("selected_baby")
    if not baby:
        st.warning("No newborn record selected.")
        if st.button("← Return to Registry"):
            st.session_state.page = "newborns"
            st.rerun()
        return

    st.title(f"👶 {baby['name']}")
    st.caption(f"ID: {baby['id']} • Registered by ASHA {baby['asha']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Birth Weight", f"{baby['weight']} kg")
    with col2:
        st.metric("Gestational Age", f"{baby['gestational_age']} weeks")
    with col3:
        st.markdown(f"**Current Triage Status:**<br>{status_html(baby['status'])}", unsafe_allow_html=True)

    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs([
        "👶 Overview",
        "🩺 Conditions",
        "📅 Follow-up Schedule",
        "🏥 Facility Referral"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(t("birth_details"))
            st.write(f"**Full Name:** {baby['name']}")
            st.write(f"**Date of Birth:** {baby['dob']}")
            st.write(f"**Biological Sex:** {baby['sex']}")
            st.write(f"**Birth Weight:** {baby['weight']} kg")
        with c2:
            st.subheader("Administrative Location")
            st.write(f"**Village:** {baby['village']}")
            st.write(f"**Taluka:** {baby['taluka']}")
            st.write(f"**District:** {baby['district']}")
            st.write(f"**Assigned ASHA Worker:** {baby['asha']}")

    with tab2:
        st.subheader(t("conditions"))
        if baby["conditions"]:
            for cond in baby["conditions"]:
                st.warning(f"🩺 **Flagged Condition:** {cond}")
        else:
            st.success("No chronic or acute conditions flagged during intake.")

    with tab3:
        st.subheader(t("followup_schedule"))
        visit_days = [3, 7, 14, 21, 28, 42]
        for day in visit_days:
            visit_date = baby["dob"] + timedelta(days=day)
            if visit_date < date.today():
                v_status, icon = "Completed", "✅"
            elif visit_date == date.today():
                v_status, icon = "Due Today", "🟡"
            else:
                v_status, icon = "Upcoming", "○"

            col_a, col_b, col_c = st.columns([1, 2, 2])
            with col_a:
                st.write(f"{icon} Day {day}")
            with col_b:
                st.write(f"{visit_date}")
            with col_c:
                st.write(f"**{v_status}**")

    with tab4:
        st.subheader(t("referral_details"))
        if baby["referral"]:
            st.error("🚨 Formal referral required / under review.")
            st.write("**Referral Status:** Pending clinical acceptance")
            st.write("**Target Facility:** District Hospital, Pune")
        else:
            st.success("No active hospital referrals indicated.")

    if st.button("← Back to Registry", key="btn_back_profile"):
        st.session_state.page = "newborns"
        st.rerun()

# ============================================================
# FOLLOW-UPS PAGE
# ============================================================

def followup_page():
    st.title(f"📅 {t('followups')}")
    today = date.today()
    due = [x for x in st.session_state.newborns if x["next_followup"] <= today]
    upcoming = [x for x in st.session_state.newborns if x["next_followup"] > today]

    st.metric(t("pending_followups"), len(due))

    st.subheader("Due or Overdue Visits")
    if due:
        for baby in due:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.write(f"👶 **{baby['name']}**")
                    st.caption(f"{baby['id']} • {baby['village']}")
                with c2:
                    st.markdown(status_html(baby["status"]), unsafe_allow_html=True)
                with c3:
                    if st.button("View", key=f"fu_view_{baby['id']}"):
                        st.session_state.selected_baby = baby
                        st.session_state.page = "profile"
                        st.rerun()
    else:
        st.success("All follow-up schedules are currently up to date.")

    st.subheader("Upcoming Schedules")
    for baby in upcoming:
        st.write(f"👶 **{baby['name']}** — Next Visit: `{baby['next_followup']}` ({baby['village']})")

# ============================================================
# REFERRALS PAGE
# ============================================================

def referrals_page():
    st.title(f"🏥 {t('referrals')}")
    referrals = [x for x in st.session_state.newborns if x["referral"]]

    if not referrals:
        st.success("No pending newborn facility referrals.")
        return

    for baby in referrals:
        with st.container(border=True):
            st.markdown(f"### 👶 {baby['name']} (ID: {baby['id']})")
            st.caption(f"Location: {baby['village']} • Status: {baby['status']}")
            st.error("Hospital referral dispatch active.")

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox(
                    "Designated Transfer Facility",
                    ["Nearest PHC", "CHC", "District Hospital", "Medical College Hospital"],
                    key=f"fac_sel_{baby['id']}"
                )
            with col2:
                st.selectbox(
                    "Transfer & Triage Status",
                    ["Pending", "Transport Arranged", "Reached Facility", "Discharged"],
                    key=f"ref_stat_{baby['id']}"
                )

# ============================================================
# ALERTS PAGE
# ============================================================

def alerts_page():
    st.title(f"⚠️ {t('alerts')}")
    urgent = [x for x in st.session_state.newborns if x["status"] == "Urgent"]
    attention = [x for x in st.session_state.newborns if x["status"] == "Needs Attention"]

    st.subheader("🔴 Urgent Interventions Required")
    if urgent:
        for baby in urgent:
            conds = ", ".join(baby["conditions"]) if baby["conditions"] else "Critical weight / GA"
            st.error(f"**{baby['name']}** ({baby['id']}) — Flagged: {conds}")
    else:
        st.success("No urgent danger-sign cases currently active.")

    st.subheader("🟡 Needs Clinical Attention")
    if attention:
        for baby in attention:
            conds = ", ".join(baby["conditions"]) if baby["conditions"] else "Observation criteria met"
            st.warning(f"**{baby['name']}** ({baby['id']}) — Flagged: {conds}")
    else:
        st.info("No intermediate-risk cases currently active.")

# ============================================================
# RESEARCH / ANALYTICS
# ============================================================

def research_page():
    st.title(f"📊 {t('research')}")
    newborns = st.session_state.newborns
    df = pd.DataFrame(newborns)

    if df.empty:
        st.info("No cohort records available for analytical breakdown.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records Analyzed", len(df))
    with col2:
        st.metric("Mean Birth Weight", f"{df['weight'].mean():.2f} kg")
    with col3:
        st.metric("Mean Gestational Age", f"{df['gestational_age'].mean():.1f} wks")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        village_df = df.groupby("village").size().reset_index(name="Newborns")
        fig_v = px.bar(village_df, x="village", y="Newborns", title="Recorded Births by Village")
        st.plotly_chart(style_chart(fig_v), use_container_width=True)

    with col2:
        fig_w = px.histogram(df, x="weight", nbins=10, title="Birth Weight Distribution (kg)")
        st.plotly_chart(style_chart(fig_w), use_container_width=True)

    st.subheader("Cohort Morbidity Summary")
    condition_counter = {}
    for baby in newborns:
        for c in baby["conditions"]:
            condition_counter[c] = condition_counter.get(c, 0) + 1

    if condition_counter:
        cdf = pd.DataFrame(list(condition_counter.items()), columns=["Condition", "Count"])
        fig_c = px.bar(cdf, x="Condition", y="Count", title="Conditions Documented in Cohort", color="Count")
        st.plotly_chart(style_chart(fig_c), use_container_width=True)
    else:
        st.info("No conditions recorded across analyzed cohort.")

# ============================================================
# DATA QUALITY
# ============================================================

def data_quality_page():
    st.title(f"🧹 {t('data_quality')}")
    newborns = st.session_state.newborns

    missing_weight = [x for x in newborns if not x.get("weight")]
    missing_village = [x for x in newborns if not x.get("village") or x.get("village") == "Unknown"]
    pending_followup = [x for x in newborns if x["next_followup"] <= date.today()]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Incomplete Weights", len(missing_weight))
    with c2:
        st.metric("Unmapped Villages", len(missing_village))
    with c3:
        st.metric("Overdue Follow-ups", len(pending_followup))
    with c4:
        st.metric("Duplicate Entries", 0)

    st.divider()
    st.subheader("Data Validation Rules Engine")
    rules = pd.DataFrame({
        "Rule Description": [
            "Mandatory birth weight record",
            "Valid administrative village mapping",
            "Exact date of birth verification",
            "ASHA worker assignment active",
            "Sequential follow-up calendar assigned"
        ],
        "Enforcement": ["Active", "Active", "Active", "Active", "Active"],
        "Health Score": ["100%", "92%", "100%", "100%", "98%"]
    })
    st.dataframe(rules, use_container_width=True, hide_index=True)

# ============================================================
# ADMINISTRATION
# ============================================================

def admin_page():
    st.title(f"⚙️ {t('administration')}")
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Users",
        "🗺️ Geography",
        "🩺 Condition Master",
        "🔐 Audit Trail"
    ])

    with tab1:
        st.subheader("System Operator Directory")
        users = pd.DataFrame({
            "Name": ["Sunita Patil", "Rajesh More", "Priya Kulkarni", "State Admin"],
            "Role": ["ASHA Worker", "Taluka Officer", "District Officer", "State Admin"],
            "Territory": ["Kharadi", "Haveli", "Pune", "Maharashtra"],
            "Status": ["Active", "Active", "Active", "Active"]
        })
        st.dataframe(users, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Administrative Hierarchy")
        st.code(
            """
            Maharashtra State
            └── Pune Division
                └── Pune District
                    └── Haveli Taluka
                        ├── Kharadi Village
                        ├── Wagholi Village
                        └── Manjari Village
            """,
            language="text"
        )

    with tab3:
        st.subheader("Diagnostic Condition Catalog")
        conditions = pd.DataFrame({
            "Condition": [
                "Jaundice", "Low Birth Weight", "Prematurity",
                "Feeding Difficulty", "Respiratory Problem",
                "Suspected Infection", "Hypothermia", "Convulsions"
            ],
            "Risk Tier": ["Medium", "High", "Critical", "Medium", "Critical", "Critical", "High", "Critical"],
            "Surveillance Active": [True] * 8
        })
        st.dataframe(conditions, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Access & Modification Audit")
        audit = pd.DataFrame({
            "Timestamp": ["2026-09-22 10:20", "2026-09-22 11:05", "2026-09-22 12:30"],
            "Operator": ["Sunita Patil", "Rajesh More", "Priya Kulkarni"],
            "Action": ["Newborn Registered", "Referral Updated", "Record Profile Viewed"],
            "Target ID": ["NB-2026-001", "NB-2026-003", "NB-2026-002"]
        })
        st.dataframe(audit, use_container_width=True, hide_index=True)

# ============================================================
# PAGE ROUTER
# ============================================================

current_page = st.session_state.page

if current_page == "dashboard":
    dashboard()
elif current_page == "newborns":
    newborn_list()
elif current_page == "register":
    register_newborn()
elif current_page == "profile":
    newborn_profile()
elif current_page == "followups":
    followup_page()
elif current_page == "referrals":
    referrals_page()
elif current_page == "alerts":
    alerts_page()
elif current_page == "research":
    research_page()
elif current_page == "quality":
    data_quality_page()
elif current_page == "admin":
    admin_page()
else:
    dashboard()

st.markdown(
    """
    <div style="margin-top:40px;padding:16px 20px;border-top:1px solid #e2e8f0;
                color:#64748b;font-size:12px;display:flex;justify-content:space-between;">
        <span>👶 Newborn Health Surveillance System</span>
        <span>Standard Operating Environment · Pune District</span>
    </div>
    """,
    unsafe_allow_html=True
)