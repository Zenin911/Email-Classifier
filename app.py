"""
app.py — Streamlit Main App (Analyze Email landing page)
After analysis, navigates to Dashboard.
"""
import streamlit as st
import time
import datetime
from classifier import EmailClassifier, ROUTING_MAP, REPLY_TEMPLATES

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Email Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }

    /* Result Badge */
    .result-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
    }
    .urgency-high {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
    }
    .urgency-medium {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #1a1a2e;
    }
    .urgency-low {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: #1a1a2e;
    }

    /* Category colors */
    .cat-complaint { border-left: 4px solid #FF6B6B; }
    .cat-feedback { border-left: 4px solid #4ECDC4; }
    .cat-other { border-left: 4px solid #34D399; }
    .cat-spam { border-left: 4px solid #6C757D; }
    .cat-support { border-left: 4px solid #45B7D1; }

    /* Confidence meter */
    .confidence-bar {
        height: 12px;
        border-radius: 6px;
        background: rgba(255,255,255,0.1);
        overflow: hidden;
        margin-top: 8px;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 1s ease;
    }

    /* Header gradient */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: rgba(255,255,255,0.5);
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    /* Input styling */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.3s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.4) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 12px !important;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Glass panel */
    .glass-panel {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
    }

    /* Routing badge */
    .routing-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
    }

    /* Animate in */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }

    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Initialize Session State ────────────────────────────────────────────────
if "classified_emails" not in st.session_state:
    st.session_state.classified_emails = []
if "classifier" not in st.session_state:
    try:
        st.session_state.classifier = EmailClassifier()
    except Exception as e:
        st.session_state.classifier = None
        st.session_state.model_error = str(e)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3rem;">🧠</div>
        <div style="font-size: 1.3rem; font-weight: 800; 
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            AI Email Classifier
        </div>
        <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-top: 4px;">
            Smart Classification Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Apply pending navigation BEFORE radio renders
    nav_index = 0
    if st.session_state.pop("_go_dashboard", False):
        nav_index = 1

    # Navigation
    page = st.radio(
        "Navigation",
        ["📧 Analyze Email", "📊 Dashboard"],
        index=nav_index,
        label_visibility="collapsed",
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Stats in sidebar
    total = len(st.session_state.classified_emails)
    high_count = sum(1 for e in st.session_state.classified_emails if e["urgency"] == "High")
    st.markdown(f"""
    <div style="padding: 16px; background: rgba(255,255,255,0.03); border-radius: 12px;">
        <div style="color: rgba(255,255,255,0.4); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">Session Stats</div>
        <div style="display: flex; justify-content: space-between; margin-top: 12px;">
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">{total}</div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">Analyzed</div>
            </div>
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ff416c;">{high_count}</div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.4);">High Priority</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── EXAMPLES ────────────────────────────────────────────────────────────────
EXAMPLE_EMAILS = [
    {
        "sender": "angry.customer@mail.com",
        "subject": "Worst Service Ever",
        "body": "I am writing to formally complain about a terrible experience with refund refused where the agent yelled at me and as a result I am very upset which is unacceptable. I demand to speak with your manager immediately. This is the worst service I have ever received."
    },
    {
        "sender": "happy.user@gmail.com",
        "subject": "Great Product Review",
        "body": "What a wonderful spice blend it is generous and added a kick truly a game changer. The packaging was eco-friendly and the flavor exceeded my expectations. I would highly recommend it to everyone."
    },
    {
        "sender": "sarah@company.com",
        "subject": "Tech Support Needed",
        "body": "Hello support team I am facing an issue with driver missing specifically when streaks on page and I need you to clean heads as soon as possible. I have tried restarting but the problem persists. Please help."
    },
    {
        "sender": "no-reply@suspicious.xyz",
        "subject": "Urgent: Your Account Compromised",
        "body": "Warning your account has been compromised due to delivery exception and we observed suspicious activity you must verify details to lock your account now. Click here immediately to secure your assets before it is too late."
    },
    {
        "sender": "friend@chat.com",
        "subject": "Random Thought",
        "body": "Hey did you hear the news concerning the fantasy novel apparently on sale now which is huge considering inspiration. I was just thinking about it the other day and realized how fascinating the world building is."
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYZE EMAIL PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📧 Analyze Email":
    st.markdown('<div class="main-header">📧 Analyze Email</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Paste an email to classify it with AI-powered intelligence</div>', unsafe_allow_html=True)

    if st.session_state.classifier is None:
        st.error(f"⚠ Models not loaded. Run `python train_model.py` first.\n\nError: {st.session_state.get('model_error', 'Unknown')}")
        st.stop()

    # ─── Apply pending example BEFORE widgets render ────────────────────
    if "_pending_example" in st.session_state:
        ex = st.session_state.pop("_pending_example")
        st.session_state["input_sender"] = ex["sender"]
        st.session_state["input_subject"] = ex["subject"]
        st.session_state["input_body"] = ex["body"]

    # ─── Input Section ───────────────────────────────────────────────────
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sender_email = st.text_input(
            "📬 Sender Email",
            placeholder="customer@example.com",
            key="input_sender",
        )
    with col2:
        subject_line = st.text_input(
            "📄 Subject Line",
            placeholder="Enter email subject",
            key="input_subject",
        )

    email_content = st.text_area(
        "📝 Email Content",
        placeholder="Paste the email content here...",
        height=200,
        key="input_body",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ─── Action Buttons ──────────────────────────────────────────────────
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        classify_btn = st.button("🚀 Classify Email", use_container_width=True)
    with col_btn2:
        example_btn = st.button("💡 Load Example", use_container_width=True)

    if example_btn:
        import random
        st.session_state["_pending_example"] = random.choice(EXAMPLE_EMAILS)
        st.rerun()

    # ─── Classification ──────────────────────────────────────────────────
    if classify_btn and email_content:
        full_text = f"Subject: {subject_line}\n\n{email_content}" if subject_line else email_content

        with st.spinner(""):
            # Show processing animation
            progress_placeholder = st.empty()
            steps = [
                ("🔍 Preprocessing text...", 0.3),
                ("🧮 Extracting features...", 0.3),
                ("🧠 Running AI classifier...", 0.4),
                ("✅ Classification complete!", 0.2),
            ]
            for step_text, delay in steps:
                progress_placeholder.markdown(f"""
                <div style="text-align: center; padding: 20px; color: rgba(255,255,255,0.7);">
                    <div style="font-size: 1.2rem;">{step_text}</div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(delay)
            progress_placeholder.empty()

        # Get prediction
        result = st.session_state.classifier.predict(full_text)
        category = result["category"]
        urgency = result["urgency"]
        confidence = result["confidence"]
        routing = ROUTING_MAP.get(category, {"team": "General Support", "color": "#888"})

        # Save to session
        email_record = {
            "id": len(st.session_state.classified_emails) + 1,
            "sender": sender_email or "Unknown",
            "subject": subject_line or "No Subject",
            "content": email_content[:200] + "..." if len(email_content) > 200 else email_content,
            "full_content": email_content,
            "category": category,
            "urgency": urgency,
            "confidence": confidence,
            "team": routing["team"],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.classified_emails.append(email_record)

        # Store result for persistent display
        st.session_state["last_result"] = {
            **result,
            "routing": routing,
        }

    elif classify_btn and not email_content:
        st.warning("⚠ Please enter email content to classify.")

    # ─── Show Results (persists across reruns) ────────────────────────────
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        category = result["category"]
        urgency = result["urgency"]
        confidence = result["confidence"]
        routing = result["routing"]

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="main-header" style="font-size: 1.8rem;">🎯 Classification Result</div>', unsafe_allow_html=True)

        # Top result cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card animate-in">
                <div class="metric-label">Category</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: {routing['color']}; margin-top: 8px;">
                    {category}
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {result['cat_confidence']*100}%; background: linear-gradient(90deg, {routing['color']}, {routing['color']}88);"></div>
                </div>
                <div style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 4px;">{result['cat_confidence']:.1%} confidence</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            urg_class = f"urgency-{urgency.lower()}"
            st.markdown(f"""
            <div class="metric-card animate-in" style="animation-delay: 0.1s;">
                <div class="metric-label">Urgency</div>
                <div style="margin-top: 12px;">
                    <span class="result-badge {urg_class}">{urgency}</span>
                </div>
                <div class="confidence-bar" style="margin-top: 16px;">
                    <div class="confidence-fill" style="width: {result['urg_confidence']*100}%; background: linear-gradient(90deg, #667eea, #764ba2);"></div>
                </div>
                <div style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 4px;">{result['urg_confidence']:.1%} confidence</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            conf_color = "#38ef7d" if confidence > 0.8 else "#ffd200" if confidence > 0.6 else "#ff416c"
            st.markdown(f"""
            <div class="metric-card animate-in" style="animation-delay: 0.2s;">
                <div class="metric-label">Overall Confidence</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: {conf_color}; margin-top: 8px;">
                    {confidence:.1%}
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence*100}%; background: linear-gradient(90deg, {conf_color}, {conf_color}88);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Routing suggestion
        st.markdown(f"""
        <div class="glass-panel animate-in" style="margin-top: 20px; animation-delay: 0.3s;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 2rem;">🔀</div>
                <div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Auto-Route To</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {routing['color']}; margin-top: 4px;">
                        {routing['team']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Smart Reply
        with st.expander("💬 View Suggested Reply", expanded=False):
            reply = REPLY_TEMPLATES.get(category, "Thank you for contacting us. We'll get back to you soon.")
            st.code(reply, language=None)
            st.button("📋 Copy Reply", key="copy_reply")

        # Go to Dashboard button — OUTSIDE classify_btn block so it works on click
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        col_go1, col_go2, col_go3 = st.columns([1, 2, 1])
        with col_go2:
            if st.button("📊 Go to Dashboard →", use_container_width=True, key="go_dashboard"):
                st.session_state.pop("last_result", None)
                st.session_state["_go_dashboard"] = True
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time overview of classified emails</div>', unsafe_allow_html=True)

    emails = st.session_state.classified_emails

    if not emails:
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 60px;">
            <div style="font-size: 4rem;">📭</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: rgba(255,255,255,0.6); margin-top: 16px;">
                No emails classified yet
            </div>
            <div style="color: rgba(255,255,255,0.3); margin-top: 8px;">
                Go to Analyze Email to classify your first email
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ─── KPI Cards ────────────────────────────────────────────────────────
    total = len(emails)
    high = sum(1 for e in emails if e["urgency"] == "High")
    medium = sum(1 for e in emails if e["urgency"] == "Medium")
    low = sum(1 for e in emails if e["urgency"] == "Low")
    avg_conf = sum(e["confidence"] for e in emails) / total if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_data = [
        (c1, "Total Emails", total, "#667eea"),
        (c2, "🔴 High Priority", high, "#ff416c"),
        (c3, "🟡 Medium Priority", medium, "#ffd200"),
        (c4, "🟢 Low Priority", low, "#38ef7d"),
        (c5, "Avg Confidence", f"{avg_conf:.1%}", "#764ba2"),
    ]
    for col, label, value, color in kpi_data:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="background: {color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ─── Charts ───────────────────────────────────────────────────────────
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    df = pd.DataFrame(emails)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 📂 Category Distribution")
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]

        color_map = {k: v["color"] for k, v in ROUTING_MAP.items()}
        colors = [color_map.get(c, "#888") for c in cat_counts["Category"]]

        fig = go.Figure(data=[go.Pie(
            labels=cat_counts["Category"],
            values=cat_counts["Count"],
            hole=0.5,
            marker=dict(colors=colors, line=dict(color="#1a1a2e", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color="white"),
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown("#### ⚡ Urgency Distribution")
        urg_counts = df["urgency"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0).reset_index()
        urg_counts.columns = ["Urgency", "Count"]

        urg_colors = {"High": "#ff416c", "Medium": "#ffd200", "Low": "#38ef7d"}
        colors = [urg_colors.get(u, "#888") for u in urg_counts["Urgency"]]

        fig = go.Figure(data=[go.Bar(
            x=urg_counts["Urgency"],
            y=urg_counts["Count"],
            marker=dict(
                color=colors,
                line=dict(width=0),
            ),
            text=urg_counts["Count"],
            textposition="outside",
            textfont=dict(color="white", size=14, family="Inter"),
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, visible=False),
            margin=dict(t=20, b=40, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ─── Filters ──────────────────────────────────────────────────────────
    st.markdown("#### 🔍 Filter & Search")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        filter_category = st.multiselect(
            "Category",
            options=df["category"].unique().tolist(),
            default=df["category"].unique().tolist(),
        )
    with filter_col2:
        filter_urgency = st.multiselect(
            "Urgency",
            options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
        )
    with filter_col3:
        search_text = st.text_input("🔎 Search", placeholder="Filter by keyword...")

    filtered = df[
        (df["category"].isin(filter_category)) &
        (df["urgency"].isin(filter_urgency))
    ]
    if search_text:
        mask = (
            filtered["subject"].str.contains(search_text, case=False, na=False) |
            filtered["content"].str.contains(search_text, case=False, na=False) |
            filtered["sender"].str.contains(search_text, case=False, na=False)
        )
        filtered = filtered[mask]

    # Sort: High first
    urgency_order = {"High": 0, "Medium": 1, "Low": 2}
    filtered = filtered.copy()
    filtered["_sort"] = filtered["urgency"].map(urgency_order)
    filtered = filtered.sort_values("_sort").drop(columns=["_sort"])

    # ─── Email Table ──────────────────────────────────────────────────────
    st.markdown(f"#### 📬 Classified Emails ({len(filtered)})")

    for _, row in filtered.iterrows():
        urg_class = f"urgency-{row['urgency'].lower()}"
        cat_key = row["category"].lower().split()[0]
        routing_color = ROUTING_MAP.get(row["category"], {}).get("color", "#888")

        st.markdown(f"""
        <div class="metric-card cat-{cat_key}" style="margin-bottom: 12px; padding: 18px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="result-badge {urg_class}" style="font-size: 0.75rem; padding: 4px 12px;">{row['urgency']}</span>
                        <span style="color: {routing_color}; font-weight: 600; font-size: 0.85rem;">{row['category']}</span>
                        <span style="color: rgba(255,255,255,0.3); font-size: 0.75rem;">#{row['id']}</span>
                    </div>
                    <div style="font-weight: 600; color: rgba(255,255,255,0.9); margin-top: 8px;">{row['subject']}</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-top: 4px;">
                        From: {row['sender']} • {row['timestamp']} • Confidence: {row['confidence']:.1%}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="routing-badge">{row['team']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Export ────────────────────────────────────────────────────────────
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    export_df = filtered[["id", "sender", "subject", "category", "urgency", "confidence", "team", "timestamp"]].copy()
    csv_data = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Export to CSV",
        data=csv_data,
        file_name="classified_emails.csv",
        mime="text/csv",
        use_container_width=True,
    )
