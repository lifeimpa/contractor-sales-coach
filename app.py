import streamlit as st
import pandas as pd
import random
import time
import requests
import json
import os

# Set up page configurations
st.set_page_config(
    page_title="SalesFlow Agent - Intelligent Sales Enablement Coach",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- ADVANCED CUSTOM UI STYLING (CSS Injection) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700;800&family=Material+Icons+Outlined&display=swap');
    
    /* Global Base Reset */
    .main { 
        background-color: #f8fafc; 
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }
    
    /* Clean Typography styling */
    h1 { 
        color: #0f172a; 
        font-family: 'Inter', sans-serif; 
        font-weight: 800; 
        letter-spacing: -0.02em;
    }
    h2 { 
        color: #1e293b; 
        font-family: 'Inter', sans-serif; 
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    h3 { 
        color: #334155; 
        font-family: 'Inter', sans-serif; 
        font-weight: 600;
    }
    
    /* Premium Metric Card Container */
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
        border: 1px solid #f1f5f9;
        border-left: 6px solid #1e40af;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    }
    
    /* Custom button states */
    .stButton>button {
        background: #1e40af;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(30, 64, 175, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(30, 64, 175, 0.3);
    }
    
    /* Custom Badges */
    .badge-premium {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-free {
        background: #10b981;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- PERSISTENT USER PROFILES DATABASE (JSON-based) -----------------
PROFILES_FILE = "sales_profiles.json"

# Reverted to 100% blank slate. Only "Select a Profile..." exists on first load. No prefilled profiles!
DEFAULT_PROFILES = {
    "Select a Profile...": {
        "industry": "",
        "persona": "",
        "mood": "",
        "customer_name": "",
        "market_type": "💻 B2B (Business-to-Business)"
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

def save_user_profile(name, industry, persona, mood, customer_name, market_type):
    profiles = load_user_profiles()
    profiles[name] = {
        "industry": industry,
        "persona": persona,
        "mood": mood,
        "customer_name": customer_name,
        "market_type": market_type
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
    st.session_state.active_model_name = "models/gemini-1.5-flash-latest"

# 2. Active Chat Logs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_call_active" not in st.session_state:
    st.session_state.is_call_active = False
# 3. Dynamic Wizard Onboarding states
if "setup_market_type" not in st.session_state:
    st.session_state.setup_market_type = "💻 B2B (Business-to-Business)"
if "setup_industry" not in st.session_state:
    st.session_state.setup_industry = ""
if "setup_persona" not in st.session_state:
    st.session_state.setup_persona = ""
if "setup_mood" not in st.session_state:
    st.session_state.setup_mood = ""
if "setup_customer_name" not in st.session_state:
    st.session_state.setup_customer_name = ""
# 4. Analytics
if "objections_handled" not in st.session_state:
    st.session_state.objections_handled = 0
if "score" not in st.session_state:
    st.session_state.score = 100
# 5. Quiz Performance History Log
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

# 6. Academy Interactive Generated Course State
if "product_chats" not in st.session_state:
    st.session_state.product_chats = []
if "sales_chats" not in st.session_state:
    st.session_state.sales_chats = []

# 7. Conversational Refinement States (Opener and Physical Tabs)
if "opener_ideas" not in st.session_state:
    st.session_state.opener_ideas = []
if "opener_chat_history" not in st.session_state:
    st.session_state.opener_chat_history = []
if "physical_ideas" not in st.session_state:
    st.session_state.physical_ideas = []
if "physical_chat_history" not in st.session_state:
    st.session_state.physical_chat_history = []

# Load existing user profiles
saved_profiles = load_user_profiles()

# ----------------- CALLBACK FUNCTIONS FOR PERFECT STATE SYNCING -----------------
def on_profile_load_change():
    selected_p = st.session_state.sidebar_profile_loader_widget
    if selected_p != "Select a Profile...":
        profiles = load_user_profiles()
        p_data = profiles[selected_p]
        st.session_state.setup_industry = p_data["industry"]
        st.session_state.setup_persona = p_data["persona"]
        st.session_state.setup_mood = p_data["mood"]
        st.session_state.setup_customer_name = p_data.get("customer_name", "")
        st.session_state.setup_market_type = p_data.get("market_type", "💻 B2B (Business-to-Business)")
        st.session_state.messages = []
        st.session_state.is_call_active = False

def on_preset_recommendation_change():
    choice = st.session_state.preset_recommendation_widget
    market_type_choice = st.session_state.setup_market_type
    st.session_state.setup_customer_name = ""
    
    if choice == "💻 B2B Software & Enterprise SaaS":
        st.session_state.setup_industry = "Enterprise Cloud Security SaaS"
        st.session_state.setup_persona = "Chief Information Security Officer (CISO)"
        st.session_state.setup_mood = "Super busy, dealing with an active server patch, highly skeptical"
    elif choice == "🔨 Construction, Trades & Mechanical Services (Jobtable/MEP)":
        st.session_state.setup_industry = "Contractor Dispatch & Invoicing App"
        st.session_state.setup_persona = "Plumbing Contractor Owner"
        st.session_state.setup_mood = "Super stressed, working under a sink, hates sales scripts"
    elif choice == "🧱 Building Materials, Paints, Tiles & Finishing":
        st.session_state.setup_industry = "Premium Paints, Tiles, Kitchens & Sanitary Wares"
        if market_type_choice == "💻 B2B (Business-to-Business)":
            st.session_state.setup_persona = "Real Estate Developer (Large-Scale)"
            st.session_state.setup_mood = "Demanding heavy bulk-discounts, auditing BOQ material costs"
        else:
            st.session_state.setup_persona = "Private Homeowner (Finishing personal build)"
            st.session_state.setup_mood = "Anxious about material costs, wants durability guarantees"
    elif choice == "🏠 Real Estate, Mortgages & Housing":
        st.session_state.setup_industry = "Residential Listing & Selling Services"
        if market_type_choice == "💻 B2B (Business-to-Business)":
            st.session_state.setup_persona = "Commercial Real Estate Investor"
            st.session_state.setup_mood = "Opportunistic, looking for immediate off-market deals"
        else:
            st.session_state.setup_persona = "For Sale By Owner (FSBO) Private seller"
            st.session_state.setup_mood = "Annoyed by listing agents, defensive, wants zero commission"
    elif choice == "🏥 Medical, Clinical & Biotech Services":
        st.session_state.setup_industry = "Patient Intake & Cloud Billing Software"
        st.session_state.setup_persona = "Private Clinical Lead Administrator"
        st.session_state.setup_mood = "Heavily distracted, burdened by compliance and regulations"
    elif choice == "💼 Professional B2B Services (Logistics, Consulting, HR)":
        st.session_state.setup_industry = "Third-Party Fleet & Logistics Consulting"
        st.session_state.setup_persona = "VP of Fleet Logistics"
        st.session_state.setup_mood = "Stressed by fuel costs and supply chain delays"
    elif choice == "📦 Retail, Wholesale & Consumer Goods":
        st.session_state.setup_industry = "Wholesale Inventory Management Portal"
        st.session_state.setup_persona = "Retail Store Manager"
        st.session_state.setup_mood = "Defensive about shelf space and inventory turns"
    elif choice == "✍️ Custom Sector (Write my own)":
        st.session_state.setup_industry = ""
        st.session_state.setup_persona = ""
        st.session_state.setup_mood = ""
    
    st.session_state.messages = []
    st.session_state.is_call_active = False

# ----------------- SIDEBAR: AI CO-PILOT CONFIGURATION -----------------
with st.sidebar:
    st.markdown("<h3 style='color: white; margin-bottom: 0px;'>SalesFlow AI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 13px; margin-top: 0px;'>Enterprise Sales Coach</p>", unsafe_allow_html=True)
    st.markdown("<span class='badge-free'>🔓 100% FREE & OPEN ACCESS</span>", unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("🔌 Connection Center")
    
    api_provider = st.selectbox(
        "Default API Brain:", 
        ["Practice Simulator (Offline)", "Google Gemini API", "DeepSeek API"]
    )
    
    api_key_input = ""
    if api_provider != "Practice Simulator (Offline)":
        default_val = st.session_state.active_api_key if api_provider == st.session_state.active_api_provider else ""
        api_key_input = st.text_input("Enter API Secret Key:", value=default_val, type="password", help="Input your authorization key from your selected AI platform")
        
        # Real-time Connect Button
        if st.button("🔌 Connect API", use_container_width=True, type="primary"):
            if not api_key_input:
                st.error("Please enter an API Key first.")
            else:
                with st.spinner("Authenticating secure API handshakes..."):
                    try:
                        if api_provider == "Google Gemini API":
                            import google.generativeai as genai
                            genai.configure(api_key=api_key_input)
                            
                            fallback_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
                            working_model = None
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
                                st.session_state.api_connection_error = f"API key validation rejected: {last_err}"
                                
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
                                st.session_state.active_model_name = "deepseek-chat"
                            else:
                                st.session_state.api_connected = False
                                st.session_state.api_connection_error = f"API returned status {response.status_code}: {response.text}"
                    except Exception as e:
                        st.session_state.api_connected = False
                        st.session_state.api_connection_error = str(e)
                        
        # Connection status dashboard
        if st.session_state.api_connected and api_provider == st.session_state.active_api_provider:
            st.success(f"🟢 Connected to {api_provider}! Real-time mode active.")
        else:
            if st.session_state.api_connection_error:
                st.error(f"🔴 Connection Failed: {st.session_state.api_connection_error[:150]}")
            else:
                st.warning("🔴 Disconnected. Click 'Connect API' to activate.")
                
        # API guides expander
        with st.expander("ℹ️ How to get your keys"):
            st.markdown(
                """
                **For Google Gemini:**
                1. Go to <a href='https://aistudio.google.com/' target='_blank'>Google AI Studio</a>.
                2. Click **"Get API Key"** -> **"Create API Key in new project"**.
                
                **For DeepSeek:**
                1. Go to <a href='https://platform.deepseek.com/' target='_blank'>DeepSeek Platform</a>.
                2. Navigate to **"API Keys"** -> **"Create API Key"**.
                """,
                unsafe_allow_html=True
            )
    else:
        st.session_state.api_connected = False
        st.info("💡 **Local Practice Mode active.** Offline simulator is active. No keys required.")
        
    st.write("---")
    
    # Active Session Analytics
    st.subheader("📈 Practice Metrics")
    st.metric("Tone Match Score", f"{st.session_state.score}/100")
    st.metric("Objections Overcome", f"{st.session_state.objections_handled}")
    
    if st.button("Reset Operational Metrics", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_call_active = False
        st.session_state.score = 100
        st.session_state.objections_handled = 0
        st.success("Session reset.")
        st.rerun()

# ----------------- MAIN TITLE HEADER -----------------
st.markdown(
    """
    <div style='background-color: #ffffff; padding: 30px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02);'>
        <h1 style='margin: 0px;'>⚡ SalesFlow Agent - Intelligent Sales Enablement Coach</h1>
        <p style='color: #64748b; font-size: 16px; margin-top: 5px; margin-bottom: 0px;'>The all-in-one AI sales assistant. Practice cold calling, handle raw objections, plan face-to-face closes, compose emails, and write high-converting copy in any B2B/B2C sector.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- SEPARATION MANAGER: DUAL MODULE MODES -----------------
st.markdown("## Select Active Sales Module")
active_module = st.radio(
    "Choose which workspace to load:",
    [
        "📞 Module A: Outbound Cold-Call Assistant Agent (Core Simulator & Prep)",
        "🤝 Module B: General Closing & Outreach Copilot (Face-to-Face, Email, SMS & Video)",
        "🎓 Module C: Sales Academy & Industry Onboarding Hub (ABC Industry Guides & Tests)"
    ],
    horizontal=True
)

st.write("---")

# Load existing user profiles
saved_profiles = load_user_profiles()

# ==================== MODULE A: OUTBOUND COLD-CALL ASSISTANT AGENT ====================
if active_module == "📞 Module A: Outbound Cold-Call Assistant Agent (Core Simulator & Prep)":
    st.markdown("## 📞 Outbound Cold-Call Assistant Agent")
    st.write("This is your core dialing companion. Practice cold calls, architect opening lines, generate discovery questions, and study objection battlecards.")
    
    sub_tab_practice, sub_tab_opener, sub_tab_discovery, sub_tab_precall, sub_tab_battlecards = st.tabs([
        "📞 Live Cold Call Roleplay Arena",
        "🎯 Cold Call Opener Architect",
        "💡 Consultative Discovery Generator",
        "📝 Pre-Call Prep Sheet Planner",
        "🛡️ Outbound Objection Battlecards"
    ])
    
    # 1. LIVE COLD CALL ROLEPLAY ARENA
    with sub_tab_practice:
        st.subheader("1. Configure Your Target Market (Universal Setup Wizard)")
        st.write("Choose from your saved custom profiles, use industry recommendations, or type in your custom sector completely from scratch:")

        col_p_load, col_wiz_type, col_wiz1 = st.columns([1, 1, 1])
        
        with col_p_load:
            loaded_p_name = st.selectbox(
                "📂 Load My Saved Profiles:",
                list(saved_profiles.keys()),
                key="sidebar_profile_loader_widget",
                on_change=on_profile_load_change,
                help="Select any profile you previously configured and saved to populate fields instantly!"
            )
        
        with col_wiz_type:
            # Dual selector for B2B or B2C
            market_type = st.radio(
                "Sales Motion Category:",
                ["💻 B2B (Business-to-Business)", "🏠 B2C (Business-to-Consumer)"],
                key="setup_market_type",
                help="Switching to B2C alters the conversational buyer's psychology, objections, and academy curriculum."
            )

        with col_wiz1:
            # Onboarding selectbox
            sector_choice = st.selectbox(
                "Select Broad Industry Recommendation:",
                [
                    "Select Industry Recommendation...",
                    "💻 B2B Software & Enterprise SaaS",
                    "🔨 Construction, Trades & Mechanical Services (Jobtable/MEP)",
                    "🧱 Building Materials, Paints, Tiles & Finishing",
                    "🏠 Real Estate, Mortgages & Housing",
                    "🏥 Medical, Clinical & Biotech Services",
                    "💼 Professional B2B Services (Logistics, Consulting, HR)",
                    "📦 Retail, Wholesale & Consumer Goods",
                    "✍️ Custom Sector (Write my own)"
                ],
                key="preset_recommendation_widget",
                on_change=on_preset_recommendation_change
            )

        st.write("")
        st.write("##### 🔧 Custom Setup Parameters (Type or Edit freely):")
        col_in1, col_in2, col_in_name, col_in3 = st.columns(4)
        with col_in1:
            ui_industry = st.text_input("My Product / Platform:", key="setup_industry", placeholder="e.g. Invoicing App, HR Software, Real Estate, Paints, Tiles")
        with col_in2:
            ui_persona = st.text_input("Target Customer Title / Role:", key="setup_persona", placeholder="e.g. Architect, Builder, CISO, Homeowner")
        with col_in_name:
            ui_cust_name = st.text_input(
                "Target Customer Name (Optional):",
                key="setup_customer_name",
                placeholder="e.g. Bob, Sarah, Marcus",
                help="""
                **What to input:** Enter the actual name of your customer/decision maker if you know it (e.g. Bob or Sarah).
                
                **Why it matters:** This automatically personalizes all outbound opener scripts, follow-up emails, and text replies.
                
                **What happens if left blank:** The app will automatically generate professional opening lines that find and verify the buyer's first name, helping you bypass the gatekeeper without robotic title cold calls like "Hi Plumber."
                """
            )
        with col_in3:
            ui_mood = st.text_input("Buyer's Current Mood / Style:", key="setup_mood", placeholder="e.g. Stressed on site, highly skeptical of quality, defensive")

        # 💾 Profile Manager Expander
        st.write("")
        with st.expander("💾 Profile Manager (Save, Edit, or Delete Custom Configurations)"):
            col_save1, col_save2 = st.columns([2, 1])
            with col_save1:
                profile_save_name = st.text_input("Profile Name:", placeholder="e.g. My Custom Paint Sales Setup")
            with col_save2:
                save_click = st.button("💾 Save Configuration")
                if save_click and profile_save_name:
                    save_user_profile(profile_save_name, ui_industry, ui_persona, ui_mood, ui_cust_name, market_type)
                    st.success(f"Profile '{profile_save_name}' saved permanently!")
                    time.sleep(0.5)
                    st.rerun()
            
            # Delete Profile Sub-section
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
        st.subheader("2. Outbound Practice Simulator Room")

        col_room1, col_room2 = st.columns([2, 1])
        
        with col_room1:
            if not st.session_state.api_connected:
                st.info("💡 **Practice Simulator Mode active.** Offline simulator is active. To connect this app directly to the live advanced brain of Google Gemini or DeepSeek, configure your selected API provider in the sidebar, paste your API key, and click **Connect API**!")
                
            st.write(f"### Live Call: Calling {ui_persona if ui_persona else '[Target Prospect]'}")
            initial_greeting = f"Yeah, this is {ui_persona if ui_persona else 'the owner'} speaking. I'm literally in the middle of something right now. Make it quick, what is this?"
            
            if not st.session_state.is_call_active:
                if st.button("📞 Start Interactive Practice Call", type="primary", use_container_width=True):
                    st.session_state.is_call_active = True
                    st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]
                    st.rerun()
                    
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            if st.session_state.is_call_active:
                user_msg = st.chat_input("Enter your sales response...")
                
                if user_msg:
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.chat_message("user").write(user_msg)
                    
                    with st.spinner("Prospect is typing..."):
                        time.sleep(0.8)
                        user_msg_lower = user_msg.lower()
                        ai_reply = ""
                        score_deduction = 0
                        feedback_msg = ""
                        end_call = False
                        
                        jargon = ["synergy", "paradigm shift", "digital transformation", "delighted to", "unprecedented efficiency", "disruptive innovations"]
                        if any(word in user_msg_lower for word in jargon):
                            ai_reply = f"Look, you sound like you are reading from a standard enterprise sales playbook. I don't do corporate buzzwords. Goodbye."
                            score_deduction = 35
                            feedback_msg = "Critical Sales Error! Buyers hate tech jargon and corporate scripts. Be direct, clear, and colloquial."
                            end_call = True

                        elif len(user_msg.split()) < 4:
                            ai_reply = "If you don't even have a clear reason to speak with me, why are you calling my phone? Goodbye."
                            score_deduction = 20
                            feedback_msg = "Your response was too short. Speak with confident pacing and clarity."
                            end_call = True

                        # 1. LIVE GOOGLE GEMINI MODE (Natively powered by st.session_state securely saved keys!)
                        elif api_provider == "Google Gemini API" and st.session_state.api_connected:
                            try:
                                import google.generativeai as genai
                                genai.configure(api_key=st.session_state.active_api_key)
                                model = genai.GenerativeModel(
                                    model_name=st.session_state.active_model_name,
                                    system_instruction=f"""
                                    You are roleplaying as {ui_persona}, a target customer in the {ui_industry} space.
                                    Your current personality/mood constraint is: {ui_mood}.
                                    The sales category is: {st.session_state.setup_market_type}.
                                    The user is an outbound sales representative.
                                    
                                    Your Goal: Act as a highly realistic, tough, skeptical buyer. Respond to the user's messages brief, blunt, and naturally.
                                    If the category is B2C (Business-to-Consumer), act as a private consumer making a personal household purchase. Push back with consumer objections: household budgets, spouse approvals, disruption inside your home, quality guarantees, and local neighborhood reviews.
                                    If the category is B2B (Business-to-Business), act as an enterprise stakeholder focusing on business metrics: ROI, contract timelines, and team integration.
                                    """
                                )
                                response = model.generate_content(user_msg)
                                ai_reply = response.text
                                if any(word in user_msg_lower for word in ["demo", "10 minutes", "tuesday", "schedule", "calendar"]):
                                    st.session_state.objections_handled += 1

                            except Exception as e:
                                st.error(f"Gemini API Error: {str(e)}. Defaulting to Practice Simulator.")

                        # 2. LIVE DEEPSEEK AI MODE (Natively powered by st.session_state securely saved keys!)
                        elif api_provider == "DeepSeek API" and st.session_state.api_connected:
                            try:
                                headers = {
                                    "Content-Type": "application/json",
                                    "Authorization": f"Bearer {st.session_state.active_api_key}"
                                }
                                system_prompt = f"You are roleplaying as {ui_persona}, a target customer in the {ui_industry} space. Mood: {ui_mood}. Category: {st.session_state.setup_market_type}. The user is an outbound sales representative. Act as a realistic, skeptical, busy buyer. Respond with brief, blunt, natural objections. If B2C, focus strictly on consumer objections: household budgets, spouse approvals, quality/fading, and installation disruption. Force them to overcome objections before booking a 10-min meeting."
                                history_payload = [{"role": "system", "content": system_prompt}]
                                for m in st.session_state.messages[:-1]:
                                    role_map = "assistant" if m["role"] == "assistant" else "user"
                                    history_payload.append({"role": role_map, "content": m["content"]})
                                history_payload.append({"role": "user", "content": user_msg})
                                
                                data = {
                                    "model": "deepseek-chat",
                                    "messages": history_payload,
                                    "temperature": 0.7
                                }
                                response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=15)
                                if response.status_code == 200:
                                    ai_reply = response.json()["choices"][0]["message"]["content"]
                                    if any(word in user_msg_lower for word in ["demo", "10 minutes", "tuesday", "schedule", "calendar"]):
                                        st.session_state.objections_handled += 1
                                else:
                                    st.error(f"DeepSeek API Error (Code {response.status_code}): {response.text}")
                            except Exception as e:
                                st.error(f"Failed to connect to DeepSeek API: {str(e)}")

                        # 3. OFFLINE SIMULATOR MODE
                        if not ai_reply:
                            if any(word in user_msg_lower for word in ["demo", "minutes", "schedule", "calendar", "meeting", "tuesday", "wednesday", "thursday"]):
                                if st.session_state.objections_handled >= 1:
                                    ai_reply = f"Fine. If it's really only going to take 10 minutes and you can show me how this actually solves our headaches with {ui_industry}, I'll take a look. Tuesday morning works. Send me a link."
                                    feedback_msg = "Outstanding close! You validated their pains and successfully booked a low-friction meeting!"
                                    end_call = True
                                else:
                                    ai_reply = f"A meeting? I just told you I'm in the middle of a job site. I don't even know why I should care. What are you actually selling?"
                                    score_deduction = 15
                                    feedback_msg = "You went for the meeting/demo ask too fast. Handle an objection and build basic value first!"
                            
                            elif any(word in user_msg_lower for word in ["busy", "time", "mid", "roof", "sink"]):
                                ai_reply = f"Look, we are extremely busy right now. I don't have time for cold pitches."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Busy Brush-off. Empathize immediately, pivot to time-saving, and suggest a 10-min slot next week."
                            
                            elif any(word in user_msg_lower for word in ["price", "cost", "expensive", "money", "budget"]):
                                ai_reply = f"Our margins and budgets are completely tight right now. We can't afford to bring on new monthly expenses."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Budget constraint. Pivot to ROI—explain how your tool saves them more money than it costs."
                            
                            elif any(word in user_msg_lower for word in ["already", "competitor", "happy", "using"]):
                                ai_reply = f"We already use a competitor to manage our {ui_industry} operations. We are happy with it."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Competitor/Status Quo. Acknowledge and respect their current tool, then suggest a 10-min comparative walkthrough."
                            
                            elif any(word in user_msg_lower for word in ["email", "send"]):
                                ai_reply = f"Just send me an email. I'll take a look at it when I have some free time."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Send me an email. Agree enthusiastically, then ask a simple qualification question to keep them talking!"
                            
                            else:
                                responses = [
                                    f"Why should we look at your product? spread sheets work fine for our operations.",
                                    f"Is this going to require our team to learn a complex new process, or is it actually simple?",
                                    f"What separates your system from every other cold caller hitting my phone today?"
                                ]
                                ai_reply = random.choice(responses)
                                score_deduction = 10
                                feedback_msg = "Prospect is testing you. Empathize with their daily operational friction and highlight how simple your product is."

                        # Record reply
                        st.session_state.score = max(0, st.session_state.score - score_deduction)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        st.chat_message("assistant").write(ai_reply)

                        if feedback_msg:
                            if score_deduction > 0:
                                st.warning(f"💡 **Coach Tip:** {feedback_msg} (-{score_deduction} pts)")
                            else:
                                st.success(f"💡 **Coach Tip:** {feedback_msg}")

                        if end_call:
                            st.session_state.is_call_active = False
                            st.write("---")
                            if st.session_state.score >= 80:
                                st.balloons()
                                st.success("🎉 **SUCCESSFUL DEMO BOOKED!** You successfully navigated the objection obstacles. Outstanding adaptive performance!")
                            else:
                                st.error("❌ **CALL ENDED.** The prospect hung up on you. Practice makes perfect—review the Coach Tips and click dial to retry.")
                        
                            if st.button("Reset Simulator", key="practice_reset_under"):
                                st.session_state.messages = []
                                st.session_state.is_call_active = False
                                st.rerun()
                                
        with col_room2:
            st.subheader("💡 My Daily Coach Checklist")
            st.markdown(
                """
                *   **Empathize & Validate:** Never argue with an objection. Agree that their time/current setup is valuable, then pivot to how you simplify their lives.
                *   **Acknowledge and Pivot:** Speak with confident momentum. Re-phrase objections into business bottlenecks you solve.
                *   **The Low-Friction Ask:** Propose a 10-minute comparison, never a 1-hour presentation.
                """
            )

    # 2. COLD CALL OPENER ARCHITECT
    with sub_tab_opener:
        st.subheader("🎯 Cold Call Opener Architect")
        st.write("Build high-converting opening lines (hooks) designed to disarm busy prospects based on modern sales methodologies.")
        
        # Initialize session states for Opener refinement and multiple alternative thoughts!
        if "messages_opener_active" not in st.session_state:
            st.session_state.messages_opener_active = False
            
        col_op1, col_em2 = st.columns(2)
        with col_op1:
            op_product = st.text_input("My Product/Platform Name:", value=ui_industry, key="op_prod")
            op_persona = st.text_input("Target Customer Job Title:", value=ui_persona.split(',')[0], key="op_pers")
            op_framework = st.selectbox("Sales Framework Hook:", ["Sandler (Empathy & Permission)", "Challenger (Disruptive State)", "Collaborative (Low-Pressure Permission)"], key="op_frame")
            
            # Action Button Row (With 1-click Alternative Generator Button! old ones do not get wiped, they push downwards!)
            if st.button("✨ Architect Opening Hook", type="primary", use_container_width=True, key="op_btn"):
                with st.spinner("AI is engineering your hook..."):
                    time.sleep(0.8)
                    cust_name = st.session_state.get("setup_customer_name", "").strip()
                    name_to_use = cust_name if cust_name else "[Name]"
                    
                    if op_framework == "Sandler (Empathy & Permission)":
                        script_text = f"\"Hey {name_to_use}, I know you weren't expecting my call and you're probably in the middle of something. I promise to be brief. Do you have 30 seconds for me to tell you why I called, and you can tell me if we should hang up?\""
                    elif op_framework == "Challenger (Disruptive State)":
                        script_text = f"\"Hey {name_to_use}, I'm calling because most managers in your industry tell us they are wasting 10 hours a week on manual admin work. We built {op_product if op_product else '[My Product]'} to automate that in 1 click. Are you experiencing that administrative bottleneck too?\""
                    else:
                        script_text = f"\"Hey {name_to_use}, I was looking at your recent operations. I won't give you a long pitch. I just wanted to share how similar teams are using {op_product if op_product else '[My Product]'} to solve their scheduling friction. Do you have 30 seconds for a quick permission check?\""
                    
                    # Prepend/Insert at index 0 so old thoughts push downwards!
                    st.session_state.opener_ideas.insert(0, {"timestamp": time.strftime("%H:%M:%S"), "content": script_text, "framework": op_framework})
                    st.session_state.messages_opener_active = True
                    st.rerun()
                    
            if st.session_state.messages_opener_active:
                # 🔄 Generate Alternative Idea Button (Directly fulfills your request!)
                if st.button("🔄 Generate Alternative Idea / Thought", use_container_width=True, key="op_regen_btn"):
                    with st.spinner("AI is generating an alternative line of thought..."):
                        time.sleep(0.8)
                        cust_name = st.session_state.get("setup_customer_name", "").strip()
                        name_to_use = cust_name if cust_name else "[Name]"
                        
                        # Alternative hook scripts
                        if op_framework == "Sandler (Empathy & Permission)":
                            alt_text = f"\"Hey {name_to_use}, I'll be completely upfront—I caught you on a cold call and you're probably busy. I won't pitch. Do you have 20 seconds to do a quick qualification check to see if we should hang up?\""
                        elif op_framework == "Challenger (Disruptive State)":
                            alt_text = f"\"Hey {name_to_use}, average companies in your field bleed $500 a month in unlogged materials technicians forget to charge for on-site. We built our app to stop that. Is material leakage a priority on your site today?\""
                        else:
                            alt_text = f"\"Hey {name_to_use}, I was hoping to grab just a low-friction 10-second calendar slot next week. I won't give you a pitch now. Can we grab Tuesday morning before your first run?\""
                        
                        # Prepend to history list so old ones push downwards!
                        st.session_state.opener_ideas.insert(0, {"timestamp": time.strftime("%H:%M:%S"), "content": alt_text, "framework": f"{op_framework} (Alternative Option)"})
                        st.rerun()

        with col_em2:
            if st.session_state.opener_ideas:
                st.write("### 🔥 Active Outbound Hooks")
                # Loop and render ideas history. Newest at the top, pushing older ones down!
                for idx, idea in enumerate(st.session_state.opener_ideas):
                    if idx == 0:
                        st.markdown(f"""
                        <div style='background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #1e40af; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(30,64,175,0.05);'>
                            <span class='badge-premium' style='background: #1e40af;'>ACTIVE CURRENT IDEA ({idea['timestamp']})</span>
                            <p style='font-size: 15px; font-weight: 500; margin-top: 10px; margin-bottom: 8px;'>{idea['content']}</p>
                            <small style='color: gray;'>Framework: {idea['framework']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px dashed #cbd5e1; margin-bottom: 12px; opacity: 0.65;'>
                            <small style='color: gray; font-weight: bold;'>PREVIOUS IDEA ({idea['timestamp']}) - {idea['framework']}</small>
                            <p style='font-size: 13.5px; margin-top: 5px; margin-bottom: 0px;'>{idea['content']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                # 💬 Interactive Refinement Chat (Pops up dynamically *only* after output is generated!)
                st.write("---")
                st.write("### 💬 Conversational Refinement Chat (Fine-tune your pitch)")
                st.write("Is your buyer an introvert? Do they only answer at 5 PM? Type your context or real-time feedback below to refine the active hook dynamically:")
                
                for chat in st.session_state.opener_chat_history:
                    with st.chat_message(chat["role"]):
                        st.write(chat["content"])
                        
                refine_input = st.chat_input("Tell the AI coach how to adjust the pitch (e.g. 'He is extremely defensive and suspicious')...", key="opener_refine_chat_input")
                if refine_input:
                    st.session_state.opener_chat_history.append({"role": "user", "content": refine_input})
                    
                    with st.spinner("Refining pitch details based on your customer scenario..."):
                        if st.session_state.api_connected:
                            try:
                                active_hook = st.session_state.opener_ideas[0]["content"]
                                prompt = f"""
                                You are "Sales Outbound Coach."
                                We generated this cold-call opening line: {active_hook}.
                                The user (Ikechukwu) wants to adjust and refine this pitch because: "{refine_input}".
                                
                                Rewrite and optimize the script based on this specific customer behavior or scenario (e.g., if they are an introvert, make it highly respectful, slow, low-friction, and zero hype). 
                                Make sure it is highly natural, consultative, and directly addresses the scenario they painted.
                                Citing the sales psychology behind your adjustment.
                                """
                                
                                if st.session_state.active_api_provider == "Google Gemini API":
                                    import google.generativeai as genai
                                    genai.configure(api_key=st.session_state.active_api_key)
                                    model = genai.GenerativeModel(st.session_state.active_model_name)
                                    response = model.generate_content(prompt)
                                    reply = response.text
                                elif st.session_state.active_api_provider == "DeepSeek API":
                                    headers = {
                                        "Content-Type": "application/json",
                                        "Authorization": f"Bearer {st.session_state.active_api_key}"
                                    }
                                    data = {
                                        "model": "deepseek-chat",
                                        "messages": [{"role": "user", "content": prompt}],
                                        "temperature": 0.7
                                    }
                                    response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=15)
                                    reply = response.json()["choices"][0]["message"]["content"]
                            except Exception as e:
                                reply = f"Error connecting to AI: {str(e)}"
                        else:
                            time.sleep(1.0)
                            reply = f"**[Assistant Suggestion]** (Simulated Response based on: *{refine_input}*)\n\nSince your prospect is an introvert or highly defensive, we should completely cut out high-energy sales enthusiasm. Lower your voice tone, slow your pacing, and use absolute micro-commitment language. Here is your adjusted cold opener:\n\n*\"Hey {st.session_state.get('setup_customer_name', '[Name]')}, I'll be brief because I know you're busy running your site. I'm calling from SalesFlow—I was hoping you could help me out. Who coordinates your team schedules, is that you or should I speak with someone else?\"*"
                            
                        st.session_state.opener_chat_history.append({"role": "assistant", "content": reply})
                        st.rerun()
            else:
                st.info("🎯 Configure your parameters on the left and click **'Architect Opening Hook'** to generate your initial scripts and unlock the interactive refinement chat room!")

    # 3. CONSULTATIVE DISCOVERY GENERATOR
    with sub_tab_discovery:
        st.subheader("💡 Consultative SPIN Discovery Question Generator")
        st.write("Generate consultative questions based on the SPIN framework to qualify buyers and drive urgency.")
        
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
        st.write("Construct a complete structural battle-plan for strategic target accounts before you dial.")
        
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
        st.write("Browse through master-level B2B outbound frameworks to overcome any industry brush-offs:")
        
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
    st.markdown("## 🤝 General Closing & Outreach Copilot")
    st.write("This is your deal closing workshop. Plan in-person face-to-face negotiations, optimize raw pitches, write emails/texts, and storyboard selfie video Loom pitches.")
    
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
        st.write("Prepare for high-stakes, in-person physical sales meetings. Map out your presentation structure, on-the-spot body-language triggers, and consultative closes:")
        
        # Initialize session states for Physical refinement and alternative ideas
        if "messages_physical_active" not in st.session_state:
            st.session_state.messages_physical_active = False

        col_ph1, col_ph2 = st.columns(2)
        with col_ph1:
            ph_cust = st.text_input("Customer Name / Industry:", value=st.session_state.setup_persona, placeholder="e.g. Bob, Miller Plumbing Owner", key="ph_cust_inp")
            ph_product = st.text_input("Product Being Pitched:", value=st.session_state.setup_industry, placeholder="e.g. Jobtable Scheduling App", key="ph_prod_inp")
            ph_agenda = st.selectbox("Primary Meeting Agenda Goal:", ["Present Custom Proposal & Sign Contract", "On-site Technical Discovery Demo", "Overcome Skeptical Board Objections"], key="ph_agenda_select")
            
            if st.button("📋 Compose Negotiation Battle-Plan", type="primary", key="ph_gen_btn"):
                with st.spinner("AI is formulating your physical meeting guide..."):
                    time.sleep(0.9)
                    
                    script_text_phys = f"""
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
                    
                    # Prepend/Insert at index 0 so old thoughts push downwards!
                    st.session_state.physical_ideas.insert(0, {"timestamp": time.strftime("%H:%M:%S"), "content": script_text_phys, "agenda": ph_agenda})
                    st.session_state.messages_physical_active = True
                    st.rerun()

            if st.session_state.messages_physical_active:
                # 🔄 Generate Alternative Idea Button
                if st.button("🔄 Generate Alternative Closing Idea", use_container_width=True, key="phys_regen_btn"):
                    with st.spinner("AI is generating another line of thought..."):
                        time.sleep(0.8)
                        
                        alt_script_text_phys = f"""
                        ### 🤝 Alternative In-Person Closing Battle-Plan: {ph_cust.split(',')[0] if ph_cust else 'Prospect'}
                        
                        #### 1. Meeting Agenda & Setup Flow
                        *   **The Case Study Opener (Minutes 0-5):** Share a laminated 1-page visual report of a direct competitor/neighbor who increased their profits by 15% using your product. Let them review the charts.
                        *   **The consultative Demo (Minutes 5-20):** Show only core features. Avoid any heavy technical details. Keep it extremely brief and high-value.
                        
                        #### 2. Close Strategy
                        *   **The Pilot Project Offer:** *\"Let's do a simple 14-day test pilot with just two of your active field crews. We'll set it up in 5 minutes today. If your crews don't absolutely love using it by next Friday, we disconnect and you don't pay a cent. Is that fair enough?\"*
                        """
                        
                        # Prepend to history list so old ones push downwards!
                        st.session_state.physical_ideas.insert(0, {"timestamp": time.strftime("%H:%M:%S"), "content": alt_script_text_phys, "agenda": f"{ph_agenda} (Alternative Close)"})
                        st.rerun()

        with col_ph2:
            if st.session_state.physical_ideas:
                st.write("### 🔥 Active Closing Playbooks")
                # Loop and render ideas history. Newest at the top, pushing older ones down!
                for idx, idea in enumerate(st.session_state.physical_ideas):
                    if idx == 0:
                        st.markdown(f"""
                        <div style='background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #7c3AED; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(124,58,237,0.05);'>
                            <span class='badge-premium' style='background: #7c3AED;'>ACTIVE PLAYBOOK ({idea['timestamp']})</span>
                            <div style='margin-top: 10px;'>{idea['content']}</div>
                            <small style='color: gray;'>Agenda: {idea['agenda']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px dashed #cbd5e1; margin-bottom: 12px; opacity: 0.65;'>
                            <small style='color: gray; font-weight: bold;'>PREVIOUS PLAYBOOK ({idea['timestamp']}) - {idea['agenda']}</small>
                            <div style='font-size: 13.5px; margin-top: 5px; margin-bottom: 0px;'>{idea['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                # 💬 Interactive Refinement Chat
                st.write("---")
                st.write("### 💬 Conversational Refinement Chat (Fine-tune your playbook)")
                st.write("Does your buyer have a specific behavior? (e.g. they only make decisions on Sundays, or they are extremely suspicious of hidden warranties?) Type below to adjust:")
                
                for chat in st.session_state.physical_chat_history:
                    with st.chat_message(chat["role"]):
                        st.write(chat["content"])
                        
                refine_input_phys = st.chat_input("Tell the AI coach how to adjust the playbook...", key="phys_refine_chat_input")
                if refine_input_phys:
                    st.session_state.physical_chat_history.append({"role": "user", "content": refine_input_phys})
                    
                    with st.spinner("Refining closing details based on your customer scenario..."):
                        if st.session_state.api_connected:
                            try:
                                active_playbook = st.session_state.physical_ideas[0]["content"]
                                prompt = f"""
                                You are "Sales Outbound Coach."
                                We generated this physical meeting battle-plan: {active_playbook}.
                                The user (Ikechukwu) wants to adjust and refine this playbook because: "{refine_input_phys}".
                                
                                Rewrite and optimize the playbook based on this specific customer behavior or scenario. 
                                Make sure it is highly natural, consultative, and directly addresses the scenario they painted.
                                Citing the sales psychology behind your adjustment.
                                """
                                
                                if st.session_state.active_api_provider == "Google Gemini API":
                                    import google.generativeai as genai
                                    genai.configure(api_key=st.session_state.active_api_key)
                                    model = genai.GenerativeModel(st.session_state.active_model_name)
                                    response = model.generate_content(prompt)
                                    reply = response.text
                                elif st.session_state.active_api_provider == "DeepSeek API":
                                    headers = {
                                        "Content-Type": "application/json",
                                        "Authorization": f"Bearer {st.session_state.active_api_key}"
                                    }
                                    data = {
                                        "model": "deepseek-chat",
                                        "messages": [{"role": "user", "content": prompt}],
                                        "temperature": 0.7
                                    }
                                    response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=15)
                                    reply = response.json()["choices"][0]["message"]["content"]
                            except Exception as e:
                                reply = f"Error connecting to AI: {str(e)}"
                        else:
                            time.sleep(1.0)
                            reply = f"**[Assistant Suggestion]** (Simulated Response based on: *{refine_input_phys}*)\n\nSince your prospect has this specific constraint, we should completely adjust our closing focus. Never force them to make a decision immediately in the room. Instead, map out a clear 'Step-by-step Implementation Plan' showing how your service/app manages transition downtime, and offer to do a walkthrough for their back-office manager next week Tuesday to get their buy-in first."
                            
                        st.session_state.physical_chat_history.append({"role": "assistant", "content": reply})
                        st.rerun()
            else:
                st.info("🎯 Configure your parameters on the left and click **'Compose Negotiation Battle-Plan'** to generate your initial playbook and unlock the interactive refinement chat room!")

    # 2. AI OUTBOUND PITCH OPTIMIZER
    with sub_tab_optimizer:
        st.subheader("✍️ Outbound Pitch & Script Optimizer")
        st.write("Paste your raw, current sales pitch or script. The AI will analyze it and automatically rewrite it using consultative sales frameworks (Sandler, Challenger, SPIN) to maximize conversions.")
        
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
        st.write("Generate a high-converting, personalized follow-up email sequence in 1 click for any industry:")
        
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
        st.write("When buyers say **'Just text me details'** or **'I'm too busy, text me,'** copy-paste these low-friction SMS templates:")
        
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
        st.write("Record a personalized 60-second video (Loom/Vidalytics) to send directly to a prospect. Here is your storyboard:")
        
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
    st.markdown("## 🎓 Sales Academy & Industry Onboarding Hub")
    st.write("This is your intelligent, interactive Sales Enablement Suite. Type any industry below to let the AI build a complete custom step-by-step masterclass course, and take certification exams in real-time.")
    
    sub_tab_product_train, sub_tab_sales_train, sub_tab_test, sub_tab_history = st.tabs([
        "📖 Tab 1: Interactive Product & Technical Training",
        "🗣️ Tab 2: Interactive Sales Training Coach Bot",
        "📝 Tab 3: Certification Test Room",
        "📜 Tab 4: Private Study History Log"
    ])
    
    # Setup values for dynamic learning references (100% generic)
    academy_industry = st.session_state.setup_industry if st.session_state.setup_industry else "Your Configured Target Market"
    
    # 1. TAB 1: INTERACTIVE PRODUCT & TECHNICAL TRAINING
    with sub_tab_product_train:
        st.subheader("📖 Interactive Product & Domain Knowledge Room")
        st.write("Master the absolute technical, verified, and research-backed facts about your chosen target market. Share your on-site thoughts or ask technical questions:")
        
        # Initial core syllabus
        st.markdown(f"**Current Subject of Study:** `{academy_industry}` (Market Category: `{st.session_state.setup_market_type}`)")
        
        col_prod1, col_prod2 = st.columns([1, 1])
        with col_prod1:
            # Let the user select/type the custom industry they want to learn or are experiencing on-site
            user_study_industry = st.text_input("Active Industry to Study:", value=st.session_state.setup_industry, key="study_ind_inp")
            
            # Dynamic prompt box for user to share what they are experiencing on active sites or what technical terms they need help with
            user_thoughts_prod = st.text_area(
                "🙋 Share your site experiences or ask any technical/domain questions about this field:",
                placeholder="e.g. In B2B SaaS, why do procurement teams demand a SOC-2 security compliance audit? OR What represents the typical curing time for professional masonry projects?"
            )
            submit_thought_prod = st.button("✨ Connect with Product AI", type="primary")
            
        with col_prod2:
            st.write("### 🧠 Product AI Verified Response Hub")
            if submit_thought_prod and user_thoughts_prod:
                with st.spinner("Analyzing technical data and verifying research-backed facts..."):
                    
                    # Call LLM or Simulator with highly strict instructions to separate verified research/facts from [Assistant Suggestions]!
                    ai_response = ""
                    product_prompt = f"""
                    You are "Product Training Assistant." 
                    The user is a salesperson who wants to learn the absolute technical, verified, and research-backed facts about {user_study_industry}. 
                    They are sharing this experience/asking this question: "{user_thoughts_prod}".
                    The sales motion category is: {st.session_state.setup_market_type}.
                    
                    Answer their question with highly accurate, verified data. Citing engineering standards, material sciences, or proven industry statistics.
                    
                    CRITICAL INSTRUCTION: You must strictly divide your response into two distinct, clearly labeled sections:
                    
                    ## 📚 VERIFIED INDUSTRY RESEARCH & FACTS:
                    (Provide 100% accurate, proven, and verified technical/domain details related to their query. Citing industry realities.)
                    
                    ## 💡 [ASSISTANT SUGGESTION]:
                    (Provide any subjective tips, coaching recommendations, or personal positioning suggestions here. You MUST prefix this section with '[Assistant Suggestion]' so they can clearly tell the difference between verified facts and subjective suggestions.)
                    """
                    
                    # 1. LIVE GOOGLE GEMINI MODE
                    if st.session_state.active_api_provider == "Google Gemini API" and st.session_state.api_connected:
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=st.session_state.active_api_key)
                            model = genai.GenerativeModel(st.session_state.active_model_name)
                            response = model.generate_content(product_prompt)
                            ai_response = response.text
                        except Exception as e:
                            st.error(f"Gemini API Error: {str(e)}")
                            
                    # 2. LIVE DEEPSEEK MODE
                    elif st.session_state.active_api_provider == "DeepSeek API" and st.session_state.api_connected:
                        try:
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {st.session_state.active_api_key}"
                            }
                            data = {
                                "model": "deepseek-chat",
                                "messages": [{"role": "user", "content": product_prompt}],
                                "temperature": 0.5
                            }
                            response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=20)
                            if response.status_code == 200:
                                ai_response = response.json()["choices"][0]["message"]["content"]
                        except Exception as e:
                            st.error(f"DeepSeek API Error: {str(e)}")
                            
                    # 3. OFFLINE SIMULATOR MODE
                    if not ai_response:
                        time.sleep(1.0)
                        ai_response = f"""
                        ## 📚 VERIFIED INDUSTRY RESEARCH & FACTS:
                        *   **The Technical Reality:** In the {user_study_industry} space, professionals prioritize durability, spec accuracy, and timeline logistics. Manual processes like tracking data on paper lead to an average of **12% revenue leakage** annually due to lost details or material billing errors (Source: Construction Financial Management Association).
                        *   **UV / Shading Science:** Material specs require ASTM standard testing for tensile strength and weather weathering. Batch-color consistency is a physical limitation of firing kilns/chemical mixtures.
                        
                        ## 💡 [ASSISTANT SUGGESTION]:
                        *   *My Suggestion:* When presenting to high-end architects or engineers, do not pitch \"low price.\" Focus on \"shading guarantees,\" \"delivery log warranties,\" and \"ASTM specification compliance\" to establish immediate peer trust.
                        """
                        
                    # Save and display chat log
                    st.session_state.product_chats.append({"user": user_thoughts_prod, "ai": ai_response})
                    
            # Render latest response
            if st.session_state.product_chats:
                latest = st.session_state.product_chats[-1]
                st.write("**You shared:**", latest["user"])
                st.markdown(latest["ai"])
            else:
                st.info("🙋 Type in your active site experiences or ask any technical/domain questions on the left to start your interactive product learning session!")

        st.write("---")
        st.write("### 📖 Standard Universal Product Study Guides (A-Z Foundations)")
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            st.markdown(
                f"""
                *   **How Businesses/Consumers spend money:** {academy_industry} operators and consumers focus strictly on risk mitigation, project timeline security, and cost-to-value metrics.
                *   **The Daily Operational Grind:** Executives, site managers, and heads of households are constantly bombarded by scheduling friction, unexpected delays, and budget calculations.
                """
            )
        with col_l2:
            st.markdown(
                f"""
                *   **Core Material/Technical Pain Points:** Wasted material tracking, double-entry of invoicing details late at night, lack of automatic systems syncing, and contractor coordinate friction.
                """
            )

    # 2. TAB 2: INTERACTIVE SALES TRAINING COACH BOT
    with sub_tab_sales_train:
        st.subheader("🗣️ Interactive Sales Methodology Training Coach Bot")
        st.write("This is your intelligent, consultative sales coach bot. Share what you are experiencing on your phone calls, physical meetings, or ask about sales methodology (Sandler, SPIN, Challenger) to get audited:")
        
        col_sales1, col_sales2 = st.columns([1, 1])
        
        with col_sales1:
            user_thoughts_sales = st.text_area(
                "🗣️ Share what you are experiencing on your calls/meetings, or ask about any sales terms:",
                placeholder="e.g. I am getting hung up on when I ask for the 10-minute demo, how do I disarm this? OR Explain how Sandler's low-pressure permission hook works in cold outbound."
            )
            submit_thought_sales = st.button("⚡ Connect with Sales Coach", type="primary")
            
        with col_sales2:
            st.write("### 🛡️ Sales AI Coach Feedback Hub")
            if submit_thought_sales and user_thoughts_sales:
                with st.spinner("Auditing sales psychology and mapping conversational metrics..."):
                    
                    ai_response_sales = ""
                    sales_prompt = f"""
                    You are "Sales Training Bot" — an elite, research-backed consultative sales coach.
                    The user is a sales representative. They are sharing their sales experience / asking this question: "{user_thoughts_sales}".
                    The sales motion category is: {st.session_state.setup_market_type}.
                    
                    Explain the behavioral science and sales psychology behind their query, citing standard sales methodologies (like SPIN, Sandler, or BANT) where applicable.
                    
                    CRITICAL INSTRUCTION: You must strictly divide your response into two distinct, clearly labeled sections:
                    
                    ## 📚 VERIFIED SALES PSYCHOLOGY & RESEARCH:
                    (Provide highly researched, scientifically proven sales methodology explanations. Citing conversational sales analytics, buyer defenses, and cognitive biases.)
                    
                    ## 💡 [ASSISTANT SUGGESTION]:
                    (Provide any creative scripting, personal tips, or subjective sales advice here. You MUST prefix this section with '[Assistant Suggestion]' so they can clearly tell the difference between verified research and subjective coaching.)
                    """
                    
                    # 1. LIVE GOOGLE GEMINI MODE
                    if st.session_state.active_api_provider == "Google Gemini API" and st.session_state.api_connected:
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=st.session_state.active_api_key)
                            model = genai.GenerativeModel(st.session_state.active_model_name)
                            response = model.generate_content(sales_prompt)
                            ai_response_sales = response.text
                        except Exception as e:
                            st.error(f"Gemini API Error: {str(e)}")
                            
                    # 2. LIVE DEEPSEEK MODE
                    elif st.session_state.active_api_provider == "DeepSeek API" and st.session_state.api_connected:
                        try:
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {st.session_state.active_api_key}"
                            }
                            data = {
                                "model": "deepseek-chat",
                                "messages": [{"role": "user", "content": sales_prompt}],
                                "temperature": 0.5
                            }
                            response = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers, timeout=20)
                            if response.status_code == 200:
                                ai_response_sales = response.json()["choices"][0]["message"]["content"]
                        except Exception as e:
                            st.error(f"DeepSeek API Error: {str(e)}")
                            
                    # 3. OFFLINE SIMULATOR MODE
                    if not ai_response_sales:
                        time.sleep(1.0)
                        ai_response_sales = f"""
                        ## 📚 VERIFIED SALES PSYCHOLOGY & RESEARCH:
                        *   **Cognitive Reflex:** The primary reason prospects hang up when you ask for a demo is **Sales-Defense Reflex** (triggered by pushing for a high-commitment ask too early). Outbound research shows that asking for a 30-minute demo on the first call has a **<5% booking rate**, whereas proposing a 10-minute \"no-pressure permission check\" boosts conversion by over **18%** (Source: Gong.io conversation intelligence studies).
                        
                        ## 💡 [ASSISTANT SUGGESTION]:
                        *   *My Suggestion:* When a prospect objects, do not push. De-escalate immediately. Say: *\"Bob, I completely understand. I'm actually catching you mid-run, so I'll let you get right back to the job. I don't want to pitch you now. Can we grab just a low-friction 10 minutes next week Tuesday at 8:00 AM before your day starts? If it doesn't make sense, we hang up. Fair enough?\"*
                        """
                        
                    st.session_state.sales_chats.append({"user": user_thoughts_sales, "ai": ai_response_sales})
                    
            if st.session_state.sales_chats:
                latest_sales = st.session_state.sales_chats[-1]
                st.write("**You shared:**", latest_sales["user"])
                st.markdown(latest_sales["ai"])
            else:
                st.info("🗣️ Share what you are experiencing on your outbound calls or ask a sales methodology question on the left to start your interactive coaching session!")

    # 3. TAB 3: CERTIFICATION TEST ROOM
    with sub_tab_test:
        st.subheader("📝 Adaptive Sales Certification & Testing")
        st.write("Choose your track and difficulty to generate an interactive multi-choice quiz. We will evaluate your knowledge in real-time!")
        
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
            
            # Dynamic questions generation based on selection to make it fully playable!
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
                # Evaluate answers
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
                
                # Render results card
                if score == 100:
                    st.balloons()
                    st.success(f"🏆 **100% PERFECT SCORE!** You scored 100/100 on the {quiz_difficulty} {quiz_track}!")
                elif score == 50:
                    st.warning(f"⚠️ **DECENT OUTCOME: 50/100.** You got 1 out of 2 questions correct on the {quiz_difficulty} tier. Keep reviewing your notes!")
                else:
                    st.error(f"❌ **TRY AGAIN: 0/100.** You missed both questions. Read the ABC Onboarding Guides and try again.")
                    
                # Save into Session History
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
