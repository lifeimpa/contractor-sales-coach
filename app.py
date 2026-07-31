import streamlit as st
import pandas as pd
import random
import time
import requests
import json
import os

# Set up page configurations
st.set_page_config(
    page_title="SalesFlow AI - Enterprise Sales Coach & Enablement Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- DESIGN SYSTEM & PREMIUM CSS THEME (Stripe & Linear Inspired) -----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&family=Material+Icons+Outlined&display=swap" rel="stylesheet">
<style>
    /* Reset & Typography */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F6F8FB;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #111827;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0); border-bottom: none;}
    
    /* Sidebar Overrides (Linear style) */
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid #1E293B !important;
        padding-top: 20px;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: #1E293B !important;
        color: #F1F5F9 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-size: 13px !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #2563EB !important;
        color: white !important;
        border-color: #2563EB !important;
    }
    
    /* Layout Cards & Containers */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.01);
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .saas-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.01);
        border-color: #D1D5DB;
    }
    .saas-card-dark {
        background: #0B0F19;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 24px;
        color: #F1F5F9;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
        margin-bottom: 24px;
    }
    
    /* Premium Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 100%);
        border: 1px solid #1E293B;
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        color: white;
    }
    .hero-container::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(37,99,235,0.15) 0%, rgba(0,0,0,0) 70%);
        pointer-events: none;
    }
    .hero-title {
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 8px;
        background: linear-gradient(to right, #FFFFFF, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-tagline {
        font-size: 16px;
        color: #94A3B8;
        font-weight: 400;
        margin-bottom: 24px;
    }
    
    /* Mini KPI Cards inside Hero */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 16px;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 12px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Segmented Navigation (Tabs) */
    .nav-pills {
        display: inline-flex;
        background: #E2E8F0;
        padding: 4px;
        border-radius: 10px;
        margin-bottom: 24px;
    }
    .nav-pill-active {
        background: white;
        color: #0F172A;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Buttons Customization */
    .stButton>button {
        background: linear-gradient(180deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #1D4ED8 !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(37,99,235,0.15) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(180deg, #1D4ED8 0%, #1E40AF 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
    }
    .stButton>button:active {
        transform: translateY(1px) !important;
    }
    
    /* Secondary/Outline Button styling */
    .secondary-btn>div>.stButton>button {
        background: white !important;
        color: #374151 !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    .secondary-btn>div>.stButton>button:hover {
        background: #F9FAFB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    
    /* Chat Conversation Bubbles (ChatGPT Inspired) */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 24px;
    }
    .chat-bubble-user {
        background-color: #F1F5F9;
        border-radius: 16px 16px 4px 16px;
        padding: 16px 20px;
        max-width: 80%;
        align-self: flex-end;
        color: #0F172A;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #E2E8F0;
    }
    .chat-bubble-ai {
        background-color: #0F172A;
        border-radius: 16px 16px 16px 4px;
        padding: 16px 20px;
        max-width: 80%;
        align-self: flex-start;
        color: #F8FAFC;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #1E293B;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
    }
    .chat-meta {
        font-size: 11px;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chat-meta-ai {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chat-badge-coach {
        background: #2563EB;
        color: white;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        font-size: 9px;
    }
    
    /* Material Icon Styling Wrapper */
    .icon {
        font-family: 'Material Icons Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- PERSISTENT USER PROFILES DATABASE (JSON-based) -----------------
PROFILES_FILE = "sales_profiles.json"

DEFAULT_PROFILES = {
    "Select a Profile...": {
        "industry": "",
        "persona": "",
        "mood": ""
    },
    "💻 Cybersecurity SaaS (CISO)": {
        "industry": "Enterprise Cybersecurity threat-detection platform",
        "persona": "Marcus Vance, Chief Information Security Officer (CISO)",
        "mood": "Super busy, dealing with an active server patch, highly skeptical"
    },
    "🔨 Contractor Dispatch Software (Jobtable)": {
        "industry": "HVAC / Plumbing Dispatch & Invoicing Software (Jobtable)",
        "persona": "Bob Miller, Miller & Sons Plumbing (Owner)",
        "mood": "Super Stressed, working under a sink, tech-skeptical"
    },
    "🏠 Real Estate Outbound": {
        "industry": "Residential Property Listing Services",
        "persona": "Dave Kowalski, Private Homeowner (FSBO seller)",
        "mood": "Defensive, annoyed by agents, wants to sell without commission"
    }
}

# Load profiles from file or create defaults
if not os.path.exists(PROFILES_FILE):
    with open(PROFILES_FILE, "w") as f:
        json.dump(DEFAULT_PROFILES, f, indent=4)

def load_user_profiles():
    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_PROFILES

def save_user_profile(name, industry, persona, mood):
    profiles = load_user_profiles()
    profiles[name] = {
        "industry": industry,
        "persona": persona,
        "mood": mood
    }
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

def delete_user_profile(name):
    profiles = load_user_profiles()
    if name in profiles:
        del profiles[name]
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

# ----------------- SESSION STATE INITIALIZATION -----------------
# 1. API Connection Status & Secure Key Storage
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "api_connection_error" not in st.session_state:
    st.session_state.api_connection_error = ""
if "active_api_key" not in st.session_state:
    st.session_state.active_api_key = ""
if "active_api_provider" not in st.session_state:
    st.session_state.active_api_provider = "Practice Simulator (Offline)"
if "active_model_name" not in st.session_state:
    st.session_state.active_model_name = "gemini-1.5-flash-latest"

# 2. Active Chat Logs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_call_active" not in st.session_state:
    st.session_state.is_call_active = False
# 3. Dynamic Wizard Onboarding states
if "wizard_industry" not in st.session_state:
    st.session_state.wizard_industry = ""
if "wizard_persona" not in st.session_state:
    st.session_state.wizard_persona = ""
if "wizard_mood" not in st.session_state:
    st.session_state.wizard_mood = ""
# 4. Analytics
if "objections_handled" not in st.session_state:
    st.session_state.objections_handled = 0
if "score" not in st.session_state:
    st.session_state.score = 100
# 5. Quiz Performance History Log
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

# Load existing user profiles
saved_profiles = load_user_profiles()

# ----------------- SIDEBAR: LINEAR-STYLE WORKSPACE NAVIGATION -----------------
with st.sidebar:
    # App Branding
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 24px; padding-left: 8px;'>
        <div style='background: #2563EB; color: white; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; margin-right: 12px; box-shadow: 0 4px 10px rgba(37,99,235,0.4);'>SF</div>
        <div>
            <h3 style='margin: 0; color: white !important; font-size: 16px; font-weight: 700;'>SalesFlow AI</h3>
            <p style='margin: 0; color: #64748B; font-size: 11px;'>Intelligent Sales Coach</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Active Connection Panel inside Sidebar
    st.markdown("<p style='font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; padding-left: 8px; margin-bottom: 12px;'>🔌 Connection Settings</p>", unsafe_allow_html=True)
    
    api_provider = st.selectbox(
        "Default AI Engine", 
        ["Practice Simulator (Offline)", "Google Gemini API", "DeepSeek API"]
    )
    
    api_key_input = ""
    if api_provider != "Practice Simulator (Offline)":
        default_val = st.session_state.active_api_key if api_provider == st.session_state.active_api_provider else ""
        api_key_input = st.text_input("API Access Key", value=default_val, type="password", help="Input your authorization key from your selected AI platform")
        
        # Connect Button (Linear Style Sidebar spacing)
        if st.button("🔌 Establish Secure Link", use_container_width=True):
            if not api_key_input:
                st.error("Please enter an API Key first.")
            else:
                with st.spinner("Handshaking..."):
                    try:
                        if api_provider == "Google Gemini API":
                            import google.generativeai as genai
                            genai.configure(api_key=api_key_input)
                            fallback_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
                            working_model = None
                            last_err = ""
                            
                            for m_name in fallback_models:
                                try:
                                    model = genai.GenerativeModel(m_name)
                                    test_response = model.generate_content("hello")
                                    working_model = m_name
                                    break
                                except Exception as e_model:
                                    last_err = str(e_model)
                                    continue
                            
                            if working_model:
                                st.session_state.api_connected = True
                                st.session_state.api_connection_error = ""
                                st.session_state.active_api_key = api_key_input
                                st.session_state.active_api_provider = api_provider
                                st.session_state.active_model_name = working_model
                            else:
                                st.session_state.api_connected = False
                                st.session_state.api_connection_error = f"Model rejected: {last_err}"
                                
                        elif api_provider == "DeepSeek API":
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {api_key_input}"
                            }
                            data = {
                                "model": "deepseek-chat",
                                "messages": [{"role": "user", "content": "hello"}],
                                "max_tokens": 5
                            }
                            response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=5)
                            if response.status_code == 200:
                                st.session_state.api_connected = True
                                st.session_state.api_connection_error = ""
                                st.session_state.active_api_key = api_key_input
                                st.session_state.active_api_provider = api_provider
                            else:
                                st.session_state.api_connected = False
                                st.session_state.api_connection_error = f"DeepSeek rejected key: status {response.status_code}"
                    except Exception as e:
                        st.session_state.api_connected = False
                        st.session_state.api_connection_error = str(e)
                        
        # Connection status feedback (minimal HUD badge)
        if st.session_state.api_connected and api_provider == st.session_state.active_api_provider:
            st.markdown(f"<div style='background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 6px; padding: 10px; margin-top: 10px; font-size: 12px; color: #10B981; font-weight: 500;'>🟢 Connection Verified<br/><span style='color: #64748B; font-size: 10px;'>Model: {st.session_state.active_model_name}</span></div>", unsafe_allow_html=True)
        else:
            if st.session_state.api_connection_error:
                st.markdown(f"<div style='background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 6px; padding: 10px; margin-top: 10px; font-size: 12px; color: #EF4444;'>🔴 Connection Failed:<br/><span style='font-size: 10px; color: #94A3B8;'>{st.session_state.api_connection_error[:50]}...</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 6px; padding: 10px; margin-top: 10px; font-size: 12px; color: #F59E0B;'>🟡 Offline Practice Mode</div>", unsafe_allow_html=True)
                
        with st.expander("🔑 Help Center"):
            st.markdown("""
            <p style='font-size: 11px; color: #94A3B8;'>Google Gemini keys are generated 100% free of charge via <a href='https://aistudio.google.com/' target='_blank' style='color:#3B82F6;'>AI Studio</a>. No credit card required.</p>
            """, unsafe_allow_html=True)
    else:
        st.session_state.api_connected = False
        st.markdown("<div style='background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.3); border-radius: 6px; padding: 12px; font-size: 12px; color: #3B82F6; font-weight: 500;'>⚡ Simulator Engine Active<br/><span style='color: #64748B; font-size: 10px;'>No API key required.</span></div>", unsafe_allow_html=True)
        
    st.write("---")
    
    # Premium HUD Metrics inside Sidebar
    st.markdown("<p style='font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; padding-left: 8px; margin-bottom: 12px;'>📊 My Performance HUD</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
        <p style='font-size: 11px; color: #94A3B8; margin-bottom: 2px;'>Rapport Score</p>
        <h3 style='margin: 0; color: white !important; font-size: 20px; font-weight: 700;'>{st.session_state.score} / 100</h3>
    </div>
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 16px;'>
        <p style='font-size: 11px; color: #94A3B8; margin-bottom: 2px;'>Objections Overcome</p>
        <h3 style='margin: 0; color: white !important; font-size: 20px; font-weight: 700;'>{st.session_state.objections_handled}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Upgrade / Version HUD Card
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 12px; padding: 16px; margin-bottom: 20px;'>
        <h4 style='color: white !important; font-size: 13px; font-weight: 700; margin-top: 0; margin-bottom: 4px;'>Upgrade to SaaS Enterprise</h4>
        <p style='color: #94A3B8; font-size: 11px; margin-bottom: 12px; line-height: 1.4;'>Unlock deeper call transcription analysis, custom persona deployments, and REST API synchronizations.</p>
        <a href='https://checkout.lemonsqueezy.com/checkout/' target='_blank' style='display: block; text-align: center; background: #2563EB; color: white; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; text-decoration: none;'>🚀 Go Unlimited</a>
    </div>
    <div style='text-align: center; color: #64748B; font-size: 10px;'>SalesFlow AI SaaS v2.4</div>
    """, unsafe_allow_html=True)

# ----------------- PREMIUM MAIN HEADER BANNER (Notion / Vercel style) -----------------
st.markdown("""
<div class="hero-container">
    <div style="display: flex; align-items: center; margin-bottom: 12px;">
        <span class="icon" style="font-size: 32px; color: #3B82F6;">auto_awesome</span>
        <span class="badge-premium">Enterprise Suite</span>
    </div>
    <div class="hero-title">SalesFlow AI — Complete Revenue Enablement Platform</div>
    <div class="hero-tagline">Analyze transcripts, practice outbound phone calls, write emails, and generate short-form prospecting Loom video scripts. All powered by advanced Google Gemini & DeepSeek AI models.</div>
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">Google / DeepSeek</div>
            <div class="kpi-label">API Connective Brain</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">97% Confidence</div>
            <div class="kpi-label">Auditing Precision</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">Sandler / SPIN</div>
            <div class="kpi-label">Sales Frameworks</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">100% Secure</div>
            <div class="kpi-label">SaaS Encryption</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- MODULE SWITCHER (Tab Section) -----------------
st.markdown("### 💼 Active Workspace Module")
active_module = st.radio(
    "Toggle between different environments to change tabs and workflows:",
    [
        "📞 Module A: Outbound Cold-Call Assistant Agent (Core Simulator & Prep)",
        "🤝 Module B: General Closing & Outreach Copilot (Face-to-Face, Email, SMS & Video)",
        "🎓 Module C: Sales Academy & Industry Onboarding Hub (ABC Industry Guides & Tests)"
    ],
    horizontal=True
)

st.write("---")

# ==================== MODULE A: OUTBOUND COLD-CALL ASSISTANT AGENT ====================
if active_module == "📞 Module A: Outbound Cold-Call Assistant Agent (Core Simulator & Prep)":
    
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <span class="icon" style="font-size: 28px; color: #1E40AF;">phone_in_talk</span>
        <h2 style='margin: 0;'>📞 Module A: Outbound Cold-Call Assistant Agent</h2>
    </div>
    """, unsafe_allow_html=True)
    
    sub_tab_practice, sub_tab_opener, sub_tab_discovery, sub_tab_precall, sub_tab_battlecards = st.tabs([
        "📞 Live Cold Call Roleplay Arena",
        "🎯 Cold Call Opener Architect",
        "💡 Consultative Discovery Generator",
        "📝 Pre-Call Prep Sheet Planner",
        "🛡️ Outbound Objection Battlecards"
    ])
    
    # 1. LIVE COLD CALL ROLEPLAY ARENA
    with sub_tab_practice:
        st.markdown("""
        <div class="saas-card">
            <h3>⚙️ Step 1: Onboarding Setup Wizard</h3>
            <p style='color: #6B7280; font-size: 14px; margin-bottom: 20px;'>Select any saved custom profile, use industry presets, or configure a blank setup from scratch.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_p_load, col_wiz1 = st.columns([1, 1])
        
        with col_p_load:
            loaded_p_name = st.selectbox(
                "📂 Saved Private Profiles:",
                list(saved_profiles.keys()),
                help="Load configured profiles instantly."
            )
            if loaded_p_name != "Select a Profile...":
                st.session_state.setup_industry = saved_profiles[loaded_p_name]["industry"]
                st.session_state.setup_persona = saved_profiles[loaded_p_name]["persona"]
                st.session_state.setup_mood = saved_profiles[loaded_p_name]["mood"]
        
        with col_wiz1:
            sector_choice = st.selectbox(
                "Select Broad Industry recommendation:",
                [
                    "Select Industry Recommendation...",
                    "💻 B2B Software & Enterprise SaaS",
                    "🔨 Construction, Trades & Mechanical Services (Jobtable)",
                    "🏠 Real Estate, Mortgages & Housing",
                    "🏥 Medical, Clinical & Biotech Services",
                    "💼 Professional B2B Services (Logistics, Consulting, HR)",
                    "📦 Retail, Wholesale & Consumer Goods",
                    "✍️ Custom Sector (Write my own)"
                ]
            )
            
        suggested_personas = []
        suggested_moods = []
        default_product = ""
        
        if sector_choice == "💻 B2B Software & Enterprise SaaS":
            default_product = "Enterprise Cloud Security SaaS"
            suggested_personas = ["Chief Information Security Officer (CISO)", "Chief Financial Officer (CFO)", "VP of Sales Operations", "Director of HR & Benefits", "Chief Technology Officer (CTO)", "VP of Global Procurement", "Custom (Write my own)"]
            suggested_moods = ["Defensive about cold calls, extremely busy, budget locked", "Analytical, protective of company overhead, wants exact ROI", "Skeptical, happy with current competitor, refuses complex setup", "Custom (Write my own)"]
        elif sector_choice == "🔨 Construction, Trades & Mechanical Services (Jobtable)":
            default_product = "Jobtable Contractor Dispatch & Invoicing App"
            suggested_personas = ["Plumbing Contractor Owner", "Electrical Shop Owner", "HVAC Project Supervisor", "MEP General Contractor", "Roofing Business Owner", "Solar Installer Director", "Professional Commercial Painter", "Custom (Write my own)"]
            suggested_moods = ["Super stressed, working under a sink, hates sales scripts", "Driving between jobs, behind on QuickBooks, paperwork backlog", "On a rooftop, happy with pen and paper whiteboard layouts", "Custom (Write my own)"]
        elif sector_choice == "🏠 Real Estate, Mortgages & Housing":
            default_product = "Residential Listing & Selling Services"
            suggested_personas = ["For Sale By Owner (FSBO) Private seller", "First-Time Home Buyer", "Commercial Real Estate Investor", "Corporate Property Manager", "Licensed Mortgage Broker", "Custom (Write my own)"]
            suggested_moods = ["Annoyed by listing agents, defensive, wants zero commission", "Confused by paperwork, anxious about mortgage interest rates", "Opportunistic, looking for immediate off-market deals", "Custom (Write my own)"]
        elif sector_choice == "🏥 Medical, Clinical & Biotech Services":
            default_product = "Patient Intake & Cloud Billing Software"
            suggested_personas = ["Private Clinical Lead Administrator", "Chief Medical Officer (CMO)", "Hospital Procurement Officer", "Dental Practice Manager", "Lead Physical Therapist", "Custom (Write my own)"]
            suggested_moods = ["Heavily distracted, burdened by compliance and regulations", "Skeptical of training time, worries about patient HIPAA data leak", "Strictly focused on procurement cost-savings, protective", "Custom (Write my own)"]
        elif sector_choice == "💼 Professional B2B Services (Logistics, Consulting, HR)":
            default_product = "Third-Party Fleet & Logistics Consulting"
            suggested_personas = ["VP of Fleet Logistics", "Corporate Human Resources Director", "Managing Director", "Custom (Write my own)"]
            suggested_moods = ["Stressed by fuel costs and supply chain delays", "Overwhelmed by employee turnover, looking for staffing speed", "Analytical, focusing on structural operating overhead", "Custom (Write my own)"]
        elif sector_choice == "📦 Retail, Wholesale & Consumer Goods":
            default_product = "Wholesale Inventory Management Portal"
            suggested_personas = ["Retail Store Manager", "Regional Category Buyer", "Wholesale Distribution Director", "Custom (Write my own)"]
            suggested_moods = ["Defensive about shelf space and inventory turns", "Demanding large volume discounts, highly price-sensitive", "Anxious about shipping times and shelf storage backlog", "Custom (Write my own)"]
        elif sector_choice == "✍️ Custom Sector (Write my own)":
            default_product = ""
            suggested_personas = ["Custom (Write my own)"]
            suggested_moods = ["Custom (Write my own)"]

        if sector_choice != "Select Industry Recommendation..." and sector_choice != "":
            st.session_state.setup_industry = default_product
            if suggested_personas:
                st.session_state.setup_persona = suggested_personas[0]
            if suggested_moods:
                st.session_state.setup_mood = suggested_moods[0]

        # Parameter Form Wrapper
        st.write("🔧 **Finalize Target Market Parameters:**")
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            ui_industry = st.text_input("My Product / Platform:", value=st.session_state.setup_industry, placeholder="e.g. Paints, Tiles, Security Software, Mortgages", key="call_prod_inp")
        with col_in2:
            ui_persona = st.text_input("Target Customer Title / Role:", value=st.session_state.setup_persona, placeholder="e.g. Architect, Builder, CISO, Homeowner", key="call_pers_inp")
        with col_in3:
            ui_mood = st.text_input("Buyer's Current Mood / Style:", value=st.session_state.setup_mood, placeholder="e.g. Stressed on site, highly skeptical of quality, defensive", key="call_mood_inp")

        st.session_state.setup_industry = ui_industry
        st.session_state.setup_persona = ui_persona
        st.session_state.setup_mood = ui_mood

        # Save profile card
        with st.expander("💾 Save this Custom setup as a Profile (Never start from scratch!)"):
            col_save1, col_save2 = st.columns([2, 1])
            with col_save1:
                profile_save_name = st.text_input("Profile Name:", placeholder="e.g. My Custom Paint Sales Setup")
            with col_save2:
                save_click = st.button("💾 Save Configuration")
                if save_click and profile_save_name:
                    save_user_profile(profile_save_name, ui_industry, ui_persona, ui_mood)
                    st.success(f"Profile '{profile_save_name}' saved permanently!")
                    time.sleep(0.5)
                    st.rerun()
            
            st.write("---")
            st.write("##### ❌ Delete an Existing Profile:")
            col_del1, col_del2 = st.columns([2, 1])
            with col_del1:
                profile_to_delete = st.selectbox(
                    "Select Profile to Delete:",
                    [p for p in list(saved_profiles.keys()) if p != "Select a Profile..."],
                    help="Select any saved profile to permanently erase it from the system."
                )
            with col_del2:
                delete_click = st.button("❌ Erase Profile", type="primary")
                if delete_click and profile_to_delete:
                    delete_user_profile(profile_to_delete)
                    st.success(f"Profile '{profile_to_delete}' successfully deleted!")
                    time.sleep(0.5)
                    st.rerun()

        st.write("---")
        
        # Dial Room
        col_room1, col_room2 = st.columns([2, 1])
        
        with col_room1:
            st.markdown("""
            <div class="saas-card-dark" style='margin-bottom: 16px;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div style='display: flex; align-items: center;'>
                        <span class="icon" style="color: #EF4444; font-size: 20px;">fiber_manual_record</span>
                        <h3 style='margin: 0; color: white;'>Live Call Recording & AI Audit Mode</h3>
                    </div>
                    <span class="badge-premium" style="background: rgba(37,99,235,0.2); color:#3B82F6;">Session Active</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            initial_greeting = f"Yeah, this is {ui_persona if ui_persona else 'the owner'} speaking. I'm literally in the middle of something right now. Make it quick, what is this?"
            
            if not st.session_state.is_call_active:
                if st.button("📞 Start Interactive Practice Call", type="primary", use_container_width=True):
                    st.session_state.is_call_active = True
                    st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]
                    st.rerun()
            
            # Chat Container
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        {msg["content"]}
                        <div class="chat-meta">
                            <span class="icon" style="font-size: 14px;">person</span> Ikechukwu Onuekwusi
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-bubble-ai">
                        {msg["content"]}
                        <div class="chat-meta-ai">
                            <span class="chat-badge-coach">Prospect AI</span> {ui_persona.split(',')[0]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.session_state.is_call_active:
                user_msg = st.chat_input("Enter your sales response...")
                
                if user_msg:
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.rerun()
                    
    # 2. COLD CALL OPENER ARCHITECT
    with sub_tab_opener:
        st.subheader("🎯 Cold Call Opener Architect")
        col_op1, col_em2 = st.columns(2)
        with col_op1:
            op_product = st.text_input("My Product/Platform Name:", value=ui_industry, key="op_prod")
            op_persona = st.text_input("Target Customer Job Title:", value=ui_persona.split(',')[0], key="op_pers")
            op_framework = st.selectbox("Sales Framework Hook:", ["Sandler (Empathy & Permission)", "Challenger (Disruptive State)", "Collaborative (Low-Pressure Permission)"], key="op_frame")
        with col_em2:
            st.write("### Generated Outbound Opening Line")
            if st.button("✨ Architect Opening Hook", type="primary", use_container_width=True, key="op_btn"):
                with st.spinner("AI is engineering your hook..."):
                    time.sleep(0.8)
                    
                    if op_framework == "Sandler (Empathy & Permission)":
                        script_text = f"\"Hey {op_persona.split()[0] if op_persona else '[Name]'}, I know you weren't expecting my call and you're probably in the middle of something. I promise to be brief. Do you have 30 seconds for me to tell you why I called, and you can tell me if we should hang up?\""
                    elif op_framework == "Challenger (Disruptive State)":
                        script_text = f"\"Hey {op_persona.split()[0] if op_persona else '[Name]'}, I'm calling because most managers in your industry tell us they are wasting 10 hours a week on manual admin work. We built {op_product if op_product else '[My Product]'} to automate that in 1 click. Are you experiencing that administrative bottleneck too?\""
                    else:
                        script_text = f"\"Hey {op_persona.split()[0] if op_persona else '[Name]'}, I was looking at your recent operations. I won't give you a long pitch. I just wanted to share how similar teams are using {op_product if op_product else '[My Product]'} to solve their scheduling friction. Do you have 30 seconds for a quick permission check?\""
                    
                    st.info(f"**Opening Line Script:**\n\n{script_text}")

    # 3. CONSULTATIVE DISCOVERY GENERATOR
    with sub_tab_discovery:
        st.subheader("💡 Consultative SPIN Discovery Question Generator")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            d_ind = st.text_input("Prospect Industry/Field:", value=ui_industry, key="disc_ind")
            d_pain = st.text_input("Primary Problem/Pain Point:", value="Late-night administrative paperwork backlog", key="disc_pain")
            d_generate = st.button("🚀 Generate Discovery Matrix", type="primary", key="disc_btn")
        with col_d2:
            if d_generate:
                with st.spinner("Generating consultative discovery playbook..."):
                    time.sleep(1.0)
                    st.markdown(
                        f"""
                        ### 💡 Consultative SPIN Discovery Playbook
                        *   **Situation Question (Fact-finding):**
                            *   *\"How are you currently managing and tracking your {d_ind.lower() if d_ind else 'operational'} invoicing and dispatcher schedules?\"*
                        *   **Problem Question (Uncovering pain):**
                            *   *\"Where do you find that your team experiences the most friction or delays in logging field sheets or receipts?\"*
                        *   **Implication Question (Driving urgency & financial impact):**
                            *   *\"When technicians forget to charge for extra parts or write sloppy field notes, how much unbilled revenue is that leaking every month? Is that forcing you to spend your evenings doing manual double-entry into QuickBooks?\"*
                        *   **Need-Payoff Question (Positioning value):**
                        *   *\"If we could automate that dispatch and invoicing directly from their phones in 30 seconds on-site, what would that do for your company's cashflow—and your own personal evenings?\"*
                        """
                    )

    # 4. PRE-CALL PREP SHEET PLANNER
    with sub_tab_precall:
        st.subheader("📝 Pre-Call Prep Sheet Planner")
        col_sh1, col_sh2 = st.columns(2)
        with col_sh1:
            sh_company = st.text_input("Target Account / Company Name:", value="Miller & Sons Mechanical", key="pre_comp")
            sh_lead = st.text_input("Target Decision Maker:", value=ui_persona, key="pre_lead")
            sh_goal = st.selectbox("Call Objective Goal:", ["Secure 10-Minute Demo Slot", "Uncover Current Software Competitor", "Bypass Gatekeeper to C-Suite"], key="pre_goal")
            sh_btn = st.button("📋 Compose Prep Sheet", type="primary", key="pre_btn")
        with col_sh2:
            if sh_btn:
                with st.spinner("Planning pre-call battle-sheet..."):
                    time.sleep(0.9)
                    st.markdown(
                        f"""
                        ### 📋 Pre-Call Preparation Sheet
                        *   **Account Target:** {sh_company}
                        *   **Prospect:** {sh_lead}
                        *   **Core Objective:** {sh_goal}
                        *   **Value-Proposition Map:**
                            *   *Feature Focus:* Simplicity, mobile driveway invoicing, 1-click QuickBooks ledger syncing.
                            *   *Pain Focus:* Late-night clerical work, lost paper invoice sheets, tech-refusal of complex apps.
                        *   **The Rebuttal Pivot (If they say \"Happy with Paper\"):**
                            *   *“I hear ya Bob, paper doesn't crash. But paper doesn't talk to QuickBooks instantly, and your admin is spending hours re-typing those sheets. We save trade owners 10 hours a week on that.”*
                        """
                    )

    # 5. OBJECTION BATTLECARDS
    with sub_tab_battlecards:
        st.subheader("🛡️ Outbound Objection Battlecards")
        obj_choice = st.selectbox("Select Objection Type:", ["I'm too busy, call me back / send an email.", "I use pen and paper / Excel and it works fine.", "We already use a competitor.", "I'm too small / don't need it."], key="battle_obj_select")
        
        if obj_choice == "I'm too busy, call me back / send an email.":
            st.markdown(
                """
                ### 🎯 Rebuttal Strategy: Busy Brush-off
                *   **Buyer Psychology:** Protective reflex to unscheduled phone interruptions. They assume you will waste 30 minutes reading dry slides.
                *   **Formula:** Acknowledge (A) + De-escalate (D) + Pivot (P) + Micro-Close (MC)
                *   **SDR Script Rebuttal:** 
                    > *"I completely hear you, [Name]. I'm catching you mid-run, so I'll let you get right back to it. Our clients use SalesFlow specifically to save their managers 10 hours of admin billing every week. I don't want to pitch you now. Can we grab just 10 minutes next Tuesday morning before your day starts, to see if it makes sense?"*
                """
            )
        elif obj_choice == "I use pen and paper / Excel and it works fine.":
            st.markdown(
                """
                ### 🎯 Rebuttal Strategy: Tech-Aversion / Pen & Paper
                *   **Buyer Psychology:** Fear of complexity and software setup. They assume software takes weeks to configure, and older techs will refuse to use it.
                *   **Formula:** Validate paper reliability + Uncover Cost of Whiteboard/Paper + Introduce simple contrast
                *   **SDR Script Rebuttal:**
                    > *"Pen and paper is 100% reliable, you are right. But paper doesn't talk to QuickBooks, and it's easy for technicians to forget to charge for extra parts. Our app is built to be as simple as sending a text message. Technicians do it in 20 seconds, and you get paid instantly. Let me show you a 5-minute comparison."*
                """
            )
        elif obj_choice == "We already use a competitor.":
            st.markdown(
                """
                ### 🎯 Rebuttal Strategy: Competitor Lock-in
                *   **Buyer Psychology:** Comfortable with current tools and dreads the friction of migrating data.
                *   **Formula:** Respect current competitor + Introduce key performance comparison + Low friction comparative overview
                *   **SDR Script Rebuttal:**
                    > *"They are a solid provider, absolutely. But what many managers find is that they use about 15% of the competitor's heavy features, but pay for 100% of their enterprise cost. Our system is built purely for simplicity. Your team can master it in 5 minutes with zero training, and it's half the price. Can I show you a 10-minute comparison next week?"*
                    """
            )
        else:
            st.markdown(
                """
                ### 🎯 Rebuttal Strategy: Small / Don't Need It
                *   **Buyer Psychology:** Perceives software as an enterprise-only cost, not a small-business administrative lifesaver.
                *   **Formula:** Reposition tool as virtual admin + Focus on growth scaling
                *   **SDR Script Rebuttal:**
                    > *"We actually built this specifically for small, scaling teams. When you're small, you don't have a full-time office admin, so you're doing double-duty as a rep and an accountant. Our tool acts as your virtual admin, automating text reminders and dispatching. It helps you look like a 50-person company and win more high-paying commercial contracts."*
                    """
                )

# ==================== MODULE B: GENERAL CLOSING & OUTREACH COPILOT ====================
elif active_module == "🤝 Module B: General Closing & Outreach Copilot (Face-to-Face, Email, SMS & Video)":
    
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <span class="icon" style="font-size: 28px; color: #7C3AED;">handshake</span>
        <h2 style='margin: 0;'>🤝 Module B: General Closing & Outreach Copilot</h2>
    </div>
    """, unsafe_allow_html=True)
    
    sub_tab_physical, sub_tab_optimizer, sub_tab_emails, sub_tab_sms, sub_tab_videos = st.tabs([
        "🤝 Face-to-Face Closing Planner",
        "✍️ AI Outbound Pitch Optimizer",
        "✉️ AI Outbound Email Composer",
        "💬 AI Text Response & SMS Writer",
        "🎬 AI Video Prospecting Script Studio"
    ])
    
    # 1. FACE-TO-FACE CLOSING PLANNER
    with sub_tab_physical:
        st.subheader("🤝 Face-to-Face Negotiation & Closing Planner")
        col_ph1, col_ph2 = st.columns(2)
        with col_ph1:
            ph_cust = st.text_input("Customer Name / Industry:", value=st.session_state.setup_persona, placeholder="e.g. Bob, Miller Plumbing Owner", key="ph_cust_inp")
            ph_product = st.text_input("Product Being Pitched:", value=st.session_state.setup_industry, placeholder="e.g. Jobtable Scheduling App", key="ph_prod_inp")
            ph_agenda = st.selectbox("Primary Meeting Agenda Goal:", ["Present Custom Proposal & Sign Contract", "On-site Technical Discovery Demo", "Overcome Skeptical Board Objections"], key="ph_agenda_select")
            ph_generate = st.button("📋 Compose Negotiation Battle-Plan", type="primary", key="ph_gen_btn")
        with col_ph2:
            if ph_generate:
                with st.spinner("AI is formulating your physical meeting guide..."):
                    time.sleep(0.9)
                    st.markdown(
                        f"""
                        ### 🤝 In-Person closing Battle-Plan: {ph_cust.split(',')[0] if ph_cust else 'Prospect'}
                        
                        #### 1. Meeting Agenda & Setup Flow
                        *   **Visual Opening Hook (Minutes 0-5):** Don't open with slides. Hold up a physical prop related to their pain (e.g. a receipt book, or a tablet with their competitor's schedule) to break the ice.
                        *   **Discovery Recap:** *\"Marcus/Bob, when we spoke on the phone, you mentioned that your biggest operational headache was late-night bookkeeping and lost material billings. Is that still your #1 barrier to scaling?\"*
                        *   **The consultative Demo (Minutes 5-20):** Focus purely on showing how {ph_product if ph_product else '[My Product]'} removes those 2 specific pains. Speak plain English, let them touch the tablet/phone themselves.
                        
                        #### 2. Body-Language & Rapport Triggers
                        *   **Mirroring Energy:** If they are gruff, speak slow and direct. If they are analytical, show data tables.
                        *   **Handling the 'Skeptical Folded Arms':** Change the focal point of the room. Hand them your tablet or product brochure so they are forced to unfold their arms to receive it.
                        
                        #### 3. High-Conversion Close Strategy
                        *   **The Alternative Close:** *\"Bob, do you want our implementation team to set up your account syncing with QuickBooks on Tuesday afternoon, or would Wednesday morning fit your calendar better?\"*
                        *   **The Risk-Free Nudge:** *\"We don't lock you into long annual contracts. We do a simple monthly license because we are confident our tool will save you 10 hours this week alone. Let's get your first crew loaded today.\"*
                        """
                    )

    # 2. AI OUTBOUND PITCH OPTIMIZER
    with sub_tab_optimizer:
        st.subheader("✍️ Outbound Pitch & Script Optimizer")
        raw_pitch = st.text_area("Paste Your Current Script/Pitch:", placeholder="e.g. Hello, I'm Ikechukwu from Jobtable. We have a great software for contractors that does dispatching, scheduling, and invoicing. It's really simple and cheap. Do you have time for a demo next week?", key="opt_text_area")
        
        if st.button("⚡ Optimize My Pitch", type="primary", use_container_width=True, key="opt_btn"):
            if not raw_pitch:
                st.error("Please paste your script to optimize!")
            else:
                with st.spinner("Analyzing vocabulary metrics and formatting hooks..."):
                    time.sleep(1.0)
                    st.markdown(
                        f"""
                        ### 🎯 Optimized Performance Analysis & Script
                        
                        #### 📊 Structural Performance Scorecard:
                        *   **The Hook:** `Weak` (Standard company introduction triggers immediate defensive sales filters).
                        *   **Language Jargon:** `Medium` (Avoid words like \"great software\" and \"cheap\"—replace with plain value terminology).
                        *   **Objection Recovery Flow:** `Low` (Pushed for a long meeting too early without validating their timing).
                        
                        #### 🛠️ AI Rewritten Outbound Script (Sandler/SPIN Hybrid):
                        > *"Hey [Prospect Name], I know you weren't expecting my call, and I'm probably catching you mid-run. I promise to be brief—do you have 30 seconds for me to tell you why I dialed, and you can tell me if we should hang up?*
                        > 
                        > *(Wait for agreement)*
                        > 
                        > *Most managers in your sector tell us they are spending 10+ hours a week handling manual paperwork late at night. We built our system to let teams invoice directly in 20 seconds, syncing everything in 1 click.*
                        > 
                        > *I won't pitch you over the phone. Can we grab just a low-friction 10-minute walkthrough next Tuesday morning before your day starts, to see if it makes sense?\"*
                        """
                    )

    # 3. AI OUTBOUND EMAIL COMPOSER
    with sub_tab_emails:
        st.subheader("✉️ Outbound AI Follow-up Email Composer")
        col_em1, col_em2 = st.columns(2)
        with col_em1:
            em_trade = st.text_input("Target Customer Industry/Profile:", value=st.session_state.setup_industry, key="email_ind_text_b")
            em_objection = st.selectbox("Objection Handled on Call:", ["Too Busy / Working On-Site", "Paper works fine", "Too Expensive / Tight Budgets", "Happy with Current Competitor"], key="email_obj_select_b")
        with col_em2:
            em_date = st.text_input("Meeting Proposal Time:", value="Tuesday morning at 8:00 AM", key="email_date_text_b")
            em_generate = st.button("✨ Generate Email Sequence", type="primary", key="email_gen_btn_b")
            
        if em_generate:
            with st.spinner("AI is crafting your email sequence..."):
                time.sleep(1.0)
                st.markdown(
                    f"""
                    ### 📧 Recommended Email Template
                    **Subject:** 10 minutes to simplify your operations for {em_trade.lower() if em_trade else 'your company'} on Tuesday?
                    
                    Hi [Name],
                    
                    Great speaking with you briefly while you were on that job site today. I know you're busy running your crew, so I promised to keep this short.
                    
                    When we spoke, you mentioned that **{em_objection.lower()}**. I completely understand—many of the direct business owners we partner with felt the exact same way. 
                    
                    But they saw how our platform eliminates late-night paperwork and gets them paid in the driveway before their trucks start up, syncing everything instantly in one click.
                    
                    I won't pitch you over email. As agreed, let’s grab a quick 10-minute walkthrough on **{em_date}** so you can see how simple it is. 
                    
                    I have sent a calendar invite to your inbox. Speak then!
                    
                    Best,
                    
                    Ikechukwu Onuekwusi  
                    Outbound Sales Representative  
                    """
                )

    # 4. AI TEXT RESPONSE & SMS WRITER
    with sub_tab_sms:
        st.subheader("💬 AI Text Response & SMS Writer")
        sms_trade = st.text_input("Target Trade/Profession:", value="Plumbing", key="sms_trade_text_b")
        sms_pain = st.radio("Core Value Angle:", ["Reclaiming lost material charges", "Getting paid in the driveway (cashflow)", "Whiteboard scheduling headaches", "Bypassing night-time admin work"], key="sms_pain_radio_b")
        
        if st.button("📱 Generate Outbound SMS", key="sms_gen_btn_b"):
            with st.spinner("AI is drafting your SMS response..."):
                time.sleep(0.8)
                
                if sms_pain == "Reclaiming lost material charges":
                    sms_text = f"Hey [Name], completely hear you! Real quick: average {sms_trade.lower() if sms_trade else 'business'} crews lose $500/mo in parts they forget to charge for. Our app makes it as simple as texting for techs to log materials on-site, protecting your margins. Grab 5 mins next Tuesday morning? - Ikechukwu Onuekwusi"
                elif sms_pain == "Getting paid in the driveway (cashflow)":
                    sms_text = f"Hey [Name], no worries! Teams use our app to take card payments directly in the field as soon as the {sms_trade.lower() if sms_trade else 'business'} job is done. Average company boosts cashflow by 20%. Grab 5 mins Tuesday morning before your first run? - Ikechukwu Onuekwusi"
                elif sms_pain == "Whiteboard scheduling headaches":
                    sms_text = f"Hey [Name], hear ya! Whiteboards and texts make scheduling {sms_trade.lower() if sms_trade else 'business'} jobs a total puzzle. Our system is a drag-and-drop map app your guys master in 5 mins. Reclaim your office sanity. Grab 10 mins Tuesday morning? - Ikechukwu Onuekwusi"
                else:
                    sms_text = f"Hey [Name], understand! Most {sms_trade.lower() if sms_trade else 'business'} owners spend their evenings doing manual invoices and double-entering administrative data. Our system automates that so you get your nights back. Reclaim 10 hrs/week. Grab 10 mins Tuesday morning? - Ikechukwu Onuekwusi"
                
                st.write("---")
                st.info(f"**Copy & Send:**\n\n`{sms_text}`")

    # 5. AI VIDEO PROSPECTING SCRIPT STUDIO
    with sub_tab_videos:
        st.subheader("🎬 AI Video Prospecting Script Studio")
        vid_trade = st.text_input("Trade Target Group:", value="Plumbing", key="video_trade_text_b")
        vid_prop = st.text_input("Physical Prop in Video (e.g. Copper pipeline elbow, receipt book, mobile phone):", value="Copper pipeline joint", key="video_prop_text_b")
        
        if st.button("🎬 Generate Video Storyboard", key="video_gen_btn_b"):
            with st.spinner("AI is storyboarding your video pitch..."):
                time.sleep(1.0)
                st.markdown(
                    f"""
                    ### 📹 60-Second Video Script: '{vid_prop}' Pattern
                    
                    *   **[0:00 - 0:10] THE HOOK (Direct & Visual):**
                        *   *Visual:* Hold the **{vid_prop}** directly in front of the camera, then pull it back to show your face.
                        *   *Audio:* *"Hey [Name], I’m holding a simple {vid_prop} here in my hand. It costs about $4, but when your field techs forget to charge for just three of these on their paper tickets, you lose $500 in profits every single month."*
                    *   **[0:10 - 0:35] THE AGITATION:**
                        *   *Audio:* *"I’m Ikechukwu, an outbound representative. Because I have supervised field setups in the field myself, I know how hard it is to get crews to log materials accurately on paper sheets late at night."*
                    *   **[0:35 - 0:50] THE SIMPLE SOLUTION:**
                        *   *Audio:* *"That’s why trade veterans built our platform. It is an extremely simple app. Techs click the exact parts they used on site, and it automatically updates the invoice and syncs instantly. Your crew will master it in 5 minutes."*
                    *   **[0:50 - 1:00] THE CALL-TO-ACTION:**
                        *   *Audio:* *"I won't pitch you further over email. Reply to this message, and let's grab just 10 minutes next week Tuesday to see if it makes sense. Have a great day!"*
                        """
                )

# ==================== MODULE C: SALES ACADEMY & INDUSTRY ONBOARDING HUB ====================
elif active_module == "🎓 Module C: Sales Academy & Industry Onboarding Hub (ABC Industry Guides & Tests)":
    
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <span class="icon" style="font-size: 28px; color: #10B981;">school</span>
        <h2 style='margin: 0;'>🎓 Module C: Sales Academy & Industry Onboarding Hub</h2>
    </div>
    """, unsafe_allow_html=True)
    
    sub_tab_academy, sub_tab_test, sub_tab_history = st.tabs([
        "📖 Industry Onboarding Guides (ABCs)",
        "📝 Test Room (Questions & Answers)",
        "📜 My Quiz Performance History"
    ])
    
    academy_industry = st.session_state.setup_industry if st.session_state.setup_industry else "Your Configured Target Market"
    
    # 1. INDUSTRY ONBOARDING GUIDES (ABCs)
    with sub_tab_academy:
        st.subheader(f"📖 Mastering {academy_industry} from Scratch")
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            st.markdown(
                f"""
                ### 🎨 Section 1: The B2B Onboarding ABCs (Universal Guide)
                *   **How B2B Businesses Make Money:** B2B organizations generate revenue by solving distinct, recurring problems for their target clients. They live and die by client retention, operational velocity, and margin protection.
                *   **Understanding the Buying Committee:** In any B2B sale, you are rarely dealing with just one person. You have **End Users** (who care about daily simplicity), **Project Managers** (who care about delivery timelines), and **C-Suite/CFOs** (who care strictly about cost-savings and return on investment).
                *   **The Daily Operational Grind:** Executives and site managers are constantly bombarded by operations issues, crew constraints, and strict deadlines. Your cold outreach must respect this busy operational clock.
                
                ### 🛠️ Section 2: Key Business Terminology
                *   **Material Takeoff / Audit:** Calculating the exact resource specifications required before launching a major commercial contract.
                *   **Gross Margin %:** The financial difference between product acquisition cost and target resale value.
                *   **Operational Bottlenecks:** Manual, repetitive clerical tasks (spreadsheets, paper tracking) that slow down billing and eat active profit margins.
                """
            )
        with col_l2:
            st.markdown(
                f"""
                ### ⚠️ Section 3: Core Administrative Bottlenecks
                1.  **Revenue Leakage:** Employees or crews forgetting to log minor costs, parts used on site, or billable hours, leading to thousands in unlogged losses.
                2.  **Scheduling & Dispatch Friction:** whiteboards and manual text coordination leading to late arrivals, double-bookings, and client friction.
                3.  **Late Accounts Receivable:** Waiting weeks for customers to manually process invoices, creating major cashflow constraints.
                
                ### ⭐ Section 4: \"The Universal Fab Five\" Sales Rules
                *   **Rule 1:** *Speak to their reputation.* Buyers care about their reviews and client portfolios. Frame your product as their ultimate reputation-builder.
                *   **Rule 2:** *Target administrative pain early.* Speak directly to manual, back-office double-entry late at night.
                *   **Rule 3:** *Respect their timing.* Acknowledge they are busy running operations immediately upon starting a call.
                *   **Rule 4:** *Keep your language plain.* Ditch the heavy software jargon. Describe your product simply, like describing a truck.
                *   **Rule 5:** *Keep the call-to-action low risk.* Propose a short, 10-minute comparison, never a heavy 1-hour slides presentation.
                """
            )
            
        # DYNAMIC VIDEO & BLOG MEDIA LINK HUB
        st.write("---")
        st.write("### 📺 Visual & Practical Study Hub (Media Resources)")
        col_media1, col_media2 = st.columns(2)
        with col_media1:
            st.markdown(
                """
                **🎥 Highly Curated Video Masterclasses:**
                *   **[YouTube Masterclass] B2B Sales Prospecting & Empathy Hooks**  
                    *Visual lessons on B2B active listening, consultative openings, and handling high-friction enterprise brush-offs.*  
                    [👉 Watch Sales Coach Tutorial](https://www.youtube.com/)
                *   **[YouTube Masterclass] Y-Combinator School: Understanding Product Market Fit**  
                    *Learn how founders and sales leaders audit their client niches and find their #1 target pains.*  
                    [👉 Watch Startup School Lessons](https://www.youtube.com/@ycombinator)
                """
            )
        with col_media2:
            st.markdown(
                """
                **📚 Deep-Dive Articles & Blogs:**
                *   **[Industry Blog] Harvard Business Review (HBR): Mastering Consultative B2B Selling**  
                    *How elite modern sales professionals use SPIN and Challenger frameworks to drive deal velocity.*  
                    [👉 Read Sales Articles on HBR](https://hbr.org/)
                *   **[Industry Blog] HubSpot Sales Academy: Understanding the Modern B2B Customer Journey**  
                    *How to conduct thorough research, map accounts, and bypass gatekeepers to speak directly to the C-suite.*  
                    [👉 Read B2B Sales Blog](https://blog.hubspot.com/sales)
                """
            )

    # 2. TEST ROOM (QUESTIONS & ANSWERS)
    with sub_tab_test:
        st.subheader("📝 Adaptive Sales Certification & Testing")
        col_t1, col_t2 = st.columns([1, 1])
        
        with col_t1:
            quiz_track = st.selectbox(
                "Select Certification Track:",
                ["Industry Domain Knowledge Track", "Outbound Sales & Objections Track", "Mixed Mode Track (Expert Certification)"]
            )
            quiz_difficulty = st.selectbox(
                "Select Difficulty Level:",
                ["Easy", "Medium", "Difficult"]
            )
            
            st.write("---")
            st.write("### 📝 Certification Exam Sheet")
            
            if quiz_track == "Industry Domain Knowledge Track":
                if quiz_difficulty == "Easy":
                    q1 = "1. What does the term 'Dispatching' represent in B2B field operations?"
                    a1_opts = ["Mailing paper newsletters", "Assigning and routing technical crews to customer sites", "Filing tax returns to the bank"]
                    q2 = "2. What is the standard accounting software most small-to-medium business owners utilize?"
                    a2_opts = ["Salesforce", "QuickBooks", "Microsoft Paint"]
                    correct_ans = [a1_opts[1], a2_opts[1]]
                elif quiz_difficulty == "Medium":
                    q1 = "1. What is 'Job Costing' in professional services?"
                    a1_opts = ["Sizing pipelines", "Calculating labor and material margins to ensure job profit", "Paying the rent for the warehouse"]
                    q2 = "2. What is a 'Change Order' or contract modification?"
                    a2_opts = ["Updating a customer's address", "Modifying the original contract scope on-site", "Replacing a technician's truck"]
                    correct_ans = [a1_opts[1], a2_opts[1]]
                else:
                    q1 = "1. Why is 'driveway invoicing' considered a critical cashflow metric?"
                    a1_opts = ["It makes the truck run faster", "It collects payments on-site immediately before the representative leaves", "It is required by state tax laws"]
                    q2 = "2. What represents the biggest source of inventory revenue leakage for small shops?"
                    a2_opts = ["Buying too many trucks", "Technicians forgetting to charge for parts used on-site", "Excessive marketing expenses"]
                    correct_ans = [a1_opts[1], a2_opts[1]]
                    
            elif quiz_track == "Outbound Sales & Objections Track":
                if quiz_difficulty == "Easy":
                    q1 = "1. When a prospect says 'I'm too busy,' what is the first thing an SDR should do?"
                    a1_opts = ["Argue and keep pitching", "Acknowledge their time constraints immediately", "Hang up the phone"]
                    q2 = "2. What is the standard time-commitment you should ask for on a cold call?"
                    a2_opts = ["A 1-hour deep slide presentation", "A quick 10-minute visual comparison walkthrough", "An on-site dinner meeting"]
                    correct_ans = [a1_opts[1], a2_opts[1]]
                elif quiz_difficulty == "Medium":
                    q1 = "1. What is the core psychology behind 'Send me an email'?"
                    a1_opts = ["They want to read your whitepaper", "It is a polite brush-off to end the call quickly", "They don't have internet access"]
                    q2 = "2. What is the best way to handle a competitor objection?"
                    a2_opts = ["Tell them their competitor is terrible", "Respect the current tool, but introduce key simplicity advantages", "Hang up"]
                    correct_ans = [a1_opts[1], a2_opts[1]]
                else:
                    q1 = "1. How do you bypass a defensive gatekeeper on an outbound call?"
                    a1_opts = ["Shout and act important", "Ask low-pressure questions with a confident, friendly peer-like tone", "Offer them a discount key"]
                    q2 = "2. What does 'Sandler low-pressure permission hook' represent?"
                    a2_opts = ["Asking for permission to speak for 30 seconds, disarming protective sales filters", "Sending a contract over SMS", "Bribing the prospect"]
                    correct_ans = [a1_opts[0], a2_opts[0]]
            else:
                # MIXED TRACK
                q1 = "1. What represents the cost-of-inaction (COI) for an organization staying with manual paperwhiteboards?"
                a1_opts = ["Wasted fuel costs", "Late nights rekeying data + double-booking team members", "Lower credit card processing rates"]
                q2 = "2. If a customer says 'We are happy with pen and paper,' how do you shift their mindset?"
                a2_opts = ["Validate paper reliability, then pivot to how paper wastes their late-night evenings", "Tell them paper is obsolete and illegal", "Offer them free software licenses"]
                correct_ans = [a1_opts[1], a2_opts[0]]

            # Render questions
            ans1 = st.radio(q1, a1_opts, key="quiz_q1_widget")
            ans2 = st.radio(q2, a2_opts, key="quiz_q2_widget")
            
            submit_quiz = st.button("🏁 Submit My Certification Quiz", type="primary", use_container_width=True)
            
        with col_t2:
            st.write("### 📊 Quiz Grading & Performance Report")
            if submit_quiz:
                score = 0
                mistakes = []
                
                if ans1 == correct_ans[0]:
                    score += 50
                else:
                    mistakes.append(f"Q1 Incorrect: You chose '{ans1}'. Correct answer was '{correct_ans[0]}'")
                    
                if ans2 == correct_ans[1]:
                    score += 50
                else:
                    mistakes.append(f"Q2 Incorrect: You chose '{ans2}'. Correct answer was '{correct_ans[1]}'")
                
                if score == 100:
                    st.balloons()
                    st.success(f"🏆 **100% PERFECT SCORE!** You scored 100/100 on the {quiz_difficulty} {quiz_track}!")
                elif score == 50:
                    st.warning(f"⚠️ **DECENT OUTCOME: 50/100.** You got 1 out of 2 questions correct on the {quiz_difficulty} tier.")
                else:
                    st.error(f"❌ **TRY AGAIN: 0/100.** You missed both questions. Read the ABC Onboarding Guides and try again.")
                    
                history_entry = {
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Industry Context": academy_industry,
                    "Track": quiz_track,
                    "Difficulty": quiz_difficulty,
                    "Score": f"{score}/100",
                    "Status": "Passed" if score >= 100 else "Requires Review",
                    "Mistakes Summary": ", ".join(mistakes) if mistakes else "None! Perfect Score."
                }
                st.session_state.quiz_history.append(history_entry)
                st.success("Performance result logged in your private study history log!")

    # 3. MY QUIZ PERFORMANCE HISTORY
    with sub_tab_history:
        st.subheader("📜 My Private Study History Log")
        st.write("Use this logs database to trace your incorrect answers, analyze structural sales mistakes, and catch up to speed:")
        
        if not st.session_state.quiz_history:
            st.info("💡 **History Log is empty.** Take a certification test under the 'Test Room' tab to record and audit your performance.")
        else:
            history_df = pd.DataFrame(st.session_state.quiz_history)
            st.dataframe(history_df, use_container_width=True)
            st.info("💡 **SDR Tip:** Use the Mistakes Summary column to pinpoint your exact terminology and rebuttal gap, and practice them in the Outbound Practice Room!")
# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed & Built by Ikechukwu Onuekwusi | SalesFlow AI Enterprise Hub ⚡</p>", unsafe_allow_html=True)
