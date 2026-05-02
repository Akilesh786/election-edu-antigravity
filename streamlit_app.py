"""
streamlit_app.py
================
Premium Streamlit UI for the Election Process Education tool.
Imports core logic from election_guide.py.

Integrates Google Cloud Logging for structured audit trails of every
major user interaction. Falls back gracefully when GCP credentials are
unavailable (e.g. local development).

Run with:
    streamlit run streamlit_app.py
"""

import logging
import traceback

import streamlit as st

# ── Google Cloud Logging ──────────────────────────────────────────────────────
try:
    import google.cloud.logging as gcp_logging

    _gcp_client = gcp_logging.Client()
    _gcp_client.setup_logging()          # routes GCP log entries to stdlib logging
    _logger = logging.getLogger("election_edu")
    _logger.setLevel(logging.INFO)
    _logger.info("google-cloud-logging initialised successfully.")
except Exception:                        # no GCP credentials in dev / CI
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    _logger = logging.getLogger("election_edu")
    _logger.warning("google-cloud-logging unavailable; falling back to stdlib logging.")

# ── Core domain imports ───────────────────────────────────────────────────────
from election_guide import (
    check_voter_eligibility,
    REGISTRATION_STEPS,
    FAQ,
    MINIMUM_VOTING_AGE,
)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Election Education Hub",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS – dark navy theme with gold accents ────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg,#0a0f1e 0%,#111827 50%,#0d1b2a 100%); color:#e2e8f0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f172a 0%,#1e293b 100%); border-right:1px solid rgba(245,166,35,.2); }
[data-testid="stSidebar"] .stRadio label { color:#94a3b8!important; font-size:.95rem; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { color:#f5a623!important; }
.hero { background:linear-gradient(135deg,#1e3a5f 0%,#0f2744 50%,#1a1a2e 100%); border:1px solid rgba(245,166,35,.3); border-radius:20px; padding:48px 40px; text-align:center; position:relative; overflow:hidden; margin-bottom:32px; box-shadow:0 25px 60px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.05); }
.hero::before { content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background:radial-gradient(ellipse at center,rgba(245,166,35,.08) 0%,transparent 60%); animation:pulse 4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:.6;transform:scale(1)} 50%{opacity:1;transform:scale(1.05)} }
.hero-icon { font-size:4rem; margin-bottom:12px; }
.hero h1 { font-size:2.8rem; font-weight:800; background:linear-gradient(90deg,#f5a623,#ffd580,#f5a623); background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation:shimmer 3s linear infinite; margin:0 0 12px; }
@keyframes shimmer { 0%{background-position:0% 50%} 100%{background-position:200% 50%} }
.hero p { color:#94a3b8; font-size:1.1rem; max-width:600px; margin:0 auto; }
.glass-card { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:28px 32px; margin-bottom:20px; backdrop-filter:blur(10px); transition:transform .2s,box-shadow .2s; }
.glass-card:hover { transform:translateY(-2px); box-shadow:0 12px 40px rgba(0,0,0,.4); }
.section-title { font-size:1.6rem; font-weight:700; color:#f5a623; margin-bottom:6px; }
.section-sub { color:#64748b; font-size:.95rem; margin-bottom:24px; }
.result-eligible { background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(5,150,105,.08)); border:1px solid rgba(16,185,129,.4); border-radius:14px; padding:24px 28px; text-align:center; }
.result-ineligible { background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(185,28,28,.08)); border:1px solid rgba(239,68,68,.4); border-radius:14px; padding:24px 28px; text-align:center; }
.result-icon { font-size:3rem; margin-bottom:8px; }
.result-title { font-size:1.4rem; font-weight:700; margin-bottom:8px; }
.result-detail { color:#94a3b8; font-size:.95rem; }
.step-card { background:rgba(255,255,255,.03); border-left:4px solid #f5a623; border-radius:0 12px 12px 0; padding:18px 22px; margin-bottom:14px; transition:all .25s; }
.step-card.done { border-left-color:#10b981; background:rgba(16,185,129,.06); }
.step-card:hover { background:rgba(255,255,255,.06); }
.step-num { display:inline-block; background:#f5a623; color:#0a0f1e; font-weight:800; font-size:.78rem; border-radius:50%; width:26px; height:26px; line-height:26px; text-align:center; margin-right:10px; }
.step-num.done { background:#10b981; }
.step-title { font-weight:600; font-size:1rem; color:#e2e8f0; }
.step-detail { color:#64748b; font-size:.88rem; margin-top:6px; line-height:1.6; }
.faq-q { font-weight:600; color:#cbd5e1; font-size:.97rem; }
.faq-a { color:#64748b; font-size:.9rem; line-height:1.7; margin-top:6px; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#f5a623,#ffd580); border-radius:9999px; }
.stButton > button { background:linear-gradient(135deg,#f5a623,#d97706); color:#0a0f1e; border:none; border-radius:10px; font-weight:700; font-size:.95rem; padding:10px 28px; transition:all .2s; box-shadow:0 4px 15px rgba(245,166,35,.3); }
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(245,166,35,.4); }
.stNumberInput input,.stSelectbox select,.stRadio { background:rgba(255,255,255,.05)!important; border-color:rgba(255,255,255,.1)!important; color:#e2e8f0!important; border-radius:10px!important; }
.stat-box { background:rgba(255,255,255,.04); border:1px solid rgba(245,166,35,.2); border-radius:14px; padding:20px; text-align:center; }
.stat-value { font-size:2.2rem; font-weight:800; color:#f5a623; }
.stat-label { color:#64748b; font-size:.85rem; margin-top:4px; }
hr { border-color:rgba(255,255,255,.06)!important; }
#MainMenu, footer { visibility:hidden; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:20px 0 10px;'>
      <div style='font-size:2.5rem;'>🗳️</div>
      <div style='font-size:1.1rem; font-weight:700; color:#f5a623; margin-top:6px;'>Election Hub</div>
      <div style='font-size:.78rem; color:#475569; margin-top:3px;'>Education &amp; Civic Guide</div>
    </div>
    <hr style='border-color:rgba(245,166,35,.2); margin:14px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        options=["🏠  Home", "✅  Eligibility Check", "📋  Registration Guide", "❓  Election FAQ"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <hr style='border-color:rgba(245,166,35,.2); margin:20px 0 14px;'>
    <div style='font-size:.78rem; color:#334155; text-align:center; line-height:1.6;'>
      Empowering citizens through<br>election education 🌐
    </div>
    """, unsafe_allow_html=True)

_logger.info("User navigated to page: %s", page)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def render_hero(icon: str, title: str, subtitle: str) -> None:
    """Render a full-width hero banner at the top of a page.

    Args:
        icon: An emoji or short string displayed above the title.
        title: The main heading text for the hero section.
        subtitle: A short descriptive sentence shown below the title.
    """
    st.markdown(f"""
    <div class="hero">
      <div class="hero-icon">{icon}</div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_title(title: str, sub: str = "") -> None:
    """Render a styled section heading with an optional sub-label.

    Args:
        title: Primary section heading text.
        sub: Optional secondary label displayed in a muted style.
    """
    st.markdown(f"""
    <div class="section-title">{title}</div>
    <div class="section-sub">{sub}</div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Global try-except wrapper — catches unhandled runtime errors
# ─────────────────────────────────────────────────────────────────────────────
try:

    # ── PAGE: Home ────────────────────────────────────────────────────────────
    if page == "🏠  Home":
        _logger.info("User viewed Home page.")
        render_hero(
            "🗳️",
            "Election Education Hub",
            "Your interactive guide to understanding voting, eligibility, and the registration process.",
        )

        c1, c2, c3, c4 = st.columns(4)
        stats = [
            ("18+", "Minimum Voting Age"),
            (str(len(REGISTRATION_STEPS)), "Registration Steps"),
            (str(len(FAQ)), "FAQ Topics"),
            ("100%", "Free & Open Access"),
        ]
        for col, (val, lbl) in zip([c1, c2, c3, c4], stats):
            with col:
                st.markdown(f"""
                <div class="stat-box">
                  <div class="stat-value">{val}</div>
                  <div class="stat-label">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        render_section_title("What You Can Do Here", "Choose a section from the sidebar to get started.")
        f1, f2, f3 = st.columns(3)
        features = [
            ("✅", "Eligibility Check",
             "Enter your age and citizenship status to instantly find out if you are eligible to vote."),
            ("📋", "Registration Guide",
             "Walk through a clear, step-by-step process to register as a voter — with progress tracking."),
            ("❓", "Election FAQ",
             "Get quick, plain-language answers to the most common questions about elections."),
        ]
        for col, (icon, feat_title, desc) in zip([f1, f2, f3], features):
            with col:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;">
                  <div style="font-size:2.2rem; margin-bottom:12px;">{icon}</div>
                  <div style="font-size:1.05rem; font-weight:700; color:#f5a623; margin-bottom:8px;">{feat_title}</div>
                  <div style="color:#64748b; font-size:.88rem; line-height:1.6;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="background:rgba(245,166,35,.06); border-color:rgba(245,166,35,.25);">
          <div style="display:flex; align-items:center; gap:14px;">
            <div style="font-size:2rem;">💡</div>
            <div>
              <div style="font-weight:600; color:#f5a623; margin-bottom:4px;">Did you know?</div>
              <div style="color:#94a3b8; font-size:.92rem;">
                Voter turnout increases significantly when citizens are well-informed about the process.
                An educated electorate leads to stronger democracies and better governance for everyone.
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── PAGE: Eligibility Check ───────────────────────────────────────────────
    elif page == "✅  Eligibility Check":
        _logger.info("User opened Eligibility Check page.")
        render_hero("✅", "Voter Eligibility Check",
                    "Answer two quick questions to find out if you're eligible to vote.")

        col_form, col_info = st.columns([1.2, 1], gap="large")

        with col_form:
            render_section_title("Your Details", "All fields are required.")

            with st.form("eligibility_form", clear_on_submit=False):
                age = st.number_input(
                    "Your Age",
                    min_value=1, max_value=120, value=25, step=1,
                    help="Enter your current age in years.",
                )
                citizenship = st.selectbox(
                    "Citizenship Status",
                    ["Yes, I am a citizen", "No, I am not a citizen"],
                    help="Select your citizenship status in this country.",
                )
                submitted = st.form_submit_button("Check My Eligibility →", use_container_width=True)

            if submitted:
                is_citizen = citizenship.startswith("Yes")
                eligible, reason = check_voter_eligibility(int(age), is_citizen)
                _logger.info(
                    "Eligibility check: age=%d, is_citizen=%s, eligible=%s",
                    int(age), is_citizen, eligible,
                )

                st.markdown("<br>", unsafe_allow_html=True)
                if eligible:
                    st.markdown(f"""
                    <div class="result-eligible">
                      <div class="result-icon">🎉</div>
                      <div class="result-title" style="color:#10b981;">You Are Eligible to Vote!</div>
                      <div class="result-detail">{reason}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.markdown(f"""
                    <div class="result-ineligible">
                      <div class="result-icon">❌</div>
                      <div class="result-title" style="color:#ef4444;">Not Yet Eligible</div>
                      <div class="result-detail">{reason}</div>
                    </div>
                    """, unsafe_allow_html=True)

        with col_info:
            render_section_title("Eligibility Criteria", "Requirements you must meet to vote.")
            criteria = [
                ("🎂", "Minimum Age",
                 f"You must be at least {MINIMUM_VOTING_AGE} years old on or before election day."),
                ("🌍", "Citizenship",
                 "You must be a registered citizen of the country where you wish to vote."),
                ("🏠", "Residency",
                 "Some regions require proof of address within the constituency."),
                ("📋", "Registration",
                 "Being eligible is not enough — you must also be registered to vote."),
            ]
            for icon, crit_title, detail in criteria:
                st.markdown(f"""
                <div class="glass-card" style="padding:16px 20px; margin-bottom:12px;">
                  <div style="display:flex; align-items:flex-start; gap:12px;">
                    <span style="font-size:1.4rem;">{icon}</span>
                    <div>
                      <div style="font-weight:600; color:#cbd5e1; font-size:.95rem;">{crit_title}</div>
                      <div style="color:#64748b; font-size:.84rem; margin-top:3px; line-height:1.5;">{detail}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── PAGE: Registration Guide ──────────────────────────────────────────────
    elif page == "📋  Registration Guide":
        _logger.info("User opened Registration Guide page.")
        render_hero(
            "📋",
            "Voter Registration Guide",
            f"A clear {len(REGISTRATION_STEPS)}-step process to register and cast your vote.",
        )

        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()

        completed = len(st.session_state.completed_steps)
        total = len(REGISTRATION_STEPS)
        progress = completed / total

        st.markdown(f"""
        <div class="glass-card" style="margin-bottom:28px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <div style="font-weight:600; color:#e2e8f0; font-size:1rem;">Your Progress</div>
            <div style="font-size:1.1rem; font-weight:700; color:#f5a623;">{completed}/{total} steps</div>
          </div>
        """, unsafe_allow_html=True)
        st.progress(progress)
        st.markdown("</div>", unsafe_allow_html=True)

        if completed == total:
            _logger.info("User completed all registration steps.")
            st.markdown("""
            <div class="result-eligible" style="margin-bottom:28px;">
              <div class="result-icon">🎉</div>
              <div class="result-title" style="color:#10b981;">Registration Complete!</div>
              <div class="result-detail">You have completed all registration steps. Remember to bring your ID on election day!</div>
            </div>
            """, unsafe_allow_html=True)

        col_steps, col_sidebar = st.columns([1.6, 1], gap="large")

        with col_steps:
            render_section_title("Registration Steps", "Check off each step as you complete it.")
            for idx, step in enumerate(REGISTRATION_STEPS, start=1):
                done = idx in st.session_state.completed_steps
                num_cls = "done" if done else ""
                card_cls = "step-card done" if done else "step-card"

                st.markdown(f"""
                <div class="{card_cls}">
                  <span class="step-num {num_cls}">{"✓" if done else idx}</span>
                  <span class="step-title">{step['title']}</span>
                  <div class="step-detail">{step['detail']}</div>
                </div>
                """, unsafe_allow_html=True)

                btn_label = "✓ Mark Done" if not done else "↩ Undo"
                if st.button(btn_label, key=f"step_{idx}"):
                    if done:
                        st.session_state.completed_steps.discard(idx)
                        _logger.info("User undid registration step %d.", idx)
                    else:
                        st.session_state.completed_steps.add(idx)
                        _logger.info("User completed registration step %d.", idx)
                    st.rerun()

        with col_sidebar:
            render_section_title("Quick Tips", "Keep these in mind during registration.")
            tips = [
                ("📅", "Check Deadlines",
                 "Registration typically closes 15–30 days before election day."),
                ("📄", "Prepare Docs",
                 "Have your ID and proof of address ready before starting."),
                ("🔍", "Verify Status",
                 "Always confirm your registration is active after submitting."),
                ("📬", "Absentee Ballot",
                 "Ask about postal voting if you cannot attend in person."),
            ]
            for icon, tip_title, tip_body in tips:
                st.markdown(f"""
                <div class="glass-card" style="padding:14px 18px; margin-bottom:12px;">
                  <div style="font-size:1.3rem; margin-bottom:6px;">{icon}</div>
                  <div style="font-weight:600; color:#f5a623; font-size:.9rem; margin-bottom:4px;">{tip_title}</div>
                  <div style="color:#64748b; font-size:.83rem; line-height:1.5;">{tip_body}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Reset Progress", use_container_width=True):
                st.session_state.completed_steps = set()
                _logger.info("User reset registration progress.")
                st.rerun()

    # ── PAGE: Election FAQ ────────────────────────────────────────────────────
    elif page == "❓  Election FAQ":
        _logger.info("User opened Election FAQ page.")
        render_hero(
            "❓",
            "Election FAQ",
            "Plain-language answers to the most common questions about elections and voting.",
        )

        render_section_title(
            "Frequently Asked Questions",
            "Click on any question to expand the answer.",
        )

        faq_extended = {
            **FAQ,
            "5": (
                "How do I find my polling station?",
                "After registration, your election authority will notify you of your assigned polling "
                "station by mail or via their online portal. You can also use the station-locator tool "
                "on your national election commission's website by entering your registered address.",
            ),
            "6": (
                "Can I change my registered address?",
                "Yes. If you move before an election, update your registration with your new address "
                "as soon as possible. Most authorities allow online updates. Check the deadline for "
                "address changes in your jurisdiction.",
            ),
            "7": (
                "What ID do I need on election day?",
                "Requirements vary by country and region, but commonly accepted IDs include a "
                "government-issued photo ID (passport, national ID card, or driver's licence). "
                "Some regions also accept utility bills or bank statements as proof of identity.",
            ),
            "8": (
                "Is voting mandatory?",
                "In most countries, voting is voluntary. However, some countries (e.g., Australia, "
                "Belgium) have compulsory voting laws where eligible citizens are legally required "
                "to cast a ballot or may face a fine.",
            ),
        }

        search_query = st.text_input("🔍  Search questions…", placeholder="Type a keyword…")
        if search_query:
            _logger.info("User searched FAQ with query: '%s'", search_query)

        for key, (question, answer) in faq_extended.items():
            if (
                search_query.lower() in question.lower()
                or search_query.lower() in answer.lower()
                or not search_query
            ):
                with st.expander(f"  {question}", expanded=False):
                    st.markdown(f'<div class="faq-a">💬 {answer}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="text-align:center; background:rgba(245,166,35,.05); border-color:rgba(245,166,35,.2);">
          <div style="font-size:1.5rem; margin-bottom:8px;">📞</div>
          <div style="font-weight:600; color:#f5a623; margin-bottom:4px;">Still have questions?</div>
          <div style="color:#64748b; font-size:.9rem;">
            Contact your local election authority or visit the official national election commission
            website for jurisdiction-specific guidance.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Global runtime error handler ──────────────────────────────────────────────
except Exception as exc:  # noqa: BLE001
    _logger.error(
        "Unhandled runtime error on page '%s': %s\n%s",
        page,
        exc,
        traceback.format_exc(),
    )
    st.error(
        "⚠️ An unexpected error occurred. The issue has been logged automatically. "
        "Please refresh the page or contact support if the problem persists."
    )
