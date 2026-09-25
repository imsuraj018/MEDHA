import os
import uuid
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
st.set_page_config(page_title='Newborn Health Surveillance', page_icon='👶', layout='wide', initial_sidebar_state='expanded')
st.markdown('\n    <style>\n\n    .main {\n        background-color: #f7f9fc;\n    }\n\n    .block-container {\n        padding-top: 1.5rem;\n        padding-bottom: 3rem;\n    }\n\n    .dashboard-card {\n        padding: 20px;\n        border-radius: 14px;\n        background: white;\n        border: 1px solid #e5e7eb;\n        box-shadow: 0 2px 8px rgba(0,0,0,0.04);\n        min-height: 130px;\n    }\n\n    .dashboard-card h4 {\n        margin-bottom: 8px;\n        font-size: 15px;\n    }\n\n    .dashboard-number {\n        font-size: 30px;\n        font-weight: 700;\n    }\n\n    .status-normal {\n        background: #dcfce7;\n        color: #166534;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-warning {\n        background: #fef3c7;\n        color: #92400e;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-danger {\n        background: #fee2e2;\n        color: #991b1b;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-info {\n        background: #dbeafe;\n        color: #1e40af;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .section-title {\n        font-size: 21px;\n        font-weight: 700;\n        margin-top: 20px;\n        margin-bottom: 15px;\n    }\n\n    .baby-header {\n        background: white;\n        border-radius: 15px;\n        padding: 25px;\n        border: 1px solid #e5e7eb;\n        margin-bottom: 20px;\n    }\n\n    .small-text {\n        color: #6b7280;\n        font-size: 13px;\n    }\n\n    div[data-testid="stMetric"] {\n        background-color: white;\n        padding: 15px;\n        border-radius: 12px;\n        border: 1px solid #e5e7eb;\n    }\n\n    </style>\n    ', unsafe_allow_html=True)
TRANSLATIONS = {'app_title': {'en': 'Newborn Health Surveillance', 'mr': 'नवजात आरोग्य निरीक्षण प्रणाली', 'hi': 'नवजात स्वास्थ्य निगरानी प्रणाली'}, 'dashboard': {'en': 'Dashboard', 'mr': 'डॅशबोर्ड', 'hi': 'डैशबोर्ड'}, 'newborns': {'en': 'Newborns', 'mr': 'नवजात बाळे', 'hi': 'नवजात शिशु'}, 'register_newborn': {'en': 'Register Newborn', 'mr': 'नवजात बाळाची नोंदणी', 'hi': 'नवजात शिशु का पंजीकरण'}, 'followups': {'en': 'Follow-ups', 'mr': 'पाठपुरावा', 'hi': 'फॉलो-अप'}, 'referrals': {'en': 'Referrals', 'mr': 'रेफरल', 'hi': 'रेफरल'}, 'alerts': {'en': 'Alerts', 'mr': 'सूचना', 'hi': 'अलर्ट'}, 'reports': {'en': 'Reports', 'mr': 'अहवाल', 'hi': 'रिपोर्ट'}, 'data_quality': {'en': 'Data Quality', 'mr': 'डेटा गुणवत्ता', 'hi': 'डेटा गुणवत्ता'}, 'research': {'en': 'Research & Analytics', 'mr': 'संशोधन आणि विश्लेषण', 'hi': 'अनुसंधान और विश्लेषण'}, 'administration': {'en': 'Administration', 'mr': 'प्रशासन', 'hi': 'प्रशासन'}, 'settings': {'en': 'Settings', 'mr': 'सेटिंग्ज', 'hi': 'सेटिंग्स'}, 'language': {'en': 'Language', 'mr': 'भाषा', 'hi': 'भाषा'}, 'role': {'en': 'Role', 'mr': 'भूमिका', 'hi': 'भूमिका'}, 'asha_worker': {'en': 'ASHA Worker', 'mr': 'आशा कार्यकर्ता', 'hi': 'आशा कार्यकर्ता'}, 'taluka_officer': {'en': 'Taluka Officer', 'mr': 'तालुका अधिकारी', 'hi': 'तालुका अधिकारी'}, 'district_officer': {'en': 'District Officer', 'mr': 'जिल्हा अधिकारी', 'hi': 'जिला अधिकारी'}, 'state_admin': {'en': 'State Admin', 'mr': 'राज्य प्रशासक', 'hi': 'राज्य प्रशासक'}, 'super_admin': {'en': 'Super Admin', 'mr': 'सुपर प्रशासक', 'hi': 'सुपर एडमिन'}, 'total_newborns': {'en': 'Total Newborns', 'mr': 'एकूण नवजात बाळे', 'hi': 'कुल नवजात शिशु'}, 'today_visits': {'en': "Today's Visits", 'mr': 'आजच्या भेटी', 'hi': 'आज की मुलाकातें'}, 'pending_followups': {'en': 'Pending Follow-ups', 'mr': 'प्रलंबित पाठपुरावा', 'hi': 'लंबित फॉलो-अप'}, 'pending_referrals': {'en': 'Pending Referrals', 'mr': 'प्रलंबित रेफरल', 'hi': 'लंबित रेफरल'}, 'needs_attention': {'en': 'Needs Attention', 'mr': 'लक्ष देणे आवश्यक', 'hi': 'ध्यान आवश्यक'}, 'birth_details': {'en': 'Birth Details', 'mr': 'जन्माची माहिती', 'hi': 'जन्म विवरण'}, 'mother_details': {'en': 'Mother Details', 'mr': 'आईची माहिती', 'hi': 'माता की जानकारी'}, 'newborn_assessment': {'en': 'Newborn Assessment', 'mr': 'नवजात तपासणी', 'hi': 'नवजात मूल्यांकन'}, 'conditions': {'en': 'Conditions', 'mr': 'आरोग्य स्थिती', 'hi': 'स्वास्थ्य स्थितियां'}, 'referral_details': {'en': 'Referral Details', 'mr': 'रेफरल माहिती', 'hi': 'रेफरल विवरण'}, 'followup_schedule': {'en': 'Follow-up Schedule', 'mr': 'पाठपुरावा वेळापत्रक', 'hi': 'फॉलो-अप अनुसूची'}, 'newborn_name': {'en': 'Newborn Name', 'mr': 'नवजात बाळाचे नाव', 'hi': 'नवजात शिशु का नाम'}, 'date_of_birth': {'en': 'Date of Birth', 'mr': 'जन्म तारीख', 'hi': 'जन्म तिथि'}, 'time_of_birth': {'en': 'Time of Birth', 'mr': 'जन्माची वेळ', 'hi': 'जन्म का समय'}, 'sex': {'en': 'Sex', 'mr': 'लिंग', 'hi': 'लिंग'}, 'male': {'en': 'Male', 'mr': 'मुलगा', 'hi': 'लड़का'}, 'female': {'en': 'Female', 'mr': 'मुलगी', 'hi': 'लड़की'}, 'other': {'en': 'Other', 'mr': 'इतर', 'hi': 'अन्य'}, 'birth_weight': {'en': 'Birth Weight (kg)', 'mr': 'जन्म वजन (किलो)', 'hi': 'जन्म वजन (किलो)'}, 'gestational_age': {'en': 'Gestational Age (weeks)', 'mr': 'गर्भधारणेचे वय (आठवडे)', 'hi': 'गर्भकालीन आयु (सप्ताह)'}, 'place_of_birth': {'en': 'Place of Birth', 'mr': 'जन्माचे ठिकाण', 'hi': 'जन्म स्थान'}, 'delivery_type': {'en': 'Delivery Type', 'mr': 'प्रसूतीचा प्रकार', 'hi': 'प्रसव का प्रकार'}, 'mother_name': {'en': "Mother's Name", 'mr': 'आईचे नाव', 'hi': 'माता का नाम'}, 'mother_age': {'en': "Mother's Age", 'mr': 'आईचे वय', 'hi': 'माता की आयु'}, 'phone': {'en': 'Phone Number', 'mr': 'फोन नंबर', 'hi': 'फोन नंबर'}, 'address': {'en': 'Address', 'mr': 'पत्ता', 'hi': 'पता'}, 'village': {'en': 'Village', 'mr': 'गाव', 'hi': 'गांव'}, 'taluka': {'en': 'Taluka', 'mr': 'तालुका', 'hi': 'तालुका'}, 'district': {'en': 'District', 'mr': 'जिल्हा', 'hi': 'जिला'}, 'temperature': {'en': 'Temperature (°C)', 'mr': 'तापमान (°C)', 'hi': 'तापमान (°C)'}, 'feeding_difficulty': {'en': 'Feeding Difficulty', 'mr': 'दूध पिण्यात अडचण', 'hi': 'दूध पीने में कठिनाई'}, 'breathing_difficulty': {'en': 'Breathing Difficulty', 'mr': 'श्वास घेण्यास त्रास', 'hi': 'सांस लेने में कठिनाई'}, 'jaundice_observed': {'en': 'Jaundice Observed', 'mr': 'कावीळ दिसून आली', 'hi': 'पीलिया देखा गया'}, 'yes': {'en': 'Yes', 'mr': 'होय', 'hi': 'हाँ'}, 'no': {'en': 'No', 'mr': 'नाही', 'hi': 'नहीं'}, 'submit': {'en': 'Submit', 'mr': 'सबमिट करा', 'hi': 'सबमिट करें'}, 'save': {'en': 'Save', 'mr': 'जतन करा', 'hi': 'सहेजें'}, 'search': {'en': 'Search', 'mr': 'शोधा', 'hi': 'खोजें'}, 'status': {'en': 'Status', 'mr': 'स्थिती', 'hi': 'स्थिति'}, 'normal': {'en': 'Normal', 'mr': 'सामान्य', 'hi': 'सामान्य'}, 'attention': {'en': 'Needs Attention', 'mr': 'लक्ष देणे आवश्यक', 'hi': 'ध्यान आवश्यक'}, 'urgent': {'en': 'Urgent', 'mr': 'तातडीचे', 'hi': 'तत्काल'}, 'referred': {'en': 'Referred', 'mr': 'रेफर केले', 'hi': 'रेफर किया गया'}, 'pending': {'en': 'Pending', 'mr': 'प्रलंबित', 'hi': 'लंबित'}, 'register_success': {'en': 'Newborn registered successfully.', 'mr': 'नवजात बाळाची नोंदणी यशस्वी झाली.', 'hi': 'नवजात शिशु का पंजीकरण सफल रहा।'}}
LANGUAGES = {'English': 'en', 'मराठी': 'mr', 'हिन्दी': 'hi'}

def local_translate(key, language):
    """Translate fixed UI terminology."""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(language, TRANSLATIONS[key]['en'])
    return key

@st.cache_data(show_spinner=False)
def google_translate(text, target_language, source_language='en'):
    if not text:
        return ''
    if target_language == source_language:
        return text
    if not GOOGLE_TRANSLATE_API_KEY:
        return text
    url = 'https://translation.googleapis.com/language/translate/v2'
    params = {'key': GOOGLE_TRANSLATE_API_KEY}
    data = {'q': text, 'source': source_language, 'target': target_language, 'format': 'text'}
    try:
        response = requests.post(url, params=params, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result['data']['translations'][0]['translatedText']
    except Exception:
        return text

def dynamic_translate(text, language):
    if language == 'en':
        return text
    return google_translate(text, language, 'en')
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'role' not in st.session_state:
    st.session_state.role = 'ASHA Worker'
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'newborns' not in st.session_state:
    st.session_state.newborns = [{'id': 'NB-2026-001', 'name': 'Aarav Sharma', 'dob': date(2026, 9, 10), 'sex': 'Male', 'weight': 2.4, 'gestational_age': 38, 'village': 'Kharadi', 'taluka': 'Haveli', 'district': 'Pune', 'asha': 'Sunita Patil', 'status': 'Needs Attention', 'conditions': ['Jaundice', 'Low Birth Weight'], 'next_followup': date.today(), 'referral': True}, {'id': 'NB-2026-002', 'name': 'Anaya Joshi', 'dob': date(2026, 9, 12), 'sex': 'Female', 'weight': 3.1, 'gestational_age': 39, 'village': 'Wagholi', 'taluka': 'Haveli', 'district': 'Pune', 'asha': 'Sunita Patil', 'status': 'Normal', 'conditions': [], 'next_followup': date.today() + timedelta(days=2), 'referral': False}, {'id': 'NB-2026-003', 'name': 'Vihaan Patil', 'dob': date(2026, 9, 5), 'sex': 'Male', 'weight': 1.9, 'gestational_age': 35, 'village': 'Manjari', 'taluka': 'Haveli', 'district': 'Pune', 'asha': 'Sunita Patil', 'status': 'Urgent', 'conditions': ['Prematurity', 'Low Birth Weight', 'Feeding Difficulty'], 'next_followup': date.today(), 'referral': True}, {'id': 'NB-2026-004', 'name': 'Ishita Deshmukh', 'dob': date(2026, 9, 14), 'sex': 'Female', 'weight': 2.9, 'gestational_age': 39, 'village': 'Hadapsar', 'taluka': 'Haveli', 'district': 'Pune', 'asha': 'Sunita Patil', 'status': 'Normal', 'conditions': [], 'next_followup': date.today() + timedelta(days=4), 'referral': False}]

def t(key):
    return local_translate(key, st.session_state.language)


def ui_text(text):
    """Translate arbitrary user-visible UI text.

    Fixed terminology uses the controlled translation dictionary first.
    Remaining English UI text uses Google Cloud Translation and is cached.
    Choice widgets use this function as format_func, so their underlying
    stored values remain stable English codes/values.
    """
    if text is None:
        return text
    text = str(text)
    if not text.strip():
        return text

    language = st.session_state.get("language", "en")
    if language == "en":
        return text

    # Don't send emoji/punctuation-only strings to Google.
    if not any(ch.isalpha() for ch in text):
        return text

    # Language names are labels, not translatable content.
    if text in LANGUAGES:
        return text

    # Avoid translating text that is already the selected-language value.
    for values in TRANSLATIONS.values():
        if text == values.get(language):
            return text

    # Prefer controlled translations for medical/public-health terminology.
    for values in TRANSLATIONS.values():
        if text == values.get("en"):
            return values.get(language, text)

    return google_translate(text, language, "en")

def status_html(status):
    if status == 'Normal':
        return '<span class="status-normal">🟢 Normal</span>'
    if status == 'Needs Attention':
        return '<span class="status-warning">🟡 Needs Attention</span>'
    if status == 'Urgent':
        return '<span class="status-danger">🔴 Urgent</span>'
    if status == 'Referred':
        return '<span class="status-info">🔵 Referred</span>'
    return status

def generate_newborn_id():
    return f'NB-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}'

def calculate_status(weight, gestational_age, conditions):
    risk_conditions = {'Jaundice', 'Low Birth Weight', 'Prematurity', 'Respiratory Problem', 'Feeding Difficulty', 'Suspected Infection', 'Hypothermia', 'Convulsions'}
    risk_count = len(set(conditions).intersection(risk_conditions))
    if weight < 2.0 or gestational_age < 37:
        return 'Urgent'
    if risk_count >= 2:
        return 'Urgent'
    if risk_count == 1:
        return 'Needs Attention'
    return 'Normal'

def metric_card(title, value, icon):
    st.markdown(f'\n        <div class="dashboard-card">\n            <h4>{icon} {title}</h4>\n            <div class="dashboard-number">{value}</div>\n        </div>\n        ', unsafe_allow_html=True)
with st.sidebar:
    st.markdown(f"\n        <h2>👶 {t('app_title')}</h2>\n        ", unsafe_allow_html=True)
    st.divider()
    selected_language_name = st.selectbox(t('language'), list(LANGUAGES.keys()), index=list(LANGUAGES.values()).index(st.session_state.language), format_func=ui_text)
    st.session_state.language = LANGUAGES[selected_language_name]
    st.divider()
    role_options = ['ASHA Worker', 'Taluka Officer', 'District Officer', 'State Admin', 'Super Admin']
    role = st.selectbox(t('role'), role_options, index=role_options.index(st.session_state.role), format_func=ui_text)
    st.session_state.role = role
    st.divider()
    st.markdown(ui_text('### Navigation'))
    if st.button(f"{ui_text('🏠 ')}{t('dashboard')}", use_container_width=True):
        st.session_state.page = 'dashboard'
    if st.button(f"{ui_text('👶 ')}{t('newborns')}", use_container_width=True):
        st.session_state.page = 'newborns'
    if st.button(f"{ui_text('➕ ')}{t('register_newborn')}", use_container_width=True):
        st.session_state.page = 'register'
    if st.button(f"{ui_text('📅 ')}{t('followups')}", use_container_width=True):
        st.session_state.page = 'followups'
    if st.button(f"{ui_text('🏥 ')}{t('referrals')}", use_container_width=True):
        st.session_state.page = 'referrals'
    if st.button(f"{ui_text('⚠️ ')}{t('alerts')}", use_container_width=True):
        st.session_state.page = 'alerts'
    if role != 'ASHA Worker':
        if st.button(f"{ui_text('📊 ')}{t('research')}", use_container_width=True):
            st.session_state.page = 'research'
        if st.button(f"{ui_text('🧹 ')}{t('data_quality')}", use_container_width=True):
            st.session_state.page = 'quality'
    if role in ['State Admin', 'Super Admin']:
        if st.button(f"{ui_text('⚙️ ')}{t('administration')}", use_container_width=True):
            st.session_state.page = 'admin'
    st.divider()
    st.caption(ui_text('Newborn Health Surveillance Prototype'))
    if GOOGLE_TRANSLATE_API_KEY:
        st.success(ui_text('Google Translation API connected'))
    else:
        st.info(ui_text('Using built-in translations'))

def dashboard():
    st.title(f"{ui_text('👶 ')}{t('dashboard')}")
    role = st.session_state.role
    if role == 'ASHA Worker':
        st.subheader('नमस्कार, Sunita Patil 👋' if st.session_state.language == 'mr' else 'Welcome, Sunita Patil 👋')
        st.caption(ui_text('ASHA Worker • Kharadi Village • Haveli Taluka'))
    elif role == 'Taluka Officer':
        st.subheader(ui_text('Haveli Taluka'))
    elif role == 'District Officer':
        st.subheader(ui_text('Pune District'))
    elif role == 'State Admin':
        st.subheader(ui_text('Maharashtra'))
    else:
        st.subheader(ui_text('System Administration'))
    newborns = st.session_state.newborns
    total = len(newborns)
    attention = len([x for x in newborns if x['status'] in ['Needs Attention', 'Urgent']])
    referrals = len([x for x in newborns if x['referral']])
    today = len([x for x in newborns if x['next_followup'] <= date.today()])
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(t('total_newborns'), total, '👶')
    with c2:
        metric_card(t('today_visits'), today, '📅')
    with c3:
        metric_card(t('needs_attention'), attention, '⚠️')
    with c4:
        metric_card(t('pending_referrals'), referrals, '🏥')
    st.markdown('<div class="section-title">Health Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    status_df = pd.DataFrame({'Status': ['Normal', 'Needs Attention', 'Urgent'], 'Count': [len([x for x in newborns if x['status'] == 'Normal']), len([x for x in newborns if x['status'] == 'Needs Attention']), len([x for x in newborns if x['status'] == 'Urgent'])]})
    with col1:
        fig = px.pie(status_df, names='Status', values='Count', title=ui_text('Newborn Status'))
        st.plotly_chart(fig, use_container_width=True)
    condition_counter = {}
    for baby in newborns:
        for condition in baby['conditions']:
            condition_counter[condition] = condition_counter.get(condition, 0) + 1
    condition_df = pd.DataFrame(list(condition_counter.items()), columns=['Condition', 'Count'])
    with col2:
        if not condition_df.empty:
            fig = px.bar(condition_df, x='Condition', y='Count', title=ui_text('Condition Distribution'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(ui_text('No conditions recorded.'))
    if role == 'ASHA Worker':
        st.markdown('<div class="section-title">Today\'s Priority</div>', unsafe_allow_html=True)
        due = [x for x in newborns if x['next_followup'] <= date.today()]
        if due:
            for baby in due:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"{ui_text('### 👶 ')}{baby['name']}")
                        st.caption(baby['id'])
                    with c2:
                        st.markdown(status_html(baby['status']), unsafe_allow_html=True)
                    with c3:
                        if st.button(ui_text('Open'), key=f"open_{baby['id']}"):
                            st.session_state.selected_baby = baby
                            st.session_state.page = 'profile'
                            st.rerun()
        else:
            st.success(ui_text('No urgent follow-ups for today.'))

def newborn_list():
    st.title(f"{ui_text('👶 ')}{t('newborns')}")
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input(f"{ui_text('🔎 ')}{t('search')}", placeholder=ui_text('Search newborn, ID or village...'))
    with col2:
        status_filter = st.selectbox(ui_text('Status'), ['All', 'Normal', 'Needs Attention', 'Urgent'], format_func=ui_text)
    data = st.session_state.newborns
    filtered = []
    for baby in data:
        text = (baby['name'] + ' ' + baby['id'] + ' ' + baby['village']).lower()
        if search.lower() not in text:
            continue
        if status_filter != 'All' and baby['status'] != status_filter:
            continue
        filtered.append(baby)
    st.caption(f"{len(filtered)}{ui_text(' newborn records')}")
    for baby in filtered:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.5, 1])
            with c1:
                st.markdown(f"{ui_text('### 👶 ')}{baby['name']}")
                st.caption(f"{baby['id']}{ui_text(' • ')}{baby['village']}")
            with c2:
                st.write(f"{ui_text('**')}{baby['weight']}{ui_text(' kg**')}")
                st.caption(ui_text('Birth Weight'))
            with c3:
                st.markdown(status_html(baby['status']), unsafe_allow_html=True)
            with c4:
                if st.button(ui_text('View'), key=f"view_{baby['id']}"):
                    st.session_state.selected_baby = baby
                    st.session_state.page = 'profile'
                    st.rerun()

def register_newborn():
    st.title(f"{ui_text('➕ ')}{t('register_newborn')}")
    st.caption(ui_text('Complete the newborn registration step by step.'))
    step = st.radio(ui_text('Registration Step'), ['1. Birth Details', '2. Mother Details', '3. Assessment', '4. Conditions', '5. Referral', '6. Review'], horizontal=True, format_func=ui_text)
    if 'registration' not in st.session_state:
        st.session_state.registration = {}
    registration = st.session_state.registration
    if step.startswith('1'):
        st.header(f"{ui_text('1️⃣ ')}{t('birth_details')}")
        col1, col2 = st.columns(2)
        with col1:
            registration['name'] = st.text_input(t('newborn_name'), value=registration.get('name', ''))
            registration['dob'] = st.date_input(t('date_of_birth'), value=registration.get('dob', date.today()))
            registration['time'] = st.time_input(t('time_of_birth'))
            registration['sex'] = st.selectbox(t('sex'), [t('male'), t('female'), t('other')], format_func=ui_text)
        with col2:
            registration['weight'] = st.number_input(t('birth_weight'), min_value=0.5, max_value=6.0, value=2.5, step=0.1)
            registration['gestational_age'] = st.number_input(t('gestational_age'), min_value=20, max_value=45, value=38)
            registration['place'] = st.selectbox(t('place_of_birth'), ['Home', 'PHC', 'CHC', 'District Hospital', 'Private Hospital', 'Other'], format_func=ui_text)
            registration['delivery'] = st.selectbox(t('delivery_type'), ['Normal', 'C-Section', 'Assisted'], format_func=ui_text)
        registration['district'] = st.selectbox(t('district'), ['Pune', 'Mumbai', 'Nagpur', 'Nashik', 'Other'], format_func=ui_text)
        registration['taluka'] = st.selectbox(t('taluka'), ['Haveli', 'Mulshi', 'Maval', 'Khed', 'Other'], format_func=ui_text)
        registration['village'] = st.text_input(t('village'))
        if st.button(ui_text('Save & Continue →'), type='primary'):
            st.success(ui_text('Birth details saved.'))
    elif step.startswith('2'):
        st.header(f"{ui_text('2️⃣ ')}{t('mother_details')}")
        registration['mother_name'] = st.text_input(t('mother_name'))
        col1, col2 = st.columns(2)
        with col1:
            registration['mother_age'] = st.number_input(t('mother_age'), min_value=12, max_value=60, value=25)
        with col2:
            registration['phone'] = st.text_input(t('phone'))
        registration['address'] = st.text_area(t('address'))
        if st.button(ui_text('Save & Continue →'), type='primary'):
            st.success(ui_text('Mother details saved.'))
    elif step.startswith('3'):
        st.header(f"{ui_text('3️⃣ ')}{t('newborn_assessment')}")
        col1, col2 = st.columns(2)
        with col1:
            registration['temperature'] = st.number_input(t('temperature'), min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            registration['feeding'] = st.radio(t('feeding_difficulty'), [t('no'), t('yes')], horizontal=True, format_func=ui_text)
            registration['breathing'] = st.radio(t('breathing_difficulty'), [t('no'), t('yes')], horizontal=True, format_func=ui_text)
        with col2:
            registration['jaundice'] = st.radio(t('jaundice_observed'), [t('no'), t('yes')], horizontal=True, format_func=ui_text)
            registration['breastfeeding'] = st.radio(ui_text('Breastfeeding initiated?'), [t('yes'), t('no')], horizontal=True, format_func=ui_text)
            registration['danger_signs'] = st.radio(ui_text('Danger signs observed?'), [t('no'), t('yes')], horizontal=True, format_func=ui_text)
        if st.button(ui_text('Save & Continue →'), type='primary'):
            st.success(ui_text('Assessment saved.'))
    elif step.startswith('4'):
        st.header(f"{ui_text('4️⃣ ')}{t('conditions')}")
        condition_options = ['Jaundice', 'Low Birth Weight', 'Prematurity', 'Feeding Difficulty', 'Respiratory Problem', 'Suspected Infection', 'Hypothermia', 'Convulsions', 'Birth Defect', 'Other']
        registration['conditions'] = st.multiselect(ui_text('Select observed/suspected conditions'), condition_options, format_func=ui_text)
        st.info(ui_text('Important: this section records observations or suspected conditions. Clinical diagnosis should be confirmed by an authorized healthcare professional.'))
        if registration.get('conditions'):
            for condition in registration['conditions']:
                with st.expander(f"{ui_text('🩺 ')}{condition}"):
                    st.selectbox(ui_text('Status'), ['Observed', 'Suspected', 'Clinically Confirmed', 'Resolved'], key=f'condition_status_{condition}', format_func=ui_text)
                    st.text_area(ui_text('Remarks'), key=f'condition_remarks_{condition}')
        if st.button(ui_text('Save & Continue →'), type='primary'):
            st.success(ui_text('Condition information saved.'))
    elif step.startswith('5'):
        st.header(f"{ui_text('5️⃣ ')}{t('referral_details')}")
        referral_required = st.radio(ui_text('Referral required?'), ['No', 'Yes'], horizontal=True, format_func=ui_text)
        registration['referral'] = referral_required == 'Yes'
        if referral_required == 'Yes':
            registration['facility'] = st.selectbox(ui_text('Referral Facility'), ['Nearest PHC', 'CHC', 'District Hospital', 'Medical College Hospital', 'Private Hospital'], format_func=ui_text)
            registration['reason'] = st.text_area(ui_text('Reason for Referral'))
            registration['transport'] = st.radio(ui_text('Transport arranged?'), ['Yes', 'No'], horizontal=True, format_func=ui_text)
        if st.button(ui_text('Save & Continue →'), type='primary'):
            st.success(ui_text('Referral details saved.'))
    elif step.startswith('6'):
        st.header(ui_text('6️⃣ Review & Submit'))
        st.write(ui_text('Review the information before creating the newborn record.'))
        if registration:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(ui_text('### Birth'))
                st.write(f"{ui_text('**Name:** ')}{registration.get('name', '-')}")
                st.write(f"{ui_text('**DOB:** ')}{registration.get('dob', '-')}")
                st.write(f"{ui_text('**Weight:** ')}{registration.get('weight', '-')}{ui_text(' kg')}")
                st.write(f"{ui_text('**Gestational Age:** ')}{registration.get('gestational_age', '-')}")
            with col2:
                st.markdown(ui_text('### Location'))
                st.write(f"{ui_text('**District:** ')}{registration.get('district', '-')}")
                st.write(f"{ui_text('**Taluka:** ')}{registration.get('taluka', '-')}")
                st.write(f"{ui_text('**Village:** ')}{registration.get('village', '-')}")
            st.markdown(ui_text('### Conditions'))
            st.write(registration.get('conditions', []))
            if st.button(f"{ui_text('✓ ')}{t('submit')}", type='primary'):
                conditions = registration.get('conditions', [])
                weight = registration.get('weight', 2.5)
                gestational_age = registration.get('gestational_age', 38)
                status = calculate_status(weight, gestational_age, conditions)
                new_baby = {'id': generate_newborn_id(), 'name': registration.get('name', 'Unknown'), 'dob': registration.get('dob', date.today()), 'sex': registration.get('sex', 'Other'), 'weight': weight, 'gestational_age': gestational_age, 'village': registration.get('village', 'Unknown'), 'taluka': registration.get('taluka', 'Unknown'), 'district': registration.get('district', 'Unknown'), 'asha': 'Sunita Patil', 'status': status, 'conditions': conditions, 'next_followup': date.today() + timedelta(days=3), 'referral': registration.get('referral', False)}
                st.session_state.newborns.append(new_baby)
                st.session_state.registration = {}
                st.success(f"{t('register_success')}{ui_text(' ID: ')}{new_baby['id']}")

def newborn_profile():
    baby = st.session_state.get('selected_baby')
    if not baby:
        st.warning(ui_text('No newborn selected.'))
        return
    st.title(f"{ui_text('👶 ')}{baby['name']}")
    st.caption(baby['id'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(ui_text('Birth Weight'), f"{baby['weight']} kg")
    with col2:
        st.metric(ui_text('Gestational Age'), f"{baby['gestational_age']} weeks")
    with col3:
        st.markdown(status_html(baby['status']), unsafe_allow_html=True)
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(['👶 Overview', '🩺 Conditions', '📅 Follow-up', '🏥 Referral'])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t('birth_details'))
            st.write(f"{ui_text('**Name:** ')}{baby['name']}")
            st.write(f"{ui_text('**DOB:** ')}{baby['dob']}")
            st.write(f"{ui_text('**Sex:** ')}{baby['sex']}")
            st.write(f"{ui_text('**Birth Weight:** ')}{baby['weight']}{ui_text(' kg')}")
        with col2:
            st.subheader(ui_text('Location'))
            st.write(f"{ui_text('**Village:** ')}{baby['village']}")
            st.write(f"{ui_text('**Taluka:** ')}{baby['taluka']}")
            st.write(f"{ui_text('**District:** ')}{baby['district']}")
            st.write(f"{ui_text('**ASHA:** ')}{baby['asha']}")
    with tab2:
        st.subheader(t('conditions'))
        if baby['conditions']:
            for condition in baby['conditions']:
                st.warning(f"{ui_text('🩺 ')}{condition}")
        else:
            st.success(ui_text('No conditions recorded.'))
    with tab3:
        st.subheader(t('followup_schedule'))
        visit_days = [3, 7, 14, 21, 28, 42]
        baby_age = (date.today() - baby['dob']).days
        for day in visit_days:
            visit_date = baby['dob'] + timedelta(days=day)
            if visit_date < date.today():
                status = 'Completed'
                icon = '✅'
            elif visit_date == date.today():
                status = 'Due Today'
                icon = '🟡'
            else:
                status = 'Upcoming'
                icon = '○'
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                st.write(f"{icon}{ui_text(' Day ')}{day}")
            with col2:
                st.write(visit_date)
            with col3:
                st.write(status)
    with tab4:
        st.subheader(t('referral_details'))
        if baby['referral']:
            st.error(ui_text('🏥 Referral required / pending'))
            st.write(ui_text('**Status:** Pending'))
            st.write(ui_text('**Facility:** District Hospital'))
        else:
            st.success(ui_text('No referral currently recorded.'))

def followup_page():
    st.title(f"{ui_text('📅 ')}{t('followups')}")
    today = date.today()
    due = []
    upcoming = []
    for baby in st.session_state.newborns:
        if baby['next_followup'] <= today:
            due.append(baby)
        else:
            upcoming.append(baby)
    st.metric(t('pending_followups'), len(due))
    st.markdown(ui_text('### Due / Overdue'))
    for baby in due:
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"{ui_text('👶 **')}{baby['name']}{ui_text('**')}")
                st.caption(baby['id'])
            with c2:
                st.write(f"{ui_text('Village: ')}{baby['village']}")
            with c3:
                st.error(ui_text('Follow-up Due'))
    st.markdown(ui_text('### Upcoming'))
    for baby in upcoming:
        st.write(f"{ui_text('👶 ')}{baby['name']}{ui_text(' — ')}{baby['next_followup']}")

def referrals_page():
    st.title(f"{ui_text('🏥 ')}{t('referrals')}")
    referrals = [x for x in st.session_state.newborns if x['referral']]
    if not referrals:
        st.success(ui_text('No pending referrals.'))
        return
    for baby in referrals:
        with st.container(border=True):
            st.markdown(f"{ui_text('### 👶 ')}{baby['name']}")
            st.write(f"{ui_text('ID: ')}{baby['id']}")
            st.write(f"{ui_text('Village: ')}{baby['village']}")
            st.error(ui_text('Referral pending'))
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox(ui_text('Referral facility'), ['PHC', 'CHC', 'District Hospital', 'Medical College'], key=f"facility_{baby['id']}", format_func=ui_text)
            with col2:
                st.selectbox(ui_text('Referral status'), ['Pending', 'Transport Arranged', 'Reached Facility', 'Completed'], key=f"refstatus_{baby['id']}", format_func=ui_text)

def alerts_page():
    st.title(f"{ui_text('⚠️ ')}{t('alerts')}")
    urgent = [x for x in st.session_state.newborns if x['status'] == 'Urgent']
    attention = [x for x in st.session_state.newborns if x['status'] == 'Needs Attention']
    st.subheader(ui_text('🔴 Urgent'))
    for baby in urgent:
        st.error(f"{baby['name']}{ui_text(' — ')}{', '.join(baby['conditions'])}")
    st.subheader(ui_text('🟡 Needs Attention'))
    for baby in attention:
        st.warning(f"{baby['name']}{ui_text(' — ')}{', '.join(baby['conditions'])}")

def research_page():
    st.title(f"{ui_text('📊 ')}{t('research')}")
    newborns = st.session_state.newborns
    df = pd.DataFrame(newborns)
    if df.empty:
        st.info(ui_text('No data available.'))
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(ui_text('Total Newborns'), len(df))
    with col2:
        st.metric(ui_text('Average Birth Weight'), f"{df['weight'].mean():.2f} kg")
    with col3:
        st.metric(ui_text('Average Gestational Age'), f"{df['gestational_age'].mean():.1f} weeks")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        village_df = df.groupby('village').size().reset_index(name='Newborns')
        fig = px.bar(village_df, x='village', y='Newborns', title=ui_text('Newborns by Village'))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        weight_df = df[['name', 'weight']]
        fig = px.histogram(weight_df, x='weight', nbins=8, title=ui_text('Birth Weight Distribution'))
        st.plotly_chart(fig, use_container_width=True)
    st.subheader(ui_text('Condition Distribution'))
    condition_counter = {}
    for baby in newborns:
        for condition in baby['conditions']:
            condition_counter[condition] = condition_counter.get(condition, 0) + 1
    if condition_counter:
        condition_df = pd.DataFrame([{'Condition': k, 'Count': v} for k, v in condition_counter.items()])
        fig = px.bar(condition_df, x='Condition', y='Count', title=ui_text('Recorded Conditions'))
        st.plotly_chart(fig, use_container_width=True)

def data_quality_page():
    st.title(f"{ui_text('🧹 ')}{t('data_quality')}")
    newborns = st.session_state.newborns
    missing_weight = [x for x in newborns if not x.get('weight')]
    missing_village = [x for x in newborns if not x.get('village')]
    pending_followup = [x for x in newborns if x['next_followup'] <= date.today()]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(ui_text('Incomplete Weight'), len(missing_weight))
    with c2:
        st.metric(ui_text('Missing Village'), len(missing_village))
    with c3:
        st.metric(ui_text('Follow-up Pending'), len(pending_followup))
    with c4:
        st.metric(ui_text('Possible Duplicates'), 0)
    st.divider()
    st.subheader(ui_text('Data Quality Rules'))
    rules = pd.DataFrame({'Rule': ['Birth weight present', 'Village present', 'Date of birth present', 'ASHA assigned', 'Follow-up scheduled', 'Conditions recorded where applicable'], 'Status': ['✓', '✓', '✓', '✓', '✓', '✓']})
    st.dataframe(rules, use_container_width=True, hide_index=True)

def admin_page():
    st.title(f"{ui_text('⚙️ ')}{t('administration')}")
    tab1, tab2, tab3, tab4 = st.tabs(['👥 Users', '🗺️ Geography', '🩺 Conditions', '🔐 Audit'])
    with tab1:
        st.subheader(ui_text('User Management'))
        users = pd.DataFrame({'User': ['Sunita Patil', 'Rajesh More', 'Priya Kulkarni', 'State Admin'], 'Role': ['ASHA Worker', 'Taluka Officer', 'District Officer', 'State Admin'], 'Location': ['Kharadi', 'Haveli', 'Pune', 'Maharashtra'], 'Status': ['Active', 'Active', 'Active', 'Active']})
        st.dataframe(users, use_container_width=True, hide_index=True)
    with tab2:
        st.subheader(ui_text('Geographic Hierarchy'))
        st.write(ui_text('\n            State\n            └── Division\n                └── District\n                    └── Taluka / Block\n                        └── Village\n                            └── ASHA Worker\n            '))
    with tab3:
        st.subheader(ui_text('Condition Master'))
        conditions = pd.DataFrame({'Condition': ['Jaundice', 'Low Birth Weight', 'Prematurity', 'Feeding Difficulty', 'Respiratory Problem', 'Suspected Infection', 'Hypothermia', 'Convulsions', 'Birth Defect'], 'Active': [True, True, True, True, True, True, True, True, True]})
        st.dataframe(conditions, use_container_width=True, hide_index=True)
    with tab4:
        st.subheader(ui_text('Audit Log'))
        audit = pd.DataFrame({'Date/Time': ['2026-09-22 10:20', '2026-09-22 11:05', '2026-09-22 12:30'], 'User': ['Sunita Patil', 'Rajesh More', 'Priya Kulkarni'], 'Action': ['Newborn Registered', 'Referral Updated', 'Record Viewed'], 'Record': ['NB-2026-001', 'NB-2026-003', 'NB-2026-002']})
        st.dataframe(audit, use_container_width=True, hide_index=True)
page = st.session_state.page
if page == 'dashboard':
    dashboard()
elif page == 'newborns':
    newborn_list()
elif page == 'register':
    register_newborn()
elif page == 'profile':
    newborn_profile()
elif page == 'followups':
    followup_page()
elif page == 'referrals':
    referrals_page()
elif page == 'alerts':
    alerts_page()
elif page == 'research':
    research_page()
elif page == 'quality':
    data_quality_page()
elif page == 'admin':
    admin_page()
else:
    dashboard()
