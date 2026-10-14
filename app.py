import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="EduMetrics Pro | Student Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- LOAD & CACHE DATA ----------------

@st.cache_data
def load_data():
    df = pd.read_csv("Student Performance new.csv")
    
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    
    # Scale decimal values (0.72) to percentage format (72.0)
    df["math_pct"] = (df["math percentage"] * 100).round(1)
    df["reading_pct"] = (df["reading score percentage"] * 100).round(1)
    df["writing_pct"] = (df["writing score percentage"] * 100).round(1)
    
    # Calculate overall average percentage
    df["overall_pct"] = ((df["math_pct"] + df["reading_pct"] + df["writing_pct"]) / 3).round(1)
    
    # Passing rule: at least 33% marks in all three subjects
    df["passed"] = (df["math_pct"] >= 33) & (df["reading_pct"] >= 33) & (df["writing_pct"] >= 33)
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ `Student Performance new.csv` was not found. Please place it in the same directory as `app.py`.")
    st.stop()

# ---------------- SESSION STATE FOR NAVIGATION & FILTERS ----------------

if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview Dashboard"

# Active Filter Selections (Saved as sets for fast toggle)
if "sel_gender" not in st.session_state:
    st.session_state.sel_gender = set(df["sex"].unique())
if "sel_group" not in st.session_state:
    st.session_state.sel_group = set(df["race/ethnicity"].unique())
if "sel_prep" not in st.session_state:
    st.session_state.sel_prep = set(df["test preparation course"].unique())
if "sel_edu" not in st.session_state:
    st.session_state.sel_edu = set(df["parental level of education"].unique())
if "sel_lunch" not in st.session_state:
    st.session_state.sel_lunch = set(df["lunch"].unique())
if "score_range" not in st.session_state:
    st.session_state.score_range = (0, 100)

def reset_all_filters():
    st.session_state.sel_gender = set(df["sex"].unique())
    st.session_state.sel_group = set(df["race/ethnicity"].unique())
    st.session_state.sel_prep = set(df["test preparation course"].unique())
    st.session_state.sel_edu = set(df["parental level of education"].unique())
    st.session_state.sel_lunch = set(df["lunch"].unique())
    st.session_state.score_range = (0, 100)

def set_page(page_name):
    st.session_state.current_page = page_name

def toggle_filter(filter_set_key, value):
    current_set = st.session_state[filter_set_key]
    if value in current_set:
        if len(current_set) > 1:  # Keep at least one selected so it doesn't vanish
            current_set.remove(value)
    else:
        current_set.add(value)

def select_all_filter(filter_set_key, all_values):
    st.session_state[filter_set_key] = set(all_values)

# ---------------- DUAL-MODE (LIGHT & DARK) ADAPTIVE STYLING ----------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 95%;
    }

    /* Distinct Sidebar divider that works in both themes */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.22) !important;
        padding-top: 0.8rem;
    }

    /* App Brand Header */
    .app-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 4px 14px 4px;
        margin-bottom: 6px;
    }
    .brand-icon {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
    }
    .brand-title {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: var(--text-color);
        line-height: 1.2;
    }

    /* Search Mockup Pill */
    .search-mockup {
        background: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 20px;
        padding: 8px 14px;
        font-size: 0.82rem;
        color: rgba(128, 128, 128, 0.9);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 14px;
    }

    /* ---------------- DUAL-MODE BUTTONS (NAV + FILTERS) ---------------- */
    [data-testid="stSidebar"] div.stButton {
        margin-bottom: -5px !important;
    }

    /* INACTIVE BUTTONS: Semi-transparent background, clear text in both light and dark */
    [data-testid="stSidebar"] div.stButton > button {
        background: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.16) !important;
        color: var(--text-color) !important;
        opacity: 0.85;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        text-align: left !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        box-shadow: none !important;
        transition: all 0.16s ease-in-out !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(59, 130, 246, 0.14) !important;
        border-color: rgba(59, 130, 246, 0.45) !important;
        opacity: 1;
        transform: translateX(2px) !important;
    }

    /* ACTIVE BUTTONS: Glowing blue tint, high contrast border, clear active text in both modes */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: rgba(59, 130, 246, 0.18) !important;
        border: 1.5px solid #3b82f6 !important;
        border-left: 4px solid #3b82f6 !important;
        color: var(--text-color) !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.22) !important;
        transform: none !important;
    }

    /* Section Subheaders */
    .filter-section-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: rgba(128, 128, 128, 0.95);
        margin: 12px 0 6px 0;
    }

    /* METRIC STAT BOXES */
    .stat-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-box:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .stat-title {
        color: rgba(128, 128, 128, 0.95);
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .stat-number {
        color: var(--text-color);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .stat-sub {
        color: rgba(128, 128, 128, 0.85);
        font-size: 0.8rem;
        margin-top: 6px;
    }

    /* HIGHLIGHT CARDS */
    .info-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 15px 18px;
        margin-bottom: 12px;
    }

    /* COHORT SCOPE BADGE */
    .cohort-pill {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.35);
        color: var(--text-color);
        padding: 8px 12px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 700;
        text-align: center;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- CHART STYLE HELPER ----------------

def style_chart(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.18)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.18)", zeroline=False),
    )
    return fig

# ---------------- SIDEBAR (NAV + PILL BUTTON FILTERS) ----------------

with st.sidebar:
    # 1. Brand Header
    st.markdown("""
    <div class="app-brand">
        <div class="brand-icon">🎓</div>
        <div class="brand-title">EduMetrics Pro</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Main Navigation Buttons
    pages = [
        ("📊  Overview Dashboard", "Overview Dashboard"),
        ("📚  Subject Comparisons", "Subject Comparisons"),
        ("🏫  Parent Education & Prep", "Parent Education & Prep"),
        ("🔮  Score Estimator", "Score Estimator"),
        ("🔍  Student Records & Table", "Student Records & Table"),
        ("📖  About Dataset & Project", "About Dataset & Project"),
    ]

    for label, target_page in pages:
        is_active = (st.session_state.current_page == target_page)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{target_page}", type=btn_type, use_container_width=True):
            set_page(target_page)
            st.rerun()

    page = st.session_state.current_page

    st.markdown("<hr style='margin: 16px 0 10px 0; opacity: 0.18;'>", unsafe_allow_html=True)

    # 3. FILTER SECTION USING PILL BUTTONS
    st.markdown("<p style='font-size:0.78rem; font-weight:800; text-transform:uppercase; color:rgba(128,128,128,0.9); margin-bottom:4px;'>Filters</p>", unsafe_allow_html=True)

    # Gender Filter Buttons
    st.markdown('<div class="filter-section-title">Gender</div>', unsafe_allow_html=True)
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        f_active = "F" in st.session_state.sel_gender
        if st.button("Female (F)", key="btn_g_f", type="primary" if f_active else "secondary", use_container_width=True):
            toggle_filter("sel_gender", "F")
            st.rerun()
    with g_col2:
        m_active = "M" in st.session_state.sel_gender
        if st.button("Male (M)", key="btn_g_m", type="primary" if m_active else "secondary", use_container_width=True):
            toggle_filter("sel_gender", "M")
            st.rerun()

    # Prep Course Filter Buttons
    st.markdown('<div class="filter-section-title">Test Prep Course</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        comp_active = "completed" in st.session_state.sel_prep
        if st.button("Completed", key="btn_prep_comp", type="primary" if comp_active else "secondary", use_container_width=True):
            toggle_filter("sel_prep", "completed")
            st.rerun()
    with p_col2:
        none_active = "none" in st.session_state.sel_prep
        if st.button("None", key="btn_prep_none", type="primary" if none_active else "secondary", use_container_width=True):
            toggle_filter("sel_prep", "none")
            st.rerun()

    # Student Group Filter Buttons
    st.markdown('<div class="filter-section-title">Student Groups</div>', unsafe_allow_html=True)
    all_groups = sorted(df["race/ethnicity"].unique())
    all_selected = (len(st.session_state.sel_group) == len(all_groups))

    if st.button("Select All Groups", key="btn_grp_all", type="primary" if all_selected else "secondary", use_container_width=True):
        select_all_filter("sel_group", all_groups)
        st.rerun()

    cols = st.columns(2)
    for idx, grp in enumerate(all_groups):
        with cols[idx % 2]:
            grp_active = grp in st.session_state.sel_group
            if st.button(grp, key=f"btn_grp_{grp}", type="primary" if grp_active else "secondary", use_container_width=True):
                toggle_filter("sel_group", grp)
                st.rerun()

    # Overall Score Range Slider
    st.markdown('<div class="filter-section-title">Overall Score Range (%)</div>', unsafe_allow_html=True)
    score_range = st.slider(
        "Score Range",
        0, 100,
        value=st.session_state.score_range,
        label_visibility="collapsed"
    )
    st.session_state.score_range = score_range

    # More Filters (Parent Education & Lunch)
    with st.expander("More Filters"):
        st.markdown('<div class="filter-section-title">Lunch Type</div>', unsafe_allow_html=True)
        l_c1, l_c2 = st.columns(2)
        with l_c1:
            std_active = "standard" in st.session_state.sel_lunch
            if st.button("Standard", key="btn_l_std", type="primary" if std_active else "secondary", use_container_width=True):
                toggle_filter("sel_lunch", "standard")
                st.rerun()
        with l_c2:
            free_active = "free/reduced" in st.session_state.sel_lunch
            if st.button("Free/Reduced", key="btn_l_free", type="primary" if free_active else "secondary", use_container_width=True):
                toggle_filter("sel_lunch", "free/reduced")
                st.rerun()

        st.markdown('<div class="filter-section-title">Parent Education</div>', unsafe_allow_html=True)
        all_edu = sorted(df["parental level of education"].unique())
        for edu in all_edu:
            edu_active = edu in st.session_state.sel_edu
            if st.button(edu, key=f"btn_edu_{edu}", type="primary" if edu_active else "secondary", use_container_width=True):
                toggle_filter("sel_edu", edu)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ Reset All Filters", key="reset_filters_btn", use_container_width=True):
        reset_all_filters()
        st.rerun()

# ---------------- APPLY FILTERS ----------------

filtered = df[
    df["sex"].isin(st.session_state.sel_gender) &
    df["race/ethnicity"].isin(st.session_state.sel_group) &
    df["test preparation course"].isin(st.session_state.sel_prep) &
    df["parental level of education"].isin(st.session_state.sel_edu) &
    df["lunch"].isin(st.session_state.sel_lunch) &
    df["overall_pct"].between(st.session_state.score_range[0], st.session_state.score_range[1])
].copy()

# Live Cohort Scope Badge
st.sidebar.markdown(
    f"""
    <div class="cohort-pill">
        ✓ {len(filtered):,} of {len(df):,} Students Selected ({len(filtered)/len(df)*100:.0f}%)
    </div>
    """,
    unsafe_allow_html=True
)

def check_filtered_data():
    if filtered.empty:
        st.warning("⚠️ No student records match these filters. Select at least one option in the sidebar or click **'↺ Reset All Filters'**.")
        st.stop()

# ---------------- 1. OVERVIEW DASHBOARD ----------------

if page == "Overview Dashboard":
    check_filtered_data()

    st.markdown("## Overview Dashboard")
    st.caption("Overall student performance, pass rates, and score distributions.")

    c1, c2, c3, c4 = st.columns(4)

    overall_avg = filtered["overall_pct"].mean()
    pass_pct = filtered["passed"].mean() * 100
    distinction_pct = (filtered["overall_pct"] >= 75).mean() * 100
    math_avg = filtered["math_pct"].mean()

    with c1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">Selected Students</div>
            <div class="stat-number">{len(filtered):,}</div>
            <div class="stat-sub">{len(filtered)/len(df)*100:.1f}% of total dataset</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">Overall Average</div>
            <div class="stat-number">{overall_avg:.1f}%</div>
            <div class="stat-sub">Across Math, Reading, Writing</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">Pass Rate (≥33%)</div>
            <div class="stat-number">{pass_pct:.1f}%</div>
            <div class="stat-sub">{distinction_pct:.1f}% scored ≥ 75% (Distinction)</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-title">Math Average</div>
            <div class="stat-number">{math_avg:.1f}%</div>
            <div class="stat-sub">Max: {filtered['math_pct'].max():.0f}% | Min: {filtered['math_pct'].min():.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Overall Score Distribution")
        fig_dist = px.histogram(
            filtered,
            x="overall_pct",
            nbins=20,
            color_discrete_sequence=["#3b82f6"],
            labels={"overall_pct": "Overall Percentage (%)", "count": "Student Count"}
        )
        fig_dist.add_vline(x=33, line_dash="dash", line_color="#ef4444", annotation_text="Pass Cutoff (33%)")
        fig_dist.add_vline(x=75, line_dash="dot", line_color="#10b981", annotation_text="Distinction (75%)")
        st.plotly_chart(style_chart(fig_dist), use_container_width=True)

    with col2:
        st.subheader("Performance by Student Group")
        group_perf = filtered.groupby("race/ethnicity", as_index=False)["overall_pct"].mean().sort_values(by="overall_pct", ascending=False)
        fig_group = px.bar(
            group_perf,
            x="race/ethnicity",
            y="overall_pct",
            text_auto=".1f",
            color="race/ethnicity",
            color_discrete_sequence=["#3b82f6", "#8b5cf6", "#06b6d4", "#ec4899", "#f59e0b"],
            labels={"race/ethnicity": "Group", "overall_pct": "Mean Score (%)"}
        )
        fig_group.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig_group), use_container_width=True)

# ---------------- 2. SUBJECT COMPARISONS ----------------

elif page == "Subject Comparisons":
    check_filtered_data()

    st.markdown("## Subject Performance Breakdown")
    st.caption("Comparing scores between Mathematics, Reading, and Writing.")

    c_left, c_right = st.columns([1.8, 1.2])

    with c_left:
        sub_means = pd.DataFrame({
            "Subject": ["Mathematics", "Reading", "Writing"],
            "Average Score (%)": [
                filtered["math_pct"].mean(),
                filtered["reading_pct"].mean(),
                filtered["writing_pct"].mean()
            ]
        })

        fig_sub = px.bar(
            sub_means,
            x="Subject",
            y="Average Score (%)",
            text_auto=".1f",
            color="Subject",
            color_discrete_sequence=["#3b82f6", "#06b6d4", "#8b5cf6"],
            title="Subject-Wise Mean Performance"
        )
        fig_sub.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig_sub, height=380), use_container_width=True)

    with c_right:
        st.markdown("<h4 style='font-size:1rem; margin-top:20px;'>Subject Insights</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <b>Reading & Writing Connection</b><br>
            Students who score high marks in reading almost always get high marks in writing as well.
        </div>
        <div class="info-card">
            <b>Math Marks Variance</b><br>
            Math has the biggest difference between high and low scorers compared to reading and writing.
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Reading vs Writing Correlation")
    fig_scatter = px.scatter(
        filtered,
        x="reading_pct",
        y="writing_pct",
        color="test preparation course",
        hover_data=["sex", "math_pct"],
        labels={
            "reading_pct": "Reading Score (%)",
            "writing_pct": "Writing Score (%)",
            "test preparation course": "Prep Course"
        },
        color_discrete_sequence=["#3b82f6", "#10b981"]
    )
    st.plotly_chart(style_chart(fig_scatter, height=380), use_container_width=True)

# ---------------- 3. PARENT EDUCATION & PREP ----------------

elif page == "Parent Education & Prep":
    check_filtered_data()

    st.markdown("## Parental Education & Test Prep Impact")
    st.caption("How parents' education level and test prep courses affect student marks.")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.subheader("Parent Education Level vs Overall Score")
        edu_order = ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"]
        edu_summary = filtered.groupby("parental level of education", as_index=False)["overall_pct"].mean()
        
        fig_edu = px.bar(
            edu_summary,
            x="parental level of education",
            y="overall_pct",
            text_auto=".1f",
            color="overall_pct",
            category_orders={"parental level of education": edu_order},
            color_continuous_scale="Blues",
            labels={"parental level of education": "Parent Education Level", "overall_pct": "Mean Score (%)"}
        )
        fig_edu.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_chart(fig_edu), use_container_width=True)

    with col_p2:
        st.subheader("Impact of Test Preparation Course")
        fig_prep = px.box(
            filtered,
            x="test preparation course",
            y="overall_pct",
            color="test preparation course",
            color_discrete_sequence=["#ef4444", "#10b981"],
            labels={"test preparation course": "Course Status", "overall_pct": "Overall Score (%)"}
        )
        fig_prep.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig_prep), use_container_width=True)

# ---------------- 4. SCORE ESTIMATOR ----------------

elif page == "Score Estimator":
    st.markdown("## Score Estimator & Simulator")
    st.caption("Estimate a student's final percentage using background indicators.")

    pred_c1, pred_c2 = st.columns([1.1, 1.2])

    with pred_c1:
        p_math = st.slider("Target Math Score (%)", 0, 100, 65)
        p_prep = st.radio("Completed Test Preparation Course?", ["completed", "none"], horizontal=True)
        p_lunch = st.radio("Lunch Program Type", ["standard", "free/reduced"], horizontal=True)
        p_edu = st.selectbox(
            "Parent Level of Education",
            ["some high school", "high school", "some college", "associate's degree", "bachelor's degree", "master's degree"],
            index=2
        )

    with pred_c2:
        prep_boost = 7.5 if p_prep == "completed" else 0.0
        lunch_boost = 6.0 if p_lunch == "standard" else 0.0
        
        edu_weights = {
            "some high school": 0.0,
            "high school": 1.5,
            "some college": 3.0,
            "associate's degree": 4.5,
            "bachelor's degree": 6.5,
            "master's degree": 8.0
        }
        
        predicted_overall = (0.60 * p_math) + prep_boost + lunch_boost + edu_weights[p_edu] + 12.0
        predicted_overall = float(np.clip(predicted_overall, 0.0, 100.0))

        if predicted_overall >= 75:
            color = "#10b981"
            badge = "DISTINCTION / HIGH ACHIEVER (≥ 75%)"
        elif predicted_overall >= 60:
            color = "#3b82f6"
            badge = "FIRST DIVISION (60% - 74%)"
        elif predicted_overall >= 33:
            color = "#f59e0b"
            badge = "PASSING (33% - 59%)"
        else:
            color = "#ef4444"
            badge = "REMEDIAL SUPPORT RECOMMENDED (< 33%)"

        st.markdown(f"""
        <div style="background:var(--secondary-background-color); border:2px solid {color}; border-radius:14px; padding:28px; text-align:center;">
            <div style="color:{color}; font-weight:700; font-size:0.85rem; letter-spacing:0.05em;">
                {badge}
            </div>
            <div style="font-size:3.2rem; font-weight:800; color:var(--text-color); margin:8px 0;">
                {predicted_overall:.1f}%
            </div>
            <p style="opacity:0.8; font-size:0.85rem; margin:0 auto; max-width:320px;">
                Modeled from math benchmark, test prep completion, and socio-educational parameters.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- 5. STUDENT RECORDS & TABLE ----------------

elif page == "Student Records & Table":
    check_filtered_data()

    st.markdown("## Student Records Ledger")
    st.caption("Inspect individual student records and download the table to CSV.")

    search_text = st.text_input("Search student profiles", placeholder="Search by gender, group, or parent education...")

    view_df = filtered[[
        "sex", "race/ethnicity", "parental level of education", 
        "lunch", "test preparation course", "math_pct", 
        "reading_pct", "writing_pct", "overall_pct"
    ]].copy()

    view_df.columns = [
        "Gender", "Group", "Parent Education", "Lunch", 
        "Test Prep", "Math (%)", "Reading (%)", "Writing (%)", "Overall (%)"
    ]

    if search_text:
        mask = view_df.astype(str).apply(
            lambda col: col.str.contains(search_text, case=False, na=False, regex=False)
        ).any(axis=1)
        view_df = view_df[mask]

    st.write(f"Showing **{len(view_df):,}** matching student records")
    st.dataframe(view_df, use_container_width=True, height=450)

    st.download_button(
        "📥 Download Table as CSV",
        data=view_df.to_csv(index=False).encode("utf-8"),
        file_name="student_performance_filtered.csv",
        mime="text/csv"
    )

# ---------------- 6. ABOUT DATASET & PROJECT ----------------

elif page == "About Dataset & Project":
    st.markdown("## 📖 About This Project")

    st.markdown("""
    ### 1. What is this project?
    This is a **Student Performance Analysis Project** created for college evaluation. It helps teachers, students, and parents understand how different factors like self-study, test prep courses, and parents' education level affect student marks in school exams.

    ---

    ### 2. Where did the data come from?
    - The dataset used in this project was downloaded directly from **[Kaggle](https://www.kaggle.com/)** (`Student Performance new.csv`).
    - Kaggle is a globally trusted public platform for data science and machine learning datasets.
    - The dataset contains information on **1,000 students**.

    ---

    ### 3. What information is inside the dataset?
    Each student profile contains the following details:
    - **Gender (`sex`):** Male (M) or Female (F).
    - **Student Group (`race/ethnicity`):** Student groups labeled from Group A to Group E.
    - **Parent Education:** The highest qualification completed by the student's parents (such as High School, Bachelor's Degree, or Master's Degree).
    - **Lunch:** The meal plan of the student (Standard or Free/Reduced).
    - **Test Preparation Course:** Whether the student completed an exam prep course (`completed` or `none`).
    - **Scores:** Marks obtained in **Math**, **Reading**, and **Writing** (converted from decimal to 0–100%).

    ---

    ### 4. Passing and Grading Rules Used
    To keep the analysis simple and clear, the standard school grading system is used:
    - **75% and above:** **Distinction** (Top Achievers)
    - **60% to 74%:** **First Division** (Good Performance)
    - **33% to 59%:** **Passing Grade** (Average Performance)
    - **Below 33%:** **Needs Help / Fail Cutoff** (Extra Tutoring Recommended)

    ---

    ### 5. Technologies Used
    - **Python:** For data cleaning and score calculations.
    - **Streamlit:** For building this web dashboard interface.
    - **Pandas:** For loading and filtering the CSV dataset.
    - **Plotly:** For generating interactive charts and graphs.
    """)

# ---------------- FOOTER ----------------

st.markdown("<hr style='opacity: 0.18; margin-top: 30px;'>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; opacity: 0.65; font-size: 0.8rem;'>"
    "EduMetrics Pro • BCA Minor Project Evaluation • Academic Analytics"
    "</div>",
    unsafe_allow_html=True
)