import streamlit as st
import pandas as pd
import random
import time

# Set up page configurations
st.set_page_config(
    page_title="SalesFlow AI - Unified Sales Workspace & Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #fafbfc; }
    h1, h2 { color: #1B365D; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; }
    h3 { color: #5A6B7C; }
    .stButton>button { background-color: #1B365D; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #5A6B7C; color: white; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e1e4e6;
    }
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE INITIALIZATION -----------------
# 1. User Account Tier State: "Free", "Practice Pro", "Enterprise"
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "Free"
# 2. Daily Practice Limit (Message Counter)
if "practice_message_count" not in st.session_state:
    st.session_state.practice_message_count = 0
# 3. Active Chat Logs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_call_active" not in st.session_state:
    st.session_state.is_call_active = False
# 4. Scenario Settings
if "setup_industry" not in st.session_state:
    st.session_state.setup_industry = "HVAC / Plumbing Dispatch Software (Jobtable)"
if "setup_persona" not in st.session_state:
    st.session_state.setup_persona = "Bob Miller, Gruff Plumbing Business Owner"
if "setup_mood" not in st.session_state:
    st.session_state.setup_mood = "Super Stressed, working on-site, tech-averse"
# 5. CRM Leads Database
if "crm_data" not in st.session_state:
    st.session_state.crm_data = pd.DataFrame([
        {"ID": "C101", "Name": "Miller & Sons Plumbing", "Contact": "Bob Miller", "Stage": "Qualified Lead", "Value": 4500, "Assigned Rep": "Ikechukwu Onuekwusi", "Last Action": "Objection handled regarding paper billing"},
        {"ID": "C102", "Name": "BrightSpark Electrical", "Contact": "Sarah Jenkins", "Stage": "Demo Scheduled", "Value": 3200, "Assigned Rep": "Ikechukwu Onuekwusi", "Last Action": "Scheduled for Tuesday morning walkthrough"},
        {"ID": "C103", "Name": "Apex Climate Systems", "Contact": "Dave Kowalski", "Stage": "Contacted", "Value": 12000, "Assigned Rep": "Jane Doe", "Last Action": "Sent comparison sheet vs ServiceTitan"},
        {"ID": "C104", "Name": "Tri-State Roofing", "Contact": "Mark Henderson", "Stage": "Closed-Won", "Value": 6000, "Assigned Rep": "Jane Doe", "Last Action": "Contract signed, QuickBooks synced"}
    ])
# 6. Team Personas
if "personas" not in st.session_state:
    st.session_state.personas = [
        {"Name": "Enterprise HVAC Manager", "Difficulty": "Hard", "Objections": "Integration, multi-site pricing"},
        {"Name": "Skeptical Dental Admin", "Difficulty": "Medium", "Objections": "HIPAA compliance, training time"}
    ]

# ----------------- SIDEBAR: ACCOUNT CONSOLE -----------------
with st.sidebar:
    st.image("https://weworkremotely.com/assets/company-name-new-listing-icon-1535d75c2a56fe22cf7821636a862de6f5dcb83b1395dc2c164b77476b274c99.svg", width=120)
    st.title("SalesFlow Studio")
    
    # Tier Indicator Badge
    if st.session_state.user_tier == "Free":
        st.markdown("`<span class='badge' style='background-color: #f0f2f6; color: #5a6b7c;'>🔓 FREE PRACTICE TIER</span>`", unsafe_allow_html=True)
        st.write(f"**Usage Limit:** {st.session_state.practice_message_count}/5 Free Daily Messages")
    elif st.session_state.user_tier == "Practice Pro":
        st.markdown("`<span class='badge' style='background-color: #d1e7dd; color: #0f5132;'>🔥 PRACTICE PRO ACTIVE</span>`", unsafe_allow_html=True)
        st.write("**Practice calls:** Unlimited")
    elif st.session_state.user_tier == "Enterprise":
        st.markdown("`<span class='badge' style='background-color: #cfe2ff; color: #084298;'>💼 ENTERPRISE SUITE ACTIVE</span>`", unsafe_allow_html=True)
        st.write("**All Modules Unlocked**")

    st.write("---")
    
    # Quick API key configuration (for Google AI Studio)
    st.subheader("🔑 API Studio Key")
    gemini_key = st.text_input("Gemini API Key:", type="password", help="Paste your free API key from Google AI Studio")
    
    st.write("---")
    
    # Dev/Demo Bypass tool (For the job application review)
    st.subheader("🛠️ Developer Tool")
    dev_bypass = st.text_input("Bypass Admin Key:", type="password")
    if dev_bypass == "salesflow99":
        st.session_state.user_tier = "Enterprise"
        st.success("Developer Bypass: Unlocked Enterprise Mode!")
        st.rerun()
        
    if st.button("Reset Usage & Account Tier", use_container_width=True):
        st.session_state.user_tier = "Free"
        st.session_state.practice_message_count = 0
        st.session_state.messages = []
        st.session_state.is_call_active = False
        st.success("App completely reset.")
        st.rerun()

# ----------------- MAIN NAVIGATION -----------------
st.title("🎯 SalesFlow All-in-One Sales Suite")
st.write("The ultimate workspace combining free AI practice roleplays with professional enterprise sales enablement pipelines.")

# Create main navigation tabs
tab_practice, tab_crm, tab_analyzer, tab_scenario, tab_api = st.tabs([
    "📞 AI Outbound Practice Arena",
    "📊 CRM Pipeline & Stages",
    "🎙️ AI Call Recording Analyzer",
    "⚙️ Custom Scenario Builder",
    "🔌 Developer API Hub"
])

# ----------------- DYNAMIC SEAMLESS CHECKOUT MODAL FUNCTION -----------------
def render_instant_paywall(target_tier, price_str, features_list):
    st.markdown(
        f"""
        <div class='card' style='border: 2px solid #1B365D; background-color: #fdfefe;'>
            <h3 style='color: #1B365D; text-align: center;'>🔐 Upgrade Instantly to {target_tier}</h3>
            <p style='text-align: center; font-size: 26px; font-weight: bold;'>{price_str}</p>
            <p style='text-align: center;'>Frictionless checkout. No registration keys required. Pay and unlock instantly below.</p>
            <hr/>
            <p><b>Features Unlocked:</b></p>
            <ul>
        """, unsafe_allow_html=True
    )
    for feat in features_list:
        st.write(f"* ✔ {feat}")
    st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Standard Card payment simulator form right in the app
    with st.form("seamless_card_payment_form"):
        st.write("### 💳 Secure Credit/Debit Card & PayPal Gateway")
        pay_card = st.text_input("Card Number:", placeholder="4111 2222 3333 4444")
        col_pay1, col_pay2 = st.columns(2)
        with col_pay1:
            pay_expiry = st.text_input("Expiry Date:", placeholder="MM/YY")
        with col_pay2:
            pay_cvv = st.text_input("CVV:", type="password", placeholder="123")
            
        pay_submit = st.form_submit_button(f"Pay & Unlock {target_tier} Instantly")
        if pay_submit:
            if pay_card and pay_expiry and pay_cvv:
                with st.spinner("Authorizing secure bank network transaction..."):
                    time.sleep(1.5)
                st.session_state.user_tier = target_tier
                st.session_state.practice_message_count = 0
                st.balloons()
                st.success(f"🎉 **PAYMENT SUCCESSFUL!** Your account has been seamlessly upgraded to **{target_tier}**. All restrictions are cleared!")
                time.sleep(1.0)
                st.rerun()
            else:
                st.error("Please enter valid billing details to complete your card transaction.")

# ----------------- TAB 1: PRACTICE ARENA (FRONT & CENTER) -----------------
with tab_practice:
    st.subheader("🚀 Interactive Outbound Practice")
    
    # Check if the user has hit their free daily practice limit
    if st.session_state.user_tier == "Free" and st.session_state.practice_message_count >= 5:
        st.error("🚫 **DAILY TRIAL EXCEEDED.** You have completed your 5 free dialogue practice turns for today.")
        render_instant_paywall(
            target_tier="Practice Pro",
            price_str="$5.99 USD / month",
            features_list=[
                "Unlimited Outbound Practice Calls (No daily constraints)",
                "Full integration with Google AI Studio (Gemini)",
                "Access to all 3 standard contractor and B2B buyer templates"
            ]
        )
    else:
        # Standard configuration panel
        st.write("Configure your scenario parameters or select a template to load:")
        
        # 1-Click Preset Buttons
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            if st.button("🔧 Preset: Jobtable Contractor Software", use_container_width=True):
                st.session_state.setup_industry = "HVAC / Plumbing Mobile Invoicing Software (Jobtable)"
                st.session_state.setup_persona = "Bob Miller, Gruff Plumbing Business Owner"
                st.session_state.setup_mood = "Super Stressed, working on-site, tech-averse"
                st.session_state.messages = []
                st.session_state.is_call_active = False
                st.rerun()
        with col_t2:
            if st.button("💼 Preset: HR B2B SaaS to CFO", use_container_width=True):
                st.session_state.setup_industry = "HR Payroll & Employee Benefits SaaS"
                st.session_state.setup_persona = "Sarah Jenkins, Analytical Enterprise CFO"
                st.session_state.setup_mood = "Extremely professional, protective of company budgets, analytical"
                st.session_state.messages = []
                st.session_state.is_call_active = False
                st.rerun()
        with col_t3:
            if st.button("🏠 Preset: B2C Real Estate Outbound", use_container_width=True):
                st.session_state.setup_industry = "Residential Property Listing Services"
                st.session_state.setup_persona = "Dave Kowalski, Skeptical Private Homeowner"
                st.session_state.setup_mood = "Defensive, annoyed by agents, wants to sell FSBO"
                st.session_state.messages = []
                st.session_state.is_call_active = False
                st.rerun()
                
        st.write("")
        
        # Custom setup inputs
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            ui_industry = st.text_input("My Product/Industry:", value=st.session_state.setup_industry)
        with col_c2:
            ui_persona = st.text_input("Target Customer:", value=st.session_state.setup_persona)
        with col_c3:
            ui_mood = st.text_input("Buyer's Current Mood:", value=st.session_state.setup_mood)
            
        st.session_state.setup_industry = ui_industry
        st.session_state.setup_persona = ui_persona
        st.session_state.setup_mood = ui_mood
        
        st.write("---")
        
        # Call room split
        col_room1, col_room2 = st.columns([2, 1])
        
        with col_room1:
            st.write(f"### Live Simulation: Calling {ui_persona.split(',')[0]}")
            initial_greeting = f"Hello? Yes, this is {ui_persona.split(',')[0]}. I'm in the middle of something {ui_mood.lower()}. Who is this and what's this about?"
            
            # Start Call Button
            if not st.session_state.is_call_active:
                if st.button("📞 Dial Phone Number", type="primary", use_container_width=True):
                    st.session_state.is_call_active = True
                    st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]
                    st.rerun()
                    
            # Render chat history
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            # User input handling
            if st.session_state.is_call_active:
                user_msg = st.chat_input("Enter your sales pitch...")
                
                if user_msg:
                    # Increment usage count if on free tier
                    if st.session_state.user_tier == "Free":
                        st.session_state.practice_message_count += 1
                        
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.chat_message("user").write(user_msg)
                    
                    with st.spinner("Prospect is typing..."):
                        time.sleep(0.8)
                        user_msg_lower = user_msg.lower()
                        ai_reply = ""
                        score_deduction = 0
                        feedback_msg = ""
                        end_call = False
                        
                        # Jargon Filter
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

                        # 1. LIVE GEMINI AI MODE
                        elif gemini_key:
                            try:
                                import google.generativeai as genai
                                genai.configure(api_key=gemini_key)

                                system_prompt = f"""
                                You are roleplaying as {ui_persona}, a target customer in the {ui_industry} space.
                                Your current personality/mood constraint is: {ui_mood}.
                                The user is an outbound SDR cold calling you.
                                
                                Your Goal: Act as a highly realistic, tough, skeptical buyer. Respond to the user's messages brief, blunt, and naturally.
                                You must challenge the user with typical objections relevant to {ui_industry} (e.g. 'not interested,' 'too expensive,' 'already have a competitor,' 'send me an email').
                                
                                Rules of Engagement:
                                1. Stay completely in character.
                                2. Do not agree to a 10-minute meeting on the first turn. Push back at least twice.
                                3. If they handle your objections well (using consultative empathy, avoiding scripts, showing clear micro-value, and proposing a frictionless 10-minute meeting), agree to the calendar invite.
                                4. If they read a scripted pitch, use tech jargon, or don't listen, hang up on them.
                                """
                                model = genai.GenerativeModel(
                                    model_name="gemini-1.5-flash",
                                    system_instruction=system_prompt
                                )

                                response = model.generate_content(user_msg)
                                ai_reply = response.text

                                if any(word in user_msg_lower for word in ["demo", "10 minutes", "tuesday", "schedule", "calendar"]):
                                    st.session_state.objections_handled += 1

                            except Exception as e:
                                st.error(f"Gemini API Error: {str(e)}. Defaulting to Practice Simulator.")

                        # 2. OFFLINE SIMULATOR MODE
                        if not ai_reply:
                            if any(word in user_msg_lower for word in ["demo", "minutes", "schedule", "calendar", "meeting", "tuesday", "wednesday", "thursday"]):
                                if st.session_state.objections_handled >= 1:
                                    ai_reply = f"Fine. If it's really only going to take 10 minutes and you can show me how this actually solves our headaches with {ui_industry}, I'll take a look. Tuesday morning works. Send me a link."
                                    feedback_msg = "Outstanding close! You validated their pains and successfully booked a low-friction meeting!"
                                    end_call = True
                                else:
                                    ai_reply = f"A meeting? I don't even know who you are or why I should care. What are you actually selling?"
                                    score_deduction = 15
                                    feedback_msg = "You went for the meeting/demo ask too fast. Handle an objection and build basic value first!"
                            
                            elif any(word in user_msg_lower for word in ["busy", "time", "mid"]):
                                ai_reply = f"Look, we are extremely busy right now managing our {ui_industry} pipeline. I don't have time for cold pitches."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Busy Brush-off. Empathize immediately, pivot to time-saving, and suggest a 10-min slot next week."
                            
                            elif any(word in user_msg_lower for word in ["price", "cost", "expensive", "money", "budget"]):
                                ai_reply = f"Our budgets are completely locked for this quarter. We can't afford to bring on new expenses."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Budget constraint. Pivot to ROI—explain how your tool saves them more money than it costs."
                            
                            elif any(word in user_msg_lower for word in ["already", "competitor", "happy", "using"]):
                                ai_reply = f"We already have a system in place that handles {ui_industry} operations. I am not looking to switch."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Competitor/Status Quo. Acknowledge and respect their current tool, then suggest a 10-min comparative walkthrough."
                            
                            elif any(word in user_msg_lower for word in ["email", "send"]):
                                ai_reply = f"Just send me an email. I'll take a look at it when I have some free time."
                                st.session_state.objections_handled += 1
                                feedback_msg = "Objection: Send me an email. Agree enthusiastically, then ask a simple qualification question to keep them talking!"
                            
                            else:
                                responses = [
                                    f"Why should we look at your product? Whiteboards and spreadsheets work fine for our {ui_industry}.",
                                    f"Is this going to require our team to learn a complex new process, or is it actually simple?",
                                    f"What separates you from every other cold caller hitting my phone today?"
                                ]
                                ai_reply = random.choice(responses)
                                score_deduction = 10
                                feedback_msg = "Prospect is testing you. Empathize with their daily operational friction and highlight how simple your product is."

                        # Record reply
                        st.session_state.score = max(0, st.session_state.score - score_deduction)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        st.chat_message("assistant").write(ai_reply)

                        # Output coaching feedback
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
                            
                            if st.button("Reset Simulator"):
                                st.session_state.messages = []
                                st.session_state.is_call_active = False
                                st.rerun()
                                
        with col_room2:
            st.subheader("💡 Coach Checklist")
            st.markdown(
                """
                *   **Acknowledge and Pivot:** Never argue with an objection. Agree that their time/current setup is valuable, then pivot to how you simplify their lives.
                *   **Focus on the Core Benefit:** Explain your product simply. *“No more spreadsheets at 10 PM,”* or *“Techs bill directly in the driveway.”*
                *   **The Low-Friction Close:** Ask for a 10-minute walkthrough, never a 1-hour demonstration.
                """
            )

# ----------------- TAB 2: CRM PIPELINE (GATED) -----------------
with tab_crm:
    st.subheader("📊 SalesFlow CRM & Pipeline Stage Tracker")
    
    if st.session_state.user_tier != "Enterprise":
        st.warning("⚠️ **ENTERPRISE MODULE LOCKED.** Managing customer leads, tracking deal stages, and logging revenue pipeline is restricted to the **Enterprise Suite Tier**.")
        render_instant_paywall(
            target_tier="Enterprise",
            price_str="$29.00 USD / month (Individual) or $99 / seat / mo (Enterprise)",
            features_list=[
                "Full-Featured Sales Pipeline & Lead CRM Stage Tracker",
                "Advanced AI Call Recording Auditor & Sentiment Analysis Tool",
                "Deploy custom scenario profiles team-wide (Manager Console)",
                "Full Developer API access and HubSpot / Salesforce automatic webhooks"
            ]
        )
    else:
        st.write("### Active Deal Pipeline Database")
        df = st.session_state.crm_data
        total_pipeline = df["Value"].sum()
        closed_won = df[df["Stage"] == "Closed-Won"]["Value"].sum()
        active_deals = df[df["Stage"] != "Closed-Won"]["Value"].count()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Pipeline Value", f"${total_pipeline:,.2f}")
        with col_m2:
            st.metric("Closed-Won Revenue", f"${closed_won:,.2f}")
        with col_m3:
            st.metric("Active Deal Opportunities", f"{active_deals} Deals")
            
        st.write("---")
        
        # Interactive CRM editor
        edited_df = st.data_editor(
            df,
            column_config={
                "Stage": st.column_config.SelectboxColumn(
                    "Customer Stage",
                    options=["Lead", "Contacted", "Qualified Lead", "Demo Scheduled", "Closed-Won", "Closed-Lost"],
                    required=True
                ),
                "Value": st.column_config.NumberColumn(
                    "Contract Value ($)",
                    format="$%d"
                )
            },
            num_rows="dynamic",
            use_container_width=True,
            key="crm_editor"
        )
        
        if st.button("💾 Save CRM Changes"):
            st.session_state.crm_data = edited_df
            st.success("CRM Pipeline synchronized with company server!")
            st.rerun()

# ----------------- TAB 3: AI CALL ANALYZER (GATED) -----------------
with tab_analyzer:
    st.subheader("🎙️ AI Call Recording Audit & Transcription Studio")
    
    if st.session_state.user_tier != "Enterprise":
        st.warning("⚠️ **ENTERPRISE MODULE LOCKED.** Analyzing call transcripts, scoring buyer sentiment, and writing automated AI follow-ups requires **Enterprise Suite Tier**.")
        render_instant_paywall(
            target_tier="Enterprise",
            price_str="$29.00 USD / month (Individual) or $99 / seat / mo (Enterprise)",
            features_list=[
                "Full-Featured Sales Pipeline & Lead CRM Stage Tracker",
                "Advanced AI Call Recording Auditor & Sentiment Analysis Tool",
                "Deploy custom scenario profiles team-wide (Manager Console)",
                "Full Developer API access and HubSpot / Salesforce automatic webhooks"
            ]
        )
    else:
        sample_transcript = """[0:02] Rep: Hey Mike, this is Ikechukwu here from Jobtable. How is your afternoon going?
[0:06] Buyer: I'm busy. I'm on a roof right now trying to fix a duct. Make it quick.
[0:12] Rep: I completely understand, Mike, and I know your time is money. I saw you've been adding more technicians. We built a simple mobile app where your guys can click the parts they used on-site and invoice the customer right in the driveway before they leave. No more tracking down receipts.
[0:22] Buyer: Well, we just use paper sheets, and then my office admin types them into QuickBooks. It's tedious, but it works.
[0:30] Rep: Paper is reliable, absolutely. But paper doesn't talk to QuickBooks instantly. Jobtable syncs the driveway invoice straight into QuickBooks in one click, meaning you get paid today, and your admin gets her evenings back. I won't pitch you now. Can we grab just 10 minutes next Tuesday morning before your day starts to see it?
[0:40] Buyer: Tuesday morning? If it's really only 10 minutes and simple, I guess I can take a look. Send me the calendar invite."""

        transcript_input = st.text_area("Paste Sales Call Transcript:", value=sample_transcript, height=250)
        
        if st.button("🔍 Run AI Call Audit", type="primary", use_container_width=True):
            with st.spinner("Analyzing call transcription sentiment and parsing sales bottlenecks..."):
                time.sleep(1.2)
                
                st.write("---")
                st.success("🎯 **AI AUDIT COMPLETE!**")
                
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    st.metric("Buyer Sentiment Score", "85% (Favorable)")
                with col_a2:
                    st.metric("Objections Detected", "2 Objections")
                with col_a3:
                    st.metric("Deal Progression Probability", "92% (High)")
                    
                st.markdown(
                    f"""
                    ### 📋 AI Audit Analysis
                    *   **Objections Overcome:**
                        1.  *Time / Busy on roof* (Handled perfectly with time-validation and a quick micro-pitch).
                        2.  *Pen & Paper / Manual QuickBooks admin* (Handled perfectly by validating paper reliability, then pivoting to saving admin time).
                    *   **Vocabulary Assessment:**
                        *   *Excellent:* Used trade terms (*"driveway invoicing"*, *"QuickBooks sync"*, *"parts used on-site"*).
                        *   *Areas to avoid:* None detected. The rep successfully avoided enterprise jargon like "cloud SaaS."
                    
                    ### ✉️ AI-Generated Follow-Up Email Template
                    ```text
                    Subject: Tuesday at 8:00 AM — Quick 10-Min Jobtable Walkthrough
                    
                    Hi Mike,
                    
                    Great speaking with you briefly while you were on that rooftop today. I'm looking forward to our call this coming Tuesday morning at 8:00 AM.
                    
                    As promised, I will keep our call to exactly 10 minutes. I will show you how other trade owners are using Jobtable to invoice in the driveway, sync instantly with QuickBooks, and eliminate night-time paperwork.
                    
                    I have sent the calendar invitation to your email. Talk to you on Tuesday!
                    
                    Best regards,
                    
                    Ikechukwu Onuekwusi
                    Jobtable SDR Team
                    ```
                    """
                )

# ----------------- TAB 4: SCENARIO BUILDER (GATED) -----------------
with tab_scenario:
    st.subheader("⚙️ Custom Training Persona Scenario Builder")
    
    if st.session_state.user_tier != "Enterprise":
        st.warning("⚠️ **ENTERPRISE MODULE LOCKED.** Building custom scenario profiles and deploying them team-wide requires **Enterprise Suite Tier**.")
        render_instant_paywall(
            target_tier="Enterprise",
            price_str="$29.00 USD / month (Individual) or $99 / seat / mo (Enterprise)",
            features_list=[
                "Full-Featured Sales Pipeline & Lead CRM Stage Tracker",
                "Advanced AI Call Recording Auditor & Sentiment Analysis Tool",
                "Deploy custom scenario profiles team-wide (Manager Console)",
                "Full Developer API access and HubSpot / Salesforce automatic webhooks"
            ]
        )
    else:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write("### Build New Buyer Persona")
            with st.form("add_persona_form"):
                p_name = st.text_input("Persona Name (e.g. Director of Procurement):")
                p_diff = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard", "Expert"])
                p_objs = st.text_input("Core Objections:")
                p_submit = st.form_submit_button("Deploy Scenario to Team")
                if p_submit and p_name:
                    st.session_state.personas.append({"Name": p_name, "Difficulty": p_diff, "Objections": p_objs})
                    st.success(f"Persona '{p_name}' deployed successfully!")
                    st.rerun()
        with col_p2:
            st.write("### Deployed Team Personas")
            st.dataframe(pd.DataFrame(st.session_state.personas), use_container_width=True)

# ----------------- TAB 5: DEVELOPER API HUB (GATED) -----------------
with tab_api:
    st.subheader("🔌 Developer REST API & Webhooks")
    
    if st.session_state.user_tier != "Enterprise":
        st.warning("⚠️ **ENTERPRISE MODULE LOCKED.** REST APIs, webhook triggers, and third-party CRM syncing requires **Enterprise Suite Tier**.")
        render_instant_paywall(
            target_tier="Enterprise",
            price_str="$29.00 USD / month (Individual) or $99 / seat / mo (Enterprise)",
            features_list=[
                "Full-Featured Sales Pipeline & Lead CRM Stage Tracker",
                "Advanced AI Call Recording Auditor & Sentiment Analysis Tool",
                "Deploy custom scenario profiles team-wide (Manager Console)",
                "Full Developer API access and HubSpot / Salesforce automatic webhooks"
            ]
        )
    else:
        st.markdown(
            """
            ### REST API Documentation
            Authenticate all requests by including your corporate Bearer Token in your HTTP headers:
            `Authorization: Bearer sf_live_82938a9283f982a839a842b10a`
            
            #### 1. POST /v1/leads (Inject Lead from HubSpot/Salesforce)
            ```json
            {
              "company_name": "Miller & Sons Plumbing",
              "contact_name": "Bob Miller",
              "estimated_value": 4500,
              "assigned_rep_email": "ikechukwuonuekwusi@gmail.com"
            }
            ```
            """
        )
        st.success("Webhooks online. Active sync with HubSpot Hub ID: #829103 and Salesforce CRM Instance NA-92.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed & Built by Ikechukwu Onuekwusi | Universal AI Outbound App 🎯</p>", unsafe_allow_html=True)
