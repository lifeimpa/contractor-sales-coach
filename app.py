import streamlit as st
import pandas as pd
import random
import time
import requests

# Set up page configurations
st.set_page_config(
    page_title="My Sales Copilot - Outbound & Closing Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- ADVANCED CUSTOM UI STYLING (CSS Injection) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Global Base Reset */
    .main { 
        background-color: #f8fafc; 
        font-family: 'Inter', sans-serif;
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

# ----------------- SESSION STATE INITIALIZATION -----------------
# 1. Active Chat Logs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_call_active" not in st.session_state:
    st.session_state.is_call_active = False
# 2. Scenario Settings (Universal & easily customized)
if "setup_industry" not in st.session_state:
    st.session_state.setup_industry = "HVAC / Plumbing Dispatch Software (Jobtable)"
if "setup_persona" not in st.session_state:
    st.session_state.setup_persona = "Bob Miller, Miller & Sons Plumbing (Owner)"
if "setup_mood" not in st.session_state:
    st.session_state.setup_mood = "Super Stressed, working under a sink, tech-skeptical"
# 3. Analytics
if "objections_handled" not in st.session_state:
    st.session_state.objections_handled = 0
if "score" not in st.session_state:
    st.session_state.score = 100

# ----------------- SIDEBAR: AI CO-PILOT CONFIGURATION -----------------
with st.sidebar:
    st.image("https://weworkremotely.com/assets/company-name-new-listing-icon-1535d75c2a56fe22cf7821636a862de6f5dcb83b1395dc2c164b77476b274c99.svg", width=120)
    st.title("My Sales Copilot")
    st.markdown("<p style='color: #64748b; font-size: 13px; margin-top: 0px;'>Proprietary Rep Command Suite</p>", unsafe_allow_html=True)
    st.markdown("<span class='badge-free'>🔓 PERSONAL ACTIVE UTILITY</span>", unsafe_allow_html=True)
    st.write("---")
    
    # Dual API Configurator Selection
    st.subheader("🤖 Connect AI Brain")
    api_provider = st.selectbox("Select API Provider:", ["Practice Simulator (Offline)", "Google Gemini API", "DeepSeek API"])
    
    api_key = ""
    if api_provider == "Google Gemini API":
        api_key = st.text_input("Gemini API Key:", type="password", help="Paste your free API key from Google AI Studio")
        with st.expander("ℹ️ How to get your FREE Gemini Key"):
            st.markdown(
                """
                1. Go to <a href='https://aistudio.google.com/' target='_blank'><b>Google AI Studio</b></a>.
                2. Click the blue **\"Get API Key\"** button in the top left.
                3. Click **\"Create API Key in new project\"** and paste it here!
                """,
                unsafe_allow_html=True
            )
    elif api_provider == "DeepSeek API":
        api_key = st.text_input("DeepSeek API Key:", type="password", help="Paste your DeepSeek API key")
        with st.expander("ℹ️ How to get your DeepSeek Key"):
            st.markdown(
                """
                1. Go to <a href='https://platform.deepseek.com/' target='_blank'><b>DeepSeek Platform</b></a>.
                2. Sign up and top up a few cents/dollars (DeepSeek is extremely cheap, costing cents for thousands of calls).
                3. Go to **\"API Keys\"** on the left menu, create a key, and paste it here!
                """,
                unsafe_allow_html=True
            )
            
    st.write("---")
    
    # Active Session Analytics
    st.subheader("📈 My Practice Performance")
    st.metric("Tone Match Score", f"{st.session_state.score}/100")
    st.metric("Objections Handled", f"{st.session_state.objections_handled}")
    
    if st.button("Reset Active Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_call_active = False
        st.session_state.score = 100
        st.session_state.objections_handled = 0
        st.success("Session reset.")
        st.rerun()

# ----------------- MAIN HEADER BANNER -----------------
st.markdown(
    """
    <div style='background-color: #ffffff; padding: 30px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02);'>
        <h1 style='margin: 0px;'>⚡ My Proprietary Sales SDR Copilot</h1>
        <p style='color: #64748b; font-size: 16px; margin-top: 5px; margin-bottom: 0px;'>My private operational dashboard. I use this tool daily to roleplay complex objections, write high-converting outbound emails, generate SMS text replies, and storyboard Loom prospecting video pitches.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- TABS: SDR UTILITIES (FULLY UNLOCKED) -----------------
tab_practice, tab_emails, tab_sms, tab_videos, tab_battlecards = st.tabs([
    "📞 Outbound & Closing Roleplay Arena",
    "✉️ AI Outbound Email Composer",
    "💬 AI Text Response & SMS Writer",
    "🎬 AI Video Prospecting Script Studio",
    "🛡️ My Closing Objection Battlecards"
])

# ----------------- TAB 1: PRACTICE ARENA -----------------
with tab_practice:
    st.subheader("🎯 Outbound Practice & Closing Simulator")
    st.write("Configure your prospect (plumber, enterprise executive, or private home buyer) and practice handling cold calls or closing deals on-the-spot:")
    
    # Standard Presets
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        if st.button("🔧 Preset: Bob Miller (Plumbing / Contractor)", use_container_width=True):
            st.session_state.setup_industry = "HVAC / Plumbing Mobile Invoicing Software (Jobtable)"
            st.session_state.setup_persona = "Bob Miller, Miller & Sons Plumbing (Owner)"
            st.session_state.setup_mood = "Super Stressed, working under a sink, tech-skeptical"
            st.session_state.messages = []
            st.session_state.is_call_active = False
            st.rerun()
    with col_t2:
        if st.button("💼 Preset: Sarah Jenkins (Electrical / Contractor)", use_container_width=True):
            st.session_state.setup_industry = "Jobtable dispatch & billing software for Electricians"
            st.session_state.setup_persona = "Sarah Jenkins, BrightSpark Electrical (Owner-Operator)"
            st.session_state.setup_mood = "Driving between jobs, overwhelmed by admin paperwork backlog, QuickBooks user"
            st.session_state.messages = []
            st.session_state.is_call_active = False
            st.rerun()
    with col_t3:
        if st.button("🏠 Preset: Dave Kowalski (HVAC / Contractor)", use_container_width=True):
            st.session_state.setup_industry = "Jobtable job scheduling & invoicing software for HVAC"
            st.session_state.setup_persona = "Dave Kowalski, Apex Heating & Air (Owner)"
            st.session_state.setup_mood = "On a commercial rooftop, highly skeptical of sales reps, happy with paper"
            st.session_state.messages = []
            st.session_state.is_call_active = False
            st.rerun()
            
    st.write("")
    
    # Custom configuration inputs (Make it completely universal!)
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        ui_industry = st.text_input("My Product/Industry:", value=st.session_state.setup_industry, help="What are you pitching? e.g. Jobtable, Real estate, B2B SaaS, etc.")
    with col_c2:
        ui_persona = st.text_input("Target Customer Persona:", value=st.session_state.setup_persona, help="Who are you calling? (Title, Company, background)")
    with col_c3:
        ui_mood = st.text_input("Buyer's Current Mood/Objection Constraints:", value=st.session_state.setup_mood, help="How should the AI behave? e.g. Extremely busy, price-focused, already using a competitor")
        
    st.session_state.setup_industry = ui_industry
    st.session_state.setup_persona = ui_persona
    st.session_state.setup_mood = ui_mood
    
    st.write("---")
    
    col_room1, col_room2 = st.columns([2, 1])
    
    with col_room1:
        # Visual Helper
        if api_provider == "Practice Simulator (Offline)":
            st.info("💡 **My Sales Tool Note:** Currently in **Practice Simulator Mode**. To connect this app directly to the advanced live brains of Google Gemini or DeepSeek, simply configure your selection in the sidebar and paste your API key!")
            
        st.write(f"### Live Session: Speaking with {ui_persona.split(',')[0]}")
        initial_greeting = f"Yeah, this is {ui_persona.split(',')[0]} speaking. I'm literally in the middle of a job site right now. Make it quick, what is this?"
        
        if not st.session_state.is_call_active:
            if st.button("📞 Initiate Active Outbound Dial", type="primary", use_container_width=True):
                st.session_state.is_call_active = True
                st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]
                st.rerun()
                
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        if st.session_state.is_call_active:
            user_msg = st.chat_input("Enter your sales pitch response...")
            
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

                    # 1. LIVE GOOGLE GEMINI MODE
                    elif api_provider == "Google Gemini API" and api_key:
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=api_key)

                            system_prompt = f"""
                            You are roleplaying as {ui_persona}, a target customer in the {ui_industry} space.
                            Your current personality/mood constraint is: {ui_mood}.
                            The user (Ikechukwu) is an outbound SDR cold calling you to pitch their product.
                            
                            Your Goal: Act as a highly realistic, tough, skeptical buyer. Respond to the user's messages brief, blunt, and naturally.
                            You must challenge the user with typical objections relevant to {ui_industry} (e.g. 'not interested,' 'too expensive,' 'already happy with paper,' 'using a competitor like Jobber/ServiceTitan').
                            
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

                            # Tone & pacing deduct calculation
                            if any(j in user_msg_lower for j in ["solution", "synergy", "paradigm"]):
                                score_deduction = 15
                                feedback_msg = "Slight tone mismatch. Keep the phrasing natural and trade-focused."

                        except Exception as e:
                            st.error(f"Gemini API Error: {str(e)}. Defaulting to Practice Simulator.")

                    # 2. LIVE DEEPSEEK API MODE
                    elif api_provider == "DeepSeek API" and api_key:
                        try:
                            # Standard REST API payload for DeepSeek
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {api_key}"
                            }
                            
                            system_prompt = f"You are roleplaying as {ui_persona}, a target customer in the {ui_industry} space. Mood: {ui_mood}. The user is an outbound sales representative. Act as a realistic, skeptical, busy buyer. Respond with brief, blunt, natural objections. Force them to overcome objections before booking a 10-min meeting."
                            
                            # Construct conversation payload
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

                    # 3. OFFLINE SIMULATOR MODE (Fallback logic)
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
                            ai_reply = f"Look, we are extremely busy right now managing our field calls. I don't have time for software cold pitches."
                            st.session_state.objections_handled += 1
                            feedback_msg = "Objection: Busy Brush-off. Empathize immediately, pivot to time-saving, and suggest a 10-min slot next week."
                        
                        elif any(word in user_msg_lower for word in ["price", "cost", "expensive", "money", "budget"]):
                            ai_reply = f"Our margins are completely tight right now. We can't afford to bring on new monthly expenses."
                            st.session_state.objections_handled += 1
                            feedback_msg = "Objection: Budget constraint. Pivot to ROI—explain how your tool saves them more money than it costs."
                        
                        elif any(word in user_msg_lower for word in ["already", "competitor", "happy", "using", "jobber", "servicetitan"]):
                            ai_reply = f"We already use ServiceTitan / Jobber to manage our HVAC and plumbing pipeline. We are happy with it."
                            st.session_state.objections_handled += 1
                            feedback_msg = "Objection: Competitor/Status Quo. Acknowledge and respect their current tool, then suggest a 10-min comparative walkthrough."
                        
                        elif any(word in user_msg_lower for word in ["email", "send"]):
                            ai_reply = f"Just send me an email. I'll take a look at it when I'm back at the office on Sunday."
                            st.session_state.objections_handled += 1
                            feedback_msg = "Objection: Send me an email. Agree enthusiastically, then ask a simple qualification question to keep them talking!"
                        
                        else:
                            responses = [
                                f"Why should we look at your product? Whiteboards and spreadsheets work fine for our HVAC and plumbing crews.",
                                f"Is this going to require our technicians to learn a complex new app, or is it actually simple?",
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
                        
                        if st.button("Reset Simulator"):
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

# ----------------- TAB 2: EMAIL COMPOSER (FULLY UNLOCKED) -----------------
with tab_emails:
    st.subheader("✉️ Outbound AI Follow-up Email Composer")
    st.write("Generate a high-converting, personalized follow-up email sequence in 1 click for any industry:")
    
    col_em1, col_em2 = st.columns(2)
    with col_em1:
        em_trade = st.text_input("Target Customer Industry/Profile:", value="HVAC & Plumbing Contractors")
        em_objection = st.selectbox("Objection Handled on Call:", ["Too Busy / Working On-Site", "Paper works fine", "Too Expensive / Tight Budgets", "Happy with Current Competitor"])
    with col_em2:
        em_date = st.text_input("Meeting Proposal Time:", value="Tuesday morning at 8:00 AM")
        em_generate = st.button("✨ Generate Email Sequence", type="primary")
        
    if em_generate:
        with st.spinner("AI is crafting your email sequence..."):
            time.sleep(1.0)
            st.markdown(
                f"""
                ### 📧 Recommended Email Template
                **Subject:** 10 minutes to simplify your operations for {em_trade.lower()} on Tuesday?
                
                Hi [Contractor Name],
                
                Great speaking with you briefly while you were on that job site today. I know you're busy running your crew, so I promised to keep this short.
                
                When we spoke, you mentioned that **{em_objection.lower()}**. I completely understand—many of the direct business owners we partner with felt the exact same way. 
                
                But they saw how **{ui_industry}** eliminates late-night paperwork and gets them paid in the driveway before their trucks start up, syncing everything instantly to QuickBooks in one click.
                
                I won't pitch you over email. As agreed, let’s grab a quick 10-minute walkthrough on **{em_date}** so you can see how simple it is. 
                
                I have sent a calendar invite to your inbox. Speak then!
                
                Best,
                
                Ikechukwu Onuekwusi  
                Outbound Sales Representative  
                """
            )

# ----------------- TAB 3: SMS COMPOSER (FULLY UNLOCKED) -----------------
with tab_sms:
    st.subheader("💬 AI Text Response & SMS Writer")
    st.write("When buyers say **'Just text me details'** or **'I'm too busy, text me,'** copy-paste these low-friction SMS templates:")
    
    sms_trade = st.text_input("Target Trade/Profession:", value="Plumbing")
    sms_pain = st.radio("Core Value Angle:", ["Reclaiming lost material charges", "Getting paid in the driveway (cashflow)", "Whiteboard scheduling headaches", "Bypassing night-time admin work"])
    
    if st.button("📱 Generate Outbound SMS"):
        with st.spinner("AI is drafting your SMS response..."):
            time.sleep(0.8)
            
            if sms_pain == "Reclaiming lost material charges":
                sms_text = f"Hey [Name], completely hear you! Real quick: average {sms_trade.lower()} crews lose $500/mo in parts they forget to charge for. Jobtable makes it as simple as texting for techs to log materials on-site, protecting your margins. Grab 5 mins next Tuesday morning? - Ikechukwu, Jobtable"
            elif sms_pain == "Getting paid in the driveway (cashflow)":
                sms_text = f"Hey [Name], no worries! Plumbers use Jobtable to take card payments directly in the driveway as soon as the {sms_trade.lower()} job is done. Average company boosts cashflow by 20%. Grab 5 mins Tuesday morning before your first run? - Ikechukwu, Jobtable"
            elif sms_pain == "Whiteboard scheduling headaches":
                sms_text = f"Hey [Name], hear ya! Whiteboards and texts make scheduling {sms_trade.lower()} jobs a total puzzle. Jobtable is a drag-and-drop map app your guys master in 5 mins. Reclaim your office sanity. Grab 10 mins Tuesday morning? - Ikechukwu, Jobtable"
            else:
                sms_text = f"Hey [Name], understand! Most {sms_trade.lower()} owners spend their evenings doing manual invoices and double-entering into QuickBooks. Jobtable automates that so you get your nights back. Reclaim 10 hrs/week. Grab 10 mins Tuesday morning? - Ikechukwu, Jobtable"
            
            st.write("---")
            st.info(f"**Copy & Send:**\n\n`{sms_text}`")

# ----------------- TAB 4: VIDEO SCRIPT STUDIO (FULLY UNLOCKED) -----------------
with tab_videos:
    st.subheader("🎬 AI Video Prospecting Script Studio")
    st.write("Record a personalized 60-second video (Loom/Vidalytics) to send directly to a contractor. Here is your storyboard:")
    
    vid_trade = st.text_input("Target Trade Category:", value="Plumbing")
    vid_prop = st.text_input("Physical Prop in Video (e.g. Copper pipeline elbow, receipt book, mobile phone):", value="Copper pipeline joint")
    
    if st.button("🎬 Generate Video Storyboard"):
        with st.spinner("AI is storyboarding your video pitch..."):
            time.sleep(1.0)
            st.markdown(
                f"""
                ### 📹 60-Second Video Script: '{vid_prop}' Pattern
                
                *   **[0:00 - 0:10] THE HOOK (Direct & Visual):**
                    *   *Visual:* Hold the **{vid_prop}** directly in front of the camera, then pull it back to show your face.
                    *   *Audio:* *"Hey [Contractor Name], I’m holding a simple {vid_prop} here in my hand. It costs about $4, but when your field techs forget to charge for just three of these on their paper tickets, you lose $500 in profits every single month."*
                *   **[0:10 - 0:35] THE AGITATION:**
                    *   *Audio:* *"I’m Ikechukwu, an outbound representative here at Jobtable. Because I have supervised HVAC and plumbing pipeline setups in the field myself, I know how hard it is to get techs to log materials accurately on paper sheets late at night."*
                *   **[0:35 - 0:50] THE SIMPLE SOLUTION:**
                    *   *Audio:* *"That’s why trade veterans built Jobtable. It is an extremely simple app. Techs click the exact parts they used on site, and it automatically updates the invoice and syncs with QuickBooks instantly. Your crew will master it in 5 minutes."*
                *   **[0:50 - 1:00] THE CALL-TO-ACTION:**
                    *   *Audio:* *"I won't pitch you further over email. Reply to this message, and let's grab just 10 minutes next week Tuesday to see if it makes sense. Have a great day!"*
                    """
            )

# ----------------- TAB 5: OBJECTION BATTLECARDS (FULLY UNLOCKED) -----------------
with tab_battlecards:
    st.subheader("🛡️ Outbound Objection Battlecards")
    st.write("Browse through master-level B2B outbound frameworks to overcome contractor brush-offs:")
    
    obj_choice = st.selectbox("Select Objection Type:", ["I'm too busy, call me back / send an email.", "I use pen and paper / Excel and it works fine.", "We already use Jobber / ServiceTitan.", "I'm too small / don't need it."])
    
    if obj_choice == "I'm too busy, call me back / send an email.":
        st.markdown(
            """
            ### 🎯 Rebuttal Strategy: Busy Brush-off
            *   **Buyer Psychology:** Protective reflex to unscheduled phone interruptions. They assume you will waste 30 minutes reading dry slides.
            *   **Formula:** Acknowledge (A) + De-escalate (D) + Pivot (P) + Micro-Close (MC)
            *   **SDR Script Rebuttal:** 
                > *"I completely hear you, Bob. I'm catching you mid-job, so I'll let you get right back to it. Trade owners use Jobtable specifically to get paid 10 days faster. I don't want to pitch you now. Can we grab just 10 minutes next Tuesday morning before your first run, to see if it makes sense?"*
            """
        )
    elif obj_choice == "I use pen and paper / Excel and it works fine.":
        st.markdown(
            """
            ### 🎯 Rebuttal Strategy: Tech-Aversion / Pen & Paper
            *   **Buyer Psychology:** Fear of complexity and software setup. They assume software takes weeks to configure, and older techs will refuse to use it.
            *   **Formula:** Validate paper reliability + Uncover Cost of Whiteboard/Paper + Introduce simple contrast
            *   **SDR Script Rebuttal:**
                > *"Pen and paper is 100% reliable, you are right. But paper doesn't talk to QuickBooks, and it's easy for technicians to forget to charge for extra parts. Jobtable is built to be as simple as sending a text message. Technicians do it in 20 seconds, and you get paid instantly. Let me show you a 5-minute comparison."*
            """
        )
    elif obj_choice == "We already use Jobber / ServiceTitan.":
        st.markdown(
            """
            ### 🎯 Rebuttal Strategy: Competitor Lock-in
            *   **Buyer Psychology:** Comfortable with current tools and dreads the friction of migrating data.
            *   **Formula:** Respect current competitor + Introduce key performance comparison + Low friction comparative overview
            *   **SDR Script Rebuttal:**
                > *"Jobber is a solid system, absolutely. But what many contractors find is that they use about 15% of the features but pay for 100% of the price. Jobtable is focused purely on simplicity. Your team can master it in 5 minutes with zero training, and it's half the price. Can I show you a 10-minute comparison next week?"*
                """
        )
    else:
        st.markdown(
            """
            ### 🎯 Rebuttal Strategy: Small / Don't Need It
            *   **Buyer Psychology:** Perceives software as an enterprise-only cost, not a small-business administrative lifesaver.
            *   **Formula:** Reposition tool as virtual admin + Focus on growth scaling
            *   **SDR Script Rebuttal:**
                > *"We actually built Jobtable specifically for 1-5 person shops. When you're small, you don't have a full-time office admin, so you're doing double-duty as a tech and an accountant. Jobtable acts as your virtual admin, automating text reminders and dispatching. It helps you look like a 50-person company and win more high-paying commercial jobs."*
                """
            )

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed & Built by Ikechukwu Onuekwusi | Universal AI Outbound App 🎯</p>", unsafe_allow_html=True)
