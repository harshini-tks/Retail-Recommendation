import sys
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.data_loader import load_users, get_all_areas, get_all_schools
from src.services.profile_service import ShopperProfile, build_profile_from_user_id, build_profile_from_form
from src.agent.recommendation_agent import RecommendationAgent

load_dotenv()

st.set_page_config(page_title="Shopping Assistant", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .main-header { font-size: 2.8rem; font-weight: 700; background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.15rem; color: #64748b; margin-bottom: 2rem; font-weight: 300; }
    .profile-sidebar { background: linear-gradient(145deg, #f8fafc, #f1f5f9); padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .profile-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; margin-top: 1rem; letter-spacing: 0.1em; }
    .profile-label:first-child { margin-top: 0; }
    .profile-value { font-size: 1.1rem; color: #0f172a; font-weight: 500; margin-bottom: 0.3rem; }
    /* Streamlit overrides for better aesthetics */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 10px 20px; transition: background-color 0.2s ease; font-size:1.1rem;}
    .stTabs [data-baseweb="tab"]:hover { background-color: #f1f5f9; }
    .stMarkdown p, .stMarkdown li { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("AI Shopper Assistant")
    st.divider()

    if not st.session_state.get("run_agent"):
        user_mode = st.radio("Mode", ["Existing User", "New User"], label_visibility="collapsed")
        
        if user_mode == "Existing User":
            users_df = load_users()
            user_options = {f"{r['user_id']} - {r['name']}": r['user_id'] for _, r in users_df.iterrows()}
            selected_uid = user_options[st.selectbox("Select User", list(user_options.keys()))]
            if st.button("Get Recommendations", use_container_width=True):
                st.session_state["profile"] = build_profile_from_user_id(selected_uid)
                st.session_state["run_agent"] = True
                st.rerun()
        else:
            with st.form("new_user"):
                name = st.text_input("Name")
                col1, col2 = st.columns(2)
                age = col1.number_input("Age", 10, 80, 22)
                gender = col2.selectbox("Gender", ["Male", "Female", "Other"])
                area = st.selectbox("Area", sorted(get_all_areas()))
                school = st.selectbox("School", sorted(get_all_schools()))
                style = st.selectbox("Style", ["Casual", "Formal", "Ethnic", "Sporty", "Streetwear"])
                col3, col4 = st.columns(2)
                brand = col3.text_input("Brand (e.g. Zara)")
                colour = col4.text_input("Colour (e.g. Blue)")
                col5, col6 = st.columns(2)
                b_min = col5.number_input("Min (₹)", 100, 50000, 300)
                b_max = col6.number_input("Max (₹)", 100, 50000, 3000)
                if st.form_submit_button("Get Recommendations", use_container_width=True):
                    st.session_state["profile"] = build_profile_from_form({
                        "name": name, "age": age, "gender": gender, "area": area, "school": school,
                        "style_pref": style, "budget_min": b_min, "budget_max": b_max,
                        "brand_pref": brand, "colour_pref": colour
                    })
                    st.session_state["run_agent"] = True
                    st.rerun()
    else:
        cp = st.session_state["profile"]
        st.markdown("### Shopper Details")
        
        st.markdown('<div class="profile-label">Full Name</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.name}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-label">Age & Gender</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.age} | {cp.gender}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-label">Area</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.area}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-label">School / Org</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.school}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-label">Style Preference</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.style_pref}</div>', unsafe_allow_html=True)

        st.markdown('<div class="profile-label">Preferred Brand</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.brand_pref or "N/A"}</div>', unsafe_allow_html=True)

        st.markdown('<div class="profile-label">Favourite Colour</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">{cp.colour_pref or "N/A"}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="profile-label">Budget Range</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="profile-value">₹{int(cp.budget_min)} - ₹{int(cp.budget_max)}</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
        
        if st.button("New User", use_container_width=True):
            st.session_state["run_agent"] = False
            st.session_state.pop("agent_results", None)
            st.rerun()

    st.divider()
    if st.session_state.get("chat_mode"):
        if st.button("⬅Back to Shopping Report", use_container_width=True):
            st.session_state["chat_mode"] = False
            st.rerun()
    else:
        if st.button("Chat Bot", use_container_width=True):
            st.session_state["chat_mode"] = True
            st.rerun()

def render_chat_interface():
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {"role": "assistant", "content": "Hello! I am your AI Shopping Assistant. Ask me anything about local trends, events, or product suggestions!"}
        ]
        
    for msg in st.session_state["chat_messages"]:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Ask about trends or products..."):
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            from src.agent.chat_agent import ChatAgent
            if "chat_agent" not in st.session_state:
                st.session_state["chat_agent"] = ChatAgent()
            
            history = " ".join([f"{m['role']}: {m['content']}" for m in st.session_state["chat_messages"][:-1]])
            response = st.write_stream(st.session_state["chat_agent"].stream_run(prompt, history))
            
        st.session_state["chat_messages"].append({"role": "assistant", "content": response})

st.markdown('<div class="main-header">AI Shopper Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personalised Retail Recommendations</div>', unsafe_allow_html=True)

if st.session_state.get("chat_mode"):
    st.markdown("### Chat with AI Shopper Assistant")
    render_chat_interface()
else:
    if not st.session_state.get("run_agent"):
        st.info("Select a user in the sidebar to generate a complete personalised shopping report.")
    else:
        cp = st.session_state["profile"]
        
        if "agent_results" not in st.session_state:
            with st.status("Orchestrating agent tools...", expanded=True) as status:
                st.write("Initializing parallel workers...")
                st.session_state["agent_results"] = {}
                
                for key, value in RecommendationAgent().run_incremental(cp):
                    if key == "llm_reasoning_stream":
                        st.session_state["reasoning_stream"] = value
                    else:
                        st.session_state["agent_results"][key] = value
                        st.write(f"Updated: {key.replace('_', ' ').title()}")
                
                status.update(label="Report Intelligence Gathered!", state="complete", expanded=False)
                
        results = st.session_state["agent_results"]

        tabs = st.tabs(["Products", "Planning", "Trends", "Social", "Events", "AI Logic"])
        mapping = [
            ("Top Picks & Alternatives", "recommendations"),
            ("Purchase Plan", "purchase_plan"),
            ("Local Trends", "trend_insights"),
            ("Social Influence", "social_insights"),
            ("Event Context", "event_insights"),
            ("Reasoning", "llm_reasoning")
        ]

        for i, (title, key) in enumerate(mapping):
            with tabs[i]:
                with st.container(border=True):
                    if key == "llm_reasoning":
                        st.subheader(title)
                        if "reasoning_stream" in st.session_state:
                            st.write_stream(st.session_state["reasoning_stream"])
                            st.session_state["agent_results"]["llm_reasoning"] = "Done" 
                            del st.session_state["reasoning_stream"]
                        elif results.get("llm_reasoning"):
                            st.info("Reasoning analysis complete.")
                        
                        st.caption(results.get("disclaimer", ""))
                    else:
                        val = results.get(key)
                        if val:
                            st.markdown(val)
                        else:
                            st.write("Loading data...")
