import streamlit as st
import pandas as pd

# Utility Imports
from utils.quiz_logic import run_quiz
from utils.content_templates import generate_template
from utils.nil_score import calculate_score
from utils.leaderboard import display_leaderboard, earnings_estimator
from utils.pitch_deck_generator import build_pitch_deck
from utils.calendar_generator import display_calendar
from utils.nil_wizard import run_wizard
from utils.case_studies import show_case_studies
from utils.course_quiz import run_nil_course
from utils.contact_handler import record_to_sheet, send_email, get_email_body
from utils.admin_tools import check_admin_access, show_admin_dashboard, get_toggle_states, render_admin_banner
from utils.partner_admin import show_partner_admin
from utils.advertisements import show_ad
from utils.partner_config import get_partner_config, show_partner_toggle_panel
from utils.changelog_viewer import display_changelog
from utils.admin_debug import render_admin_debug_panel  # ✅ NEW DEBUG PANEL IMPORT

# ✅ Page Setup
st.set_page_config(page_title="NextPlay NIL", layout="centered")

# ✅ Session State Initialization
if "selected_sport" not in st.session_state:
    st.session_state["selected_sport"] = "Football"
if "partner_mode" not in st.session_state:
    st.session_state["partner_mode"] = False

# ✅ Admin Mode
is_admin = check_admin_access()
if is_admin:
    render_admin_banner()
    show_admin_dashboard()

    with st.sidebar:
        if st.button("🧩 Partner Config Panel"):
            show_partner_admin()
            show_partner_toggle_panel()

        with st.expander("📄 View Changelog"):
            display_changelog()

        with st.expander("🛠️ Live Admin Panel"):
            render_admin_debug_panel()

# ✅ Partner Mode Toggle (Safe Assignment)
partner_mode_toggle = st.sidebar.checkbox("🎛️ Enable Partner Mode", value=st.session_state["partner_mode"])
st.session_state["partner_mode"] = partner_mode_toggle

# ✅ Partner Mode Dashboard
if is_admin and st.session_state["partner_mode"]:
    st.header("🧩 Partner Mode Dashboard")
    show_partner_toggle_panel()

# ✅ Test Mode
test_mode = st.sidebar.checkbox("🧪 Enable Test Mode (Safe Demo)", key="test_mode_checkbox")
if test_mode:
    st.sidebar.warning("Test Mode is ON — No data will be saved or emailed.")
    st.markdown("### ⚠️ TEST MODE: No data will be sent or stored.", unsafe_allow_html=True)

# ✅ Load Toggles
toggle_states = get_toggle_states()
partner_config = get_partner_config()

# ✅ Sponsored Header Ad
if toggle_states.get("admin_toggle_enable_ads", False) and partner_config.get("partner_toggle_enable_partner_ads", False):
    st.markdown("### 📢 Sponsored Message")
    show_ad(location="header_ad", sport=st.session_state.get("selected_sport", "Football"))

# ✅ App Branding
st.title("🏈 NextPlay NIL")
st.subheader("Own your brand. Win your next play.")
st.subheader("Your NIL Strategy & Branding Assistant")

# ✅ Step 0: NIL Education
with st.expander("🎓 NIL Education"):
    run_nil_course()

# ✅ Step 1: NIL Readiness Quiz
if toggle_states.get("admin_toggle_step_1", True) and not partner_config.get("partner_toggle_hide_quiz", False):
    st.header("Step 1: NIL Readiness Quiz")
    quiz_score = 72 if test_mode else run_quiz()
    if quiz_score:
        st.success(f"🎯 Your NIL Match Score: {quiz_score}/100")
        st.markdown(calculate_score(quiz_score))
        estimated_earnings = earnings_estimator(quiz_score)
        st.info(f"💰 Estimated NIL Earning Potential: ${estimated_earnings:,.2f}")

# ✅ Step 2: NIL Business Tools
if toggle_states.get("admin_toggle_step_2", True):
    st.header("Step 2: NIL Business Tools")
    deal_type = st.selectbox("Pick your need:", ["Brand Outreach Email", "Contract Template", "Social Media Post", "Thank You Note"])
    custom_name = st.text_input("Enter Athlete or Brand Name:")
    if st.button("Generate My Template"):
        if custom_name:
            st.code(generate_template(deal_type, custom_name), language="markdown")
        else:
            st.warning("Please enter a name or brand.")

# ✅ Step 3: Deal Builder Wizard
if toggle_states.get("admin_toggle_step_3", True):
    st.header("🧾 Step 3: NIL Deal Builder Wizard")
    run_wizard()

# ✅ Step 4: Pitch Deck Generator
if toggle_states.get("admin_toggle_step_4", True) and partner_config.get("partner_toggle_enable_pitch", True):
    st.header("📊 Step 4: NIL Pitch Deck Generator")
    with st.form("pitch_deck_form"):
        name = st.text_input("Your Name")
        sport = st.text_input("Sport")
        followers = st.text_input("Social Followers (e.g., 2500 IG, 1200 TikTok)")
        stats = st.text_input("Top 3 Athletic Stats")
        goals = st.text_area("What are your NIL goals?")
        pitch_submitted = st.form_submit_button("Generate Pitch Deck")
        if pitch_submitted:
            st.code(build_pitch_deck(name, sport, followers, stats, goals), language="markdown")

# ✅ Step 5: Weekly Content Plan
if toggle_states.get("admin_toggle_step_5", True):
    st.header("📅 Step 5: Weekly Content Plan")
    display_calendar()

# ✅ Step 6: NIL Success Stories
if toggle_states.get("admin_toggle_step_6", True):
    st.header("📚 Step 6: Real NIL Success Stories")
    show_case_studies()

# ✅ Step 7: Contact Form
if toggle_states.get("admin_toggle_step_7", True) and partner_config.get("partner_toggle_allow_contact_form", True):
    st.header("📥 Step 7: Stay in the NIL Loop")
    with st.form("contact_form"):
        name = st.text_input("Your Full Name")
        email = st.text_input("Your Email")
        school = st.text_input("School or Program")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not test_mode:
            record_to_sheet(name, email, school)
            success, email_body = send_email(name, email, quiz_score)
        else:
            pd.DataFrame([[name, email, school, quiz_score]], columns=["Name", "Email", "School", "Score"]) \
              .to_csv("test_mode_log.csv", mode="a", index=False, header=False)
            success = True
            email_body = get_email_body(name, quiz_score)

        if success:
            st.success("✅ Your info has been recorded. We will follow up with NIL tips and updates.")
            st.markdown("### 📄 Preview of Email Sent:")
            st.code(email_body)
            if st.button("📤 Resend Email"):
                send_email(name, email, quiz_score)

# ✅ Always Show Leaderboard
display_leaderboard()
