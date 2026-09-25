import os
import uuid
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import requests
import json
import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)
GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '').strip()
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')
ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'

# Optional OpenAI services used only for voice input/output.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
OPENAI_RESPONSES_URL = 'https://api.openai.com/v1/responses'
OPENAI_TRANSCRIPTION_URL = 'https://api.openai.com/v1/audio/transcriptions'
OPENAI_SPEECH_URL = 'https://api.openai.com/v1/audio/speech'
OPENAI_TRANSCRIPTION_MODEL = os.getenv('OPENAI_TRANSCRIPTION_MODEL', 'gpt-4o-mini-transcribe')
OPENAI_TTS_MODEL = os.getenv('OPENAI_TTS_MODEL', 'gpt-4o-mini-tts')
OPENAI_TTS_VOICE = os.getenv('OPENAI_TTS_VOICE', 'alloy')
st.set_page_config(page_title='Newborn Health Surveillance', page_icon='👶', layout='wide', initial_sidebar_state='expanded')
st.markdown('\n    <style>\n\n    .main {\n        background-color: #f7f9fc;\n    }\n\n    .block-container {\n        padding-top: 1.5rem;\n        padding-bottom: 3rem;\n    }\n\n    .dashboard-card {\n        padding: 20px;\n        border-radius: 14px;\n        background: white;\n        border: 1px solid #e5e7eb;\n        box-shadow: 0 2px 8px rgba(0,0,0,0.04);\n        min-height: 130px;\n    }\n\n    .dashboard-card h4 {\n        margin-bottom: 8px;\n        font-size: 15px;\n    }\n\n    .dashboard-number {\n        font-size: 30px;\n        font-weight: 700;\n    }\n\n    .status-normal {\n        background: #dcfce7;\n        color: #166534;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-warning {\n        background: #fef3c7;\n        color: #92400e;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-danger {\n        background: #fee2e2;\n        color: #991b1b;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .status-info {\n        background: #dbeafe;\n        color: #1e40af;\n        padding: 6px 12px;\n        border-radius: 20px;\n        font-weight: 600;\n    }\n\n    .section-title {\n        font-size: 21px;\n        font-weight: 700;\n        margin-top: 20px;\n        margin-bottom: 15px;\n    }\n\n    .baby-header {\n        background: white;\n        border-radius: 15px;\n        padding: 25px;\n        border: 1px solid #e5e7eb;\n        margin-bottom: 20px;\n    }\n\n    .small-text {\n        color: #6b7280;\n        font-size: 13px;\n    }\n\n    div[data-testid="stMetric"] {\n        background-color: white;\n        padding: 15px;\n        border-radius: 12px;\n        border: 1px solid #e5e7eb;\n    }\n\n    </style>\n    ', unsafe_allow_html=True)
TRANSLATIONS = {'app_title': {'en': 'Newborn Health Surveillance', 'mr': 'नवजात आरोग्य निरीक्षण प्रणाली', 'hi': 'नवजात स्वास्थ्य निगरानी प्रणाली'}, 'dashboard': {'en': 'Dashboard', 'mr': 'डॅशबोर्ड', 'hi': 'डैशबोर्ड'}, 'newborns': {'en': 'Newborns', 'mr': 'नवजात बाळे', 'hi': 'नवजात शिशु'}, 'register_newborn': {'en': 'Register Newborn', 'mr': 'नवजात बाळाची नोंदणी', 'hi': 'नवजात शिशु का पंजीकरण'}, 'followups': {'en': 'Follow-ups', 'mr': 'पाठपुरावा', 'hi': 'फॉलो-अप'}, 'referrals': {'en': 'Referrals', 'mr': 'रेफरल', 'hi': 'रेफरल'}, 'alerts': {'en': 'Alerts', 'mr': 'सूचना', 'hi': 'अलर्ट'}, 'reports': {'en': 'Reports', 'mr': 'अहवाल', 'hi': 'रिपोर्ट'}, 'data_quality': {'en': 'Data Quality', 'mr': 'डेटा गुणवत्ता', 'hi': 'डेटा गुणवत्ता'}, 'research': {'en': 'Research & Analytics', 'mr': 'संशोधन आणि विश्लेषण', 'hi': 'अनुसंधान और विश्लेषण'}, 'administration': {'en': 'Administration', 'mr': 'प्रशासन', 'hi': 'प्रशासन'}, 'settings': {'en': 'Settings', 'mr': 'सेटिंग्ज', 'hi': 'सेटिंग्स'}, 'language': {'en': 'Language', 'mr': 'भाषा', 'hi': 'भाषा'}, 'role': {'en': 'Role', 'mr': 'भूमिका', 'hi': 'भूमिका'}, 'asha_worker': {'en': 'ASHA Worker', 'mr': 'आशा कार्यकर्ता', 'hi': 'आशा कार्यकर्ता'}, 'taluka_officer': {'en': 'Taluka Officer', 'mr': 'तालुका अधिकारी', 'hi': 'तालुका अधिकारी'}, 'district_officer': {'en': 'District Officer', 'mr': 'जिल्हा अधिकारी', 'hi': 'जिला अधिकारी'}, 'state_admin': {'en': 'State Admin', 'mr': 'राज्य प्रशासक', 'hi': 'राज्य प्रशासक'}, 'super_admin': {'en': 'Super Admin', 'mr': 'सुपर प्रशासक', 'hi': 'सुपर एडमिन'}, 'total_newborns': {'en': 'Total Newborns', 'mr': 'एकूण नवजात बाळे', 'hi': 'कुल नवजात शिशु'}, 'today_visits': {'en': "Today's Visits", 'mr': 'आजच्या भेटी', 'hi': 'आज की मुलाकातें'}, 'pending_followups': {'en': 'Pending Follow-ups', 'mr': 'प्रलंबित पाठपुरावा', 'hi': 'लंबित फॉलो-अप'}, 'pending_referrals': {'en': 'Pending Referrals', 'mr': 'प्रलंबित रेफरल', 'hi': 'लंबित रेफरल'}, 'needs_attention': {'en': 'Needs Attention', 'mr': 'लक्ष देणे आवश्यक', 'hi': 'ध्यान आवश्यक'}, 'birth_details': {'en': 'Birth Details', 'mr': 'जन्माची माहिती', 'hi': 'जन्म विवरण'}, 'mother_details': {'en': 'Mother Details', 'mr': 'आईची माहिती', 'hi': 'माता की जानकारी'}, 'newborn_assessment': {'en': 'Newborn Assessment', 'mr': 'नवजात तपासणी', 'hi': 'नवजात मूल्यांकन'}, 'conditions': {'en': 'Conditions', 'mr': 'आरोग्य स्थिती', 'hi': 'स्वास्थ्य स्थितियां'}, 'referral_details': {'en': 'Referral Details', 'mr': 'रेफरल माहिती', 'hi': 'रेफरल विवरण'}, 'followup_schedule': {'en': 'Follow-up Schedule', 'mr': 'पाठपुरावा वेळापत्रक', 'hi': 'फॉलो-अप अनुसूची'}, 'newborn_name': {'en': 'Newborn Name', 'mr': 'नवजात बाळाचे नाव', 'hi': 'नवजात शिशु का नाम'}, 'date_of_birth': {'en': 'Date of Birth', 'mr': 'जन्म तारीख', 'hi': 'जन्म तिथि'}, 'time_of_birth': {'en': 'Time of Birth', 'mr': 'जन्माची वेळ', 'hi': 'जन्म का समय'}, 'sex': {'en': 'Sex', 'mr': 'लिंग', 'hi': 'लिंग'}, 'male': {'en': 'Male', 'mr': 'मुलगा', 'hi': 'लड़का'}, 'female': {'en': 'Female', 'mr': 'मुलगी', 'hi': 'लड़की'}, 'other': {'en': 'Other', 'mr': 'इतर', 'hi': 'अन्य'}, 'birth_weight': {'en': 'Birth Weight (kg)', 'mr': 'जन्म वजन (किलो)', 'hi': 'जन्म वजन (किलो)'}, 'gestational_age': {'en': 'Gestational Age (weeks)', 'mr': 'गर्भधारणेचे वय (आठवडे)', 'hi': 'गर्भकालीन आयु (सप्ताह)'}, 'place_of_birth': {'en': 'Place of Birth', 'mr': 'जन्माचे ठिकाण', 'hi': 'जन्म स्थान'}, 'delivery_type': {'en': 'Delivery Type', 'mr': 'प्रसूतीचा प्रकार', 'hi': 'प्रसव का प्रकार'}, 'mother_name': {'en': "Mother's Name", 'mr': 'आईचे नाव', 'hi': 'माता का नाम'}, 'mother_age': {'en': "Mother's Age", 'mr': 'आईचे वय', 'hi': 'माता की आयु'}, 'phone': {'en': 'Phone Number', 'mr': 'फोन नंबर', 'hi': 'फोन नंबर'}, 'address': {'en': 'Address', 'mr': 'पत्ता', 'hi': 'पता'}, 'village': {'en': 'Village', 'mr': 'गाव', 'hi': 'गांव'}, 'taluka': {'en': 'Taluka', 'mr': 'तालुका', 'hi': 'तालुका'}, 'district': {'en': 'District', 'mr': 'जिल्हा', 'hi': 'जिला'}, 'temperature': {'en': 'Temperature (°C)', 'mr': 'तापमान (°C)', 'hi': 'तापमान (°C)'}, 'feeding_difficulty': {'en': 'Feeding Difficulty', 'mr': 'दूध पिण्यात अडचण', 'hi': 'दूध पीने में कठिनाई'}, 'breathing_difficulty': {'en': 'Breathing Difficulty', 'mr': 'श्वास घेण्यास त्रास', 'hi': 'सांस लेने में कठिनाई'}, 'jaundice_observed': {'en': 'Jaundice Observed', 'mr': 'कावीळ दिसून आली', 'hi': 'पीलिया देखा गया'}, 'yes': {'en': 'Yes', 'mr': 'होय', 'hi': 'हाँ'}, 'no': {'en': 'No', 'mr': 'नाही', 'hi': 'नहीं'}, 'submit': {'en': 'Submit', 'mr': 'सबमिट करा', 'hi': 'सबमिट करें'}, 'save': {'en': 'Save', 'mr': 'जतन करा', 'hi': 'सहेजें'}, 'search': {'en': 'Search', 'mr': 'शोधा', 'hi': 'खोजें'}, 'status': {'en': 'Status', 'mr': 'स्थिती', 'hi': 'स्थिति'}, 'normal': {'en': 'Normal', 'mr': 'सामान्य', 'hi': 'सामान्य'}, 'attention': {'en': 'Needs Attention', 'mr': 'लक्ष देणे आवश्यक', 'hi': 'ध्यान आवश्यक'}, 'urgent': {'en': 'Urgent', 'mr': 'तातडीचे', 'hi': 'तत्काल'}, 'referred': {'en': 'Referred', 'mr': 'रेफर केले', 'hi': 'रेफर किया गया'}, 'pending': {'en': 'Pending', 'mr': 'प्रलंबित', 'hi': 'लंबित'}, 'register_success': {'en': 'Newborn registered successfully.', 'mr': 'नवजात बाळाची नोंदणी यशस्वी झाली.', 'hi': 'नवजात शिशु का पंजीकरण सफल रहा।'}}

TRANSLATIONS.update({
    'ai_health_assistant': {'en': 'AI Health Assistant', 'mr': 'एआय आरोग्य सहाय्यक', 'hi': 'एआई स्वास्थ्य सहायक'},
    'ask_by_voice': {'en': 'Ask by Voice', 'mr': 'आवाजाने विचारा', 'hi': 'आवाज़ से पूछें'},
    'record_question': {'en': 'Record your question', 'mr': 'तुमचा प्रश्न रेकॉर्ड करा', 'hi': 'अपना प्रश्न रिकॉर्ड करें'},
    'recognized_question': {'en': 'Recognized question', 'mr': 'ओळखलेला प्रश्न', 'hi': 'पहचाना गया प्रश्न'},
    'listen_to_response': {'en': 'Listen to response', 'mr': 'उत्तर ऐका', 'hi': 'उत्तर सुनें'},
    'use_voice_question': {'en': 'Use this voice question', 'mr': 'हा आवाजातील प्रश्न वापरा', 'hi': 'इस आवाज़ वाले प्रश्न का उपयोग करें'},
    'send_voice_question': {'en': 'Send voice question', 'mr': 'आवाजातील प्रश्न पाठवा', 'hi': 'आवाज़ वाला प्रश्न भेजें'},
    'or_type_question': {'en': 'Or type your question', 'mr': 'किंवा तुमचा प्रश्न टाइप करा', 'hi': 'या अपना प्रश्न टाइप करें'},
    'ai_health_description': {'en': 'Use voice or text to ask about newborn records, follow-ups, referrals, alerts, and general newborn-health information.', 'mr': 'नवजात नोंदी, पाठपुरावा, रेफरल, सूचना आणि सामान्य नवजात आरोग्य माहितीसाठी आवाजाने किंवा मजकूराने प्रश्न विचारा.', 'hi': 'नवजात रिकॉर्ड, फॉलो-अप, रेफरल, अलर्ट और सामान्य नवजात स्वास्थ्य जानकारी के बारे में आवाज़ या टेक्स्ट से पूछें.'},
})

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
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
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

# ============================================================
# AI ASSISTANT
# ============================================================

AI_SYSTEM_PROMPT = """
You are the AI assistant embedded in a newborn health surveillance application.
Your role is to support ASHA workers and authorized public-health officers with
record lookup, follow-up coordination, data-quality assistance, aggregate
summaries, and general newborn-health education.

SAFETY RULES:
- Do not diagnose a newborn. Distinguish observations/suspected conditions
  from clinician-confirmed diagnoses.
- Do not prescribe medicines, dosages, or treatment plans.
- Do not replace a doctor, nurse, or other qualified healthcare professional.
- If the user describes a newborn with an emergency warning sign or severe
  deterioration, advise immediate assessment by an appropriately qualified
  healthcare professional / emergency service rather than attempting to manage
  the emergency in chat.
- Never invent patient data. Use only the application context supplied below.
  If the requested record or fact is not present, say that it is not available.
- Protect privacy. Do not expose unnecessary personal information when an
  aggregate answer is sufficient.
- For application-data questions, clearly distinguish recorded data from your
  general educational explanation.
- Keep answers practical and concise for field workers.
"""


def language_name(language_code):
    return {'en': 'English', 'mr': 'Marathi', 'hi': 'Hindi'}.get(language_code, 'English')


def build_ai_data_context():
    """Create a compact, factual snapshot of the current prototype data."""
    newborns = st.session_state.get('newborns', [])
    today = date.today()
    records = []
    for baby in newborns:
        records.append({
            'id': baby.get('id'),
            'name': baby.get('name'),
            'date_of_birth': str(baby.get('dob')),
            'sex': baby.get('sex'),
            'birth_weight_kg': baby.get('weight'),
            'gestational_age_weeks': baby.get('gestational_age'),
            'village': baby.get('village'),
            'taluka': baby.get('taluka'),
            'district': baby.get('district'),
            'asha': baby.get('asha'),
            'status': baby.get('status'),
            'conditions': baby.get('conditions', []),
            'next_followup': str(baby.get('next_followup')),
            'followup_due_today_or_overdue': bool(baby.get('next_followup') and baby.get('next_followup') <= today),
            'referral_pending': bool(baby.get('referral')),
        })

    return json.dumps({
        'today': str(today),
        'current_role': st.session_state.get('role', 'ASHA Worker'),
        'current_language': language_name(st.session_state.get('language', 'en')),
        'newborn_count': len(records),
        'newborns': records,
    }, ensure_ascii=False, indent=2, default=str)


def local_ai_data_answer(question):
    """Handle simple record queries deterministically before calling the LLM."""
    q = question.lower().strip()
    newborns = st.session_state.get('newborns', [])
    today = date.today()

    # Direct newborn-ID lookup.
    import re
    ids = re.findall(r'nb[-\s]?\d{4}[-\s]?[a-z0-9]+', q, flags=re.I)
    if ids:
        normalized = ids[0].replace(' ', '').upper()
        for baby in newborns:
            if baby.get('id', '').upper() == normalized:
                return {
                    'type': 'record',
                    'data': baby,
                }

    # Follow-up queries.
    followup_terms = ['follow-up', 'followup', 'follow up', 'पाठपुरावा', 'फॉलो-अप']
    if any(term in q for term in followup_terms) and any(word in q for word in ['today', 'due', 'pending', 'overdue', 'आज', 'लंबित', 'प्रलंबित']):
        due = [b for b in newborns if b.get('next_followup') and b['next_followup'] <= today]
        return {'type': 'followups', 'data': due}

    # Referral queries.
    referral_terms = ['referral', 'referred', 'रेफरल', 'रेफर']
    if any(term in q for term in referral_terms) and any(word in q for word in ['pending', 'list', 'show', 'लंबित', 'दाखल', 'दाखव', 'दिखा']):
        referred = [b for b in newborns if b.get('referral')]
        return {'type': 'referrals', 'data': referred}

    # Urgent / attention lists.
    if any(word in q for word in ['urgent', 'तातडी', 'तत्काल', 'attention', 'लक्ष']):
        urgent = [b for b in newborns if b.get('status') in ['Urgent', 'Needs Attention']]
        return {'type': 'attention', 'data': urgent}

    return None


def format_local_ai_answer(result):
    """Turn deterministic application data into a compact prompt fragment."""
    if not result:
        return ''
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


def call_claude_ai(question, history):
    """Generate the text AI response using Anthropic Claude."""
    if not ANTHROPIC_API_KEY:
        return None, 'ANTHROPIC_API_KEY is not configured. Add your Claude API key to .env and restart Streamlit.'

    language = language_name(st.session_state.get('language', 'en'))
    context = build_ai_data_context()
    local_result = local_ai_data_answer(question)
    local_context = format_local_ai_answer(local_result)

    system_prompt = AI_SYSTEM_PROMPT + (
        f"\n\nRespond in {language}. Do not translate newborn IDs, dates, names, "
        "or database field values unless useful for readability. "
        "Do not expose unnecessary personal information. "
        "When discussing an AI photo-screening result, call it a screening "
        "signal and never a confirmed diagnosis."
        f"\n\nCURRENT APPLICATION DATA:\n{context}"
    )
    if local_context:
        system_prompt += (
            f"\n\nDETERMINISTIC QUERY RESULT FOR THIS REQUEST:\n{local_context}"
        )

    # Claude requires alternating user/assistant messages and does not accept
    # a system message inside the messages array. Keep only recent context.
    recent = history[-8:]
    messages = []
    for msg in recent:
        role = msg.get('role', 'user')
        if role not in ('user', 'assistant'):
            continue
        content = str(msg.get('content', '')).strip()
        if not content:
            continue
        if messages and messages[-1]['role'] == role:
            # Merge consecutive messages of the same role.
            messages[-1]['content'] += '\n\n' + content
        else:
            messages.append({'role': role, 'content': content})

    if not messages or messages[-1]['role'] != 'user':
        messages.append({'role': 'user', 'content': question})

    payload = {
        'model': ANTHROPIC_MODEL,
        'max_tokens': 2048,
        'system': system_prompt,
        'messages': messages,
    }

    try:
        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=90,
        )

        if not response.ok:
            try:
                body = response.json()
                detail = body.get('error', {}).get('message', response.text)
            except Exception:
                detail = response.text
            return None, f'Claude API error ({response.status_code}): {detail}'

        body = response.json()
        parts = []
        for item in body.get('content', []):
            if item.get('type') == 'text' and item.get('text'):
                parts.append(item['text'])

        answer = '\n'.join(parts).strip()
        if not answer:
            return None, 'Claude returned an empty response.'

        return answer, None

    except requests.RequestException as exc:
        return None, f'Could not connect to the Claude service: {exc}'
    except Exception as exc:
        return None, f'Unexpected Claude response error: {exc}'


def transcribe_voice(audio_file):
    """Transcribe a Streamlit microphone recording using OpenAI Speech-to-Text."""
    if not OPENAI_API_KEY:
        return None, (
            'OPENAI_API_KEY is not configured. Add it to your .env file or Streamlit secrets.'
        )
    if audio_file is None:
        return None, 'No voice recording was provided.'

    language = st.session_state.get('language', 'en')
    # Streamlit st.audio_input() currently returns WAV audio. Use the actual
    # uploaded bytes rather than trying to re-encode them in the browser.
    audio_bytes = audio_file.getvalue()
    if not audio_bytes:
        return None, 'The microphone returned an empty recording. Please record again.'

    # The primary model is configurable. If an account/model-access issue is
    # returned, retry once with GPT-4o Transcribe. This gives a clearer and
    # more robust fallback than failing the whole voice feature.
    models = []
    for model_name in [OPENAI_TRANSCRIPTION_MODEL, 'gpt-4o-transcribe']:
        if model_name and model_name not in models:
            models.append(model_name)

    last_error = None
    try:
        for model_name in models:
            files = {
                'file': ('voice_question.wav', audio_bytes, 'audio/wav')
            }
            data = {
                'model': model_name,
                'language': language,
                'response_format': 'json',
            }

            response = requests.post(
                OPENAI_TRANSCRIPTION_URL,
                headers={'Authorization': f'Bearer {OPENAI_API_KEY.strip()}'},
                files=files,
                data=data,
                timeout=90,
            )

            if response.ok:
                body = response.json()
                text = (body.get('text') or '').strip()
                if text:
                    return text, None
                last_error = f'{model_name} returned an empty transcription.'
                continue

            try:
                error_body = response.json()
                error_obj = error_body.get('error', {})
                detail = error_obj.get('message') or response.text
                error_type = error_obj.get('type') or ''
                error_code = error_obj.get('code') or ''
            except Exception:
                detail = response.text
                error_type = ''
                error_code = ''

            last_error = (
                f'{model_name}: HTTP {response.status_code}: {detail}'
                + (f' [{error_type}]' if error_type else '')
                + (f' [{error_code}]' if error_code else '')
            )

            # Retry the alternate model for model/access-related failures.
            if response.status_code not in (400, 401, 403, 404, 429, 500, 502, 503):
                break

        return None, (
            'Voice transcription failed. ' + (last_error or 'No transcription was returned.')
        )

    except requests.RequestException as exc:
        return None, f'Could not connect to the OpenAI speech service: {exc}'
    except Exception as exc:
        return None, f'Unexpected voice transcription error: {exc}'

def generate_voice_response(text):
    """Generate MP3 speech for the current AI response."""
    if not OPENAI_API_KEY:
        return None, 'OPENAI_API_KEY is not configured.'
    if not text:
        return None, 'There is no AI response to read aloud.'

    language = st.session_state.get('language', 'en')
    language_label = language_name(language)
    try:
        payload = {
            'model': OPENAI_TTS_MODEL,
            'voice': OPENAI_TTS_VOICE,
            'input': text,
            'instructions': (
                f'Speak clearly and naturally in {language_label}. '
                'Use a calm, professional, easy-to-understand voice suitable '
                'for a public-health field worker. Do not translate names, '
                'newborn IDs, dates, or medical terms unnecessarily.'
            ),
            'response_format': 'mp3',
        }
        response = requests.post(
            OPENAI_SPEECH_URL,
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=90,
        )
        if not response.ok:
            try:
                detail = response.json().get('error', {}).get('message', response.text)
            except Exception:
                detail = response.text
            return None, f'Voice generation error ({response.status_code}): {detail}'
        return response.content, None
    except requests.RequestException as exc:
        return None, f'Could not connect to the voice service: {exc}'
    except Exception as exc:
        return None, f'Unexpected voice generation error: {exc}'


def attractive_chart(fig, height=360):
    """Apply a consistent dashboard-quality Plotly layout."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, Segoe UI, sans-serif', size=13),
        title=dict(x=0.02, xanchor='left', font=dict(size=17, family='Inter, Segoe UI, sans-serif')),
        legend=dict(orientation='h', yanchor='bottom', y=1.01, xanchor='right', x=1),
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor='rgba(148,163,184,.25)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(148,163,184,.16)', zeroline=False)
    return fig


def ai_assistant_page(show_title=True):
    if show_title:
        st.title(f"🤖 {ui_text('AI Assistant')}")

    st.caption(ui_text('Ask about newborn records, follow-ups, referrals, data quality, or general newborn-health information.'))

    if not OPENAI_API_KEY:
        st.warning(ui_text('AI chatbot is not configured yet. Add OPENAI_API_KEY to your .env file and restart Streamlit.'))
        st.code('OPENAI_API_KEY=your_api_key_here\nOPENAI_MODEL=gpt-5.6-luna', language='text')
        st.info(ui_text('The rest of the application continues to work without the AI API.'))
        return

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button(ui_text('Clear Chat'), use_container_width=True, key='clear_ai_chat'):
            st.session_state.chat_messages = []
            st.session_state.voice_recording_hash = None
            st.session_state.last_voice_text = ''
            st.rerun()

    quick_prompts = [
        'Which newborns need follow-up today?',
        'Show me pending referrals.',
        'Which newborns need attention?',
        'Explain jaundice in a newborn.',
    ]
    selected_prompt = st.selectbox(
        ui_text('Quick questions'),
        ['-- Select --'] + quick_prompts,
        format_func=ui_text,
        key='ai_quick_prompt',
    )
    if selected_prompt != '-- Select --':
        st.session_state.ai_pending_prompt = selected_prompt

    # Existing conversation
    for message in st.session_state.chat_messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if message['role'] == 'assistant' and message.get('audio'):
                st.audio(message['audio'], format='audio/mp3')

    # --------------------------------------------------------
    # VOICE INPUT
    # --------------------------------------------------------
    st.markdown(f"### 🎤 {t('ask_by_voice')}")
    st.caption(ui_text('Record your question in English, Marathi, or Hindi.'))

    audio_file = st.audio_input(
        t('record_question'),
        sample_rate=16000,
        key='voice_question_input',
    )

    voice_prompt = None
    if audio_file is not None:
        audio_bytes = audio_file.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        st.session_state.current_voice_hash = audio_hash

        # Always show the captured recording so microphone/browser problems
        # can be distinguished from API transcription problems.
        st.audio(audio_file, format='audio/wav')
        st.caption(
            f"Recording captured: {len(audio_bytes) / 1024:.1f} KB | "
            f"MIME: {getattr(audio_file, 'type', 'audio/wav')}"
        )

        if st.session_state.get('voice_recording_hash') != audio_hash:
            st.session_state.voice_transcription = None
            st.session_state.voice_transcription_error = None

        if st.button(
            f"🎤 {t('use_voice_question')}",
            type='primary',
            use_container_width=True,
            key=f'use_voice_{audio_hash[:10]}',
        ):
            with st.spinner(ui_text('Converting your voice to text...')):
                recognized_text, voice_error = transcribe_voice(audio_file)

            if voice_error:
                st.session_state.voice_transcription_error = voice_error
                st.session_state.voice_transcription = None
            else:
                st.session_state.voice_transcription = recognized_text
                st.session_state.voice_recording_hash = audio_hash
                st.session_state.voice_transcription_error = None

            st.rerun()

        if st.session_state.get('voice_transcription_error'):
            st.error(st.session_state.voice_transcription_error)
            st.info(
                'If the recording plays above but transcription fails, the microphone is working; '
                'the problem is the OpenAI speech API key/model/access configuration.'
            )

        if st.session_state.get('voice_transcription'):
            voice_prompt = st.session_state.voice_transcription
            st.success(
                f"{t('recognized_question')}: {voice_prompt}"
            )

            if st.button(
                f"➤ {t('send_voice_question')}",
                use_container_width=True,
                key=f'send_voice_{audio_hash[:10]}',
            ):
                st.session_state.ai_pending_prompt = voice_prompt
                st.session_state.voice_transcription = None
                st.rerun()

    # --------------------------------------------------------
    # TEXT INPUT FALLBACK
    # --------------------------------------------------------
    st.markdown(f"**{t('or_type_question')}**")
    text_prompt = st.chat_input(ui_text('Ask the AI assistant...'))

    prompt = text_prompt
    if not prompt and st.session_state.get('ai_pending_prompt'):
        prompt = st.session_state.pop('ai_pending_prompt')

    if prompt:
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': prompt,
        })

        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            with st.spinner(ui_text('AI is preparing a response...')):
                answer, error = call_claude_ai(
                    prompt,
                    st.session_state.chat_messages[:-1],
                )

            if error:
                st.error(error)
                answer = ui_text(
                    'I could not complete that request. Please check the AI configuration and try again.'
                )

            st.markdown(answer)

            # Voice response button
            if answer and not error:
                voice_key = hashlib.sha256(answer.encode('utf-8')).hexdigest()[:12]
                if st.button(
                    f"🔊 {t('listen_to_response')}",
                    key=f'listen_{voice_key}',
                    use_container_width=True,
                ):
                    with st.spinner(ui_text('Generating voice response...')):
                        audio_bytes, audio_error = generate_voice_response(answer)

                    if audio_error:
                        st.error(audio_error)
                    else:
                        st.audio(audio_bytes, format='audio/mp3', autoplay=False)
                        st.session_state.last_generated_audio = audio_bytes

        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': answer,
        })

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
    if st.button(f"🤖 {ui_text('AI Assistant')}", use_container_width=True):
        st.session_state.page = 'ai_assistant'
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

def dashboard_chart_status(newborns):
    status_counts = {
        'Normal': sum(x['status'] == 'Normal' for x in newborns),
        'Needs Attention': sum(x['status'] == 'Needs Attention' for x in newborns),
        'Urgent': sum(x['status'] == 'Urgent' for x in newborns),
    }
    df = pd.DataFrame({'Status': list(status_counts.keys()), 'Count': list(status_counts.values())})
    fig = px.pie(
        df,
        names='Status',
        values='Count',
        hole=0.62,
        color='Status',
        color_discrete_map={
            'Normal': '#22c55e',
            'Needs Attention': '#f59e0b',
            'Urgent': '#ef4444',
        },
    )
    fig.update_traces(
        textposition='outside',
        textinfo='label+percent',
        marker=dict(line=dict(color='white', width=3)),
    )
    fig.add_annotation(
        text=f"<b>{len(newborns)}</b><br><span style='font-size:12px'>Newborns</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22),
    )
    return attractive_chart(fig, 390)


def dashboard_condition_chart(newborns):
    counter = {}
    for baby in newborns:
        for condition in baby.get('conditions', []):
            counter[condition] = counter.get(condition, 0) + 1

    if not counter:
        return None

    df = pd.DataFrame(
        sorted(counter.items(), key=lambda x: x[1], reverse=True),
        columns=['Condition', 'Count'],
    ).sort_values('Count')

    fig = px.bar(
        df,
        x='Count',
        y='Condition',
        orientation='h',
        text='Count',
        color='Count',
        color_continuous_scale='Teal',
    )
    fig.update_traces(
        textposition='outside',
        cliponaxis=False,
        marker_line_width=0,
    )
    fig.update_coloraxes(showscale=False)
    return attractive_chart(fig, 390)


def dashboard_village_chart(newborns):
    df = pd.DataFrame(newborns)
    if df.empty:
        return None
    village_df = df.groupby('village').size().reset_index(name='Newborns').sort_values('Newborns')
    fig = px.bar(
        village_df,
        x='Newborns',
        y='village',
        orientation='h',
        text='Newborns',
        color='Newborns',
        color_continuous_scale='Blues',
    )
    fig.update_traces(textposition='outside', cliponaxis=False, marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    return attractive_chart(fig, 360)


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

    # KPI cards
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

    # Attractive chart row
    chart1, chart2 = st.columns([1, 1.25], gap='large')
    with chart1:
        st.markdown('#### 🩺 Newborn Status')
        st.plotly_chart(
            dashboard_chart_status(newborns),
            use_container_width=True,
            config={'displayModeBar': False},
        )
    with chart2:
        st.markdown('#### 📌 Recorded Conditions')
        condition_fig = dashboard_condition_chart(newborns)
        if condition_fig:
            st.plotly_chart(condition_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info(ui_text('No conditions recorded.'))

    # Village analytics
    st.markdown('#### 📍 Newborns by Village')
    village_fig = dashboard_village_chart(newborns)
    if village_fig:
        st.plotly_chart(village_fig, use_container_width=True, config={'displayModeBar': False})

    # ASHA priority section
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

    # AI assistant on EVERY dashboard
    st.divider()
    st.markdown('## 🤖 ' + t('ai_health_assistant'))
    st.caption(ui_text('Use voice or text to ask about newborn records, follow-ups, referrals, alerts, and general newborn-health information.'))
    ai_assistant_page(show_title=False)

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

    col1, col2 = st.columns(2, gap='large')
    with col1:
        village_df = df.groupby('village').size().reset_index(name='Newborns').sort_values('Newborns')
        fig = px.bar(village_df, x='Newborns', y='village', orientation='h', text='Newborns', color='Newborns', color_continuous_scale='Blues')
        fig.update_traces(textposition='outside', cliponaxis=False, marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(title=ui_text('Newborns by Village'))
        st.plotly_chart(attractive_chart(fig), use_container_width=True, config={'displayModeBar': False})

    with col2:
        fig = px.histogram(df, x='weight', nbins=8, marginal='box', title=ui_text('Birth Weight Distribution'), color_discrete_sequence=['#14b8a6'])
        fig.update_traces(marker_line_width=1, marker_line_color='white')
        st.plotly_chart(attractive_chart(fig), use_container_width=True, config={'displayModeBar': False})

    st.subheader(ui_text('Condition Distribution'))
    condition_counter = {}
    for baby in newborns:
        for condition in baby['conditions']:
            condition_counter[condition] = condition_counter.get(condition, 0) + 1
    if condition_counter:
        condition_df = pd.DataFrame(
            [{'Condition': k, 'Count': v} for k, v in condition_counter.items()]
        ).sort_values('Count')
        fig = px.bar(condition_df, x='Count', y='Condition', orientation='h', text='Count', color='Count', color_continuous_scale='Teal')
        fig.update_traces(textposition='outside', cliponaxis=False, marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(title=ui_text('Recorded Conditions'))
        st.plotly_chart(attractive_chart(fig), use_container_width=True, config={'displayModeBar': False})

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
elif page == 'ai_assistant':
    ai_assistant_page()
elif page == 'research':
    research_page()
elif page == 'quality':
    data_quality_page()
elif page == 'admin':
    admin_page()
else:
    dashboard()
