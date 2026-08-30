import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Online Test Portal",
    page_icon="📝",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (STYLING & DARK MODE OVERRIDES)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Question Card Box */
    .question-card {
        background-color: #FFFFFF !important;
        border: 2.5px solid #0D6EFD !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.08);
    }
    
    /* Question Title - Forced High Contrast */
    .question-title {
        color: #0F172A !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        line-height: 1.4 !important;
        margin: 8px 0 0 0 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Options Card Box */
    .options-card {
        background-color: #F8FAFC !important;
        border: 2px solid #64748B !important;
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Override Mobile / Dark Mode for Radio Options */
    div[data-testid="stRadio"] {
        background-color: transparent !important;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label div,
    div[data-testid="stRadio"] label span,
    div[data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        line-height: 1.5 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #0F172A !important;
        text-shadow: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #FFFFFF !important;
        padding: 10px;
        border-radius: 8px;
    }

    .question-card p, .question-card span, .question-card h3 {
        color: #0F172A !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Target ONLY Previous, Next, and Mark buttons via container wrapper */
    div[data-testid="column"] div.nav-btn-container button {
        width: 100% !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 4px !important;
        border-radius: 8px !important;
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    div[data-testid="column"] div.nav-btn-container button:hover {
        background-color: #115E59 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="column"] div.nav-btn-container button:disabled {
        background-color: #CBD5E1 !important;
        color: #64748B !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SAMPLE DATA (REPLACE WITH YOUR EXCEL / DATABASE LOADING LOGIC)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    return pd.DataFrame({
        "q_id": [101, 102, 103, 104, 105],
        "question": [
            "What is the capital of France?",
            "Which programming language is commonly used for Data Science?",
            "What is 15 multiplied by 6?",
            "Which database property guarantees that transactional changes survive system failures?",
            "What does SQL stand for?"
        ],
        "option_a": ["London", "Java", "80", "Atomicity", "Structured Query Language"],
        "option_b": ["Berlin", "Python", "90", "Consistency", "Sequential Query List"],
        "option_c": ["Paris", "C++", "100", "Isolation", "System Standard Language"],
        "option_d": ["Madrid", "HTML", "70", "Durability", "Simple Question Line"],
        "answer": ["Paris", "Python", "90", "Durability", "Structured Query Language"]
    })

df = load_data()
total_q = len(df)
curr_stage_name = "General Knowledge & Computer Science"

# -----------------------------------------------------------------------------
# 4. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "marked" not in st.session_state:
    st.session_state.marked = set()

def sync_url():
    st.query_params["q"] = str(st.session_state.current_q + 1)

# URL query sync check on load
if "q" in st.query_params:
    try:
        param_q = int(st.query_params["q"]) - 1
        if 0 <= param_q < total_q:
            st.session_state.current_q = param_q
    except ValueError:
        pass

curr_idx = st.session_state.current_q
row = df.iloc[curr_idx]
q_id = row["q_id"]

# -----------------------------------------------------------------------------
# 5. MAIN INTERFACE LAYOUT
# -----------------------------------------------------------------------------
col_main, col_palette = st.columns([3, 1])

with col_main:
    # --- 1. QUESTION CARD ---
    st.markdown(f"""
        <div class="question-card">
            <span style="color: #64748B; font-weight: 600; font-size: 14px;">Question {curr_idx + 1} of {total_q} (ID: {q_id})</span>
            <div class="question-title">{row['question']}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. OPTIONS CARD ---
    options = [row["option_a"], row["option_b"], row["option_c"], row["option_d"]]
    saved_answer = st.session_state.answers.get(q_id, None)
    
    saved_index = options.index(saved_answer) if saved_answer in options else None

    st.markdown('<div class="options-card">', unsafe_allow_html=True)
    selected_option = st.radio(
        label="Select your answer:",
        options=options,
        index=saved_index,
        key=f"radio_{q_id}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Save answer on selection
    if selected_option is not None:
        st.session_state.answers[q_id] = selected_option

    # --- 3. TARGETED NAVIGATION BUTTONS ---
    btn_prev, btn_mark, btn_next = st.columns(3)
    
    with btn_prev:
        st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
        if st.button("⬅️ Previous", disabled=(curr_idx == 0)):
            st.session_state.current_q = max(0, st.session_state.current_q - 1)
            sync_url()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with btn_mark:
        st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
        is_marked = q_id in st.session_state.marked
        mark_label = "🔖 Unmark" if is_marked else "📌 Mark for Review"
        if st.button(mark_label):
            if is_marked:
                st.session_state.marked.remove(q_id)
            else:
                st.session_state.marked.add(q_id)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with btn_next:
        st.markdown('<div class="nav-btn-container">', unsafe_allow_html=True)
        if st.button("Next ➡️", disabled=(curr_idx == total_q - 1)):
            st.session_state.current_q = min(total_q - 1, st.session_state.current_q + 1)
            sync_url()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # --- 4. COPY QUESTION BUTTON (DEFAULT STYLE UNCHANGED) ---
    copy_text = f"Subject: {curr_stage_name}\\nQuestion: {row['question']}\\nOptions:\\nA) {options[0]}\\nB) {options[1]}\\nC) {options[2]}\\nD) {options[3]}\\n\\nPlease explain the correct answer step-by-step."

    st.components.v1.html(
        f"""
        <button id="copyBtn" onclick="copyToClipboard()" style="
            width: 100%;
            background-color: #0D6EFD;
            color: white;
            border: none;
            padding: 12px 14px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        ">
            📋 Copy Question for AI Explanation
        </button>
        <script>
        function copyToClipboard() {{
            const textToCopy = `{copy_text}`;
            navigator.clipboard.writeText(textToCopy).then(function() {{
                const btn = document.getElementById('copyBtn');
                btn.innerText = '✅ Copied to Clipboard!';
                btn.style.backgroundColor = '#15803D';
                setTimeout(() => {{
                    btn.innerText = '📋 Copy Question for AI Explanation';
                    btn.style.backgroundColor = '#0D6EFD';
                }}, 2000);
            }}).catch(function(err) {{
                console.error('Copy failed: ', err);
            }});
        }}
        </script>
        """,
        height=55
    )

# -----------------------------------------------------------------------------
# 6. SIDEBAR / QUESTION PALETTE (DEFAULT STYLES UNCHANGED)
# -----------------------------------------------------------------------------
with col_palette:
    st.subheader("Question Palette")
    grid_cols = st.columns(4)
    for i in range(total_q):
        item_qid = df.iloc[i]["q_id"]
        is_current = (i == curr_idx)
        is_answered = item_qid in st.session_state.answers
        is_flagged = item_qid in st.session_state.marked

        btn_type = "primary" if is_current else "secondary"
        prefix = "📌 " if is_flagged else ("✅ " if is_answered else "")
        
        with grid_cols[i % 4]:
            if st.button(f"{prefix}{i+1}", key=f"pal_{i}", type=btn_type):
                st.session_state.current_q = i
                sync_url()
                st.rerun()

    st.write("---")
    if st.button("Submit Assessment", type="primary", use_container_width=True):
        st.success("Test Submitted Successfully!")
