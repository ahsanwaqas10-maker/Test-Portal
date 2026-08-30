import streamlit as st
import pandas as pd
import time
import os

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# --- CONFIGURATION ---
PORTAL_PIN = "1234"
DEFAULT_TEST_MINUTES = 15     # Time limit per test section
PASSING_PERCENTAGE = 85       # Combined overall passing score

STAGE_SEQUENCE = ["Verbal", "Non-Verbal", "English", "General Science", "Math", "Urdu"]

st.set_page_config(page_title="Exam Portal", layout="wide")

# Live 1-second timer auto-refresh (Prevents UI lock/freeze)
if st_autorefresh:
    st_autorefresh(interval=1000, key="exam_timer_tick")

# --- CACHE EXCEL FILE ---
@st.cache_data
def load_questions():
    df = pd.read_excel("questions.xlsx")
    df.columns = df.columns.astype(str).str.strip()
    return df

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .question-card {
        background-color: #F8F9FA;
        border: 2px solid #0D6EFD;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.08);
    }
    
    .question-title {
        color: #1E293B;
        font-size: 22px;
        font-weight: 700;
        margin: 0 0 5px 0;
    }

    .options-card {
        background-color: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.04);
    }

    .stButton>button {
        width: 100%;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
    }

    div[data-testid="column"] .stButton>button {
        padding: 6px 2px !important;
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Exam Portal")

# --- PERSISTENCE HELPERS (URL PARAMETERS) ---
query_params = st.query_params

if "authenticated" not in st.session_state:
    st.session_state.authenticated = query_params.get("auth", "0") == "1"
if "student_name" not in st.session_state:
    st.session_state.student_name = query_params.get("name", "")
if "stage_index" not in st.session_state:
    st.session_state.stage_index = int(query_params.get("stage", "0"))
if "current_q" not in st.session_state:
    st.session_state.current_q = int(query_params.get("q", "0"))
if "start_time" not in st.session_state:
    st.session_state.start_time = float(query_params.get("t", "0")) if query_params.get("t", "0") != "0" else time.time()
if "all_answers" not in st.session_state:
    st.session_state.all_answers = {}
if "marked" not in st.session_state:
    st.session_state.marked = set()
if "submitted_all" not in st.session_state:
    st.session_state.submitted_all = query_params.get("done", "0") == "1"

def sync_url():
    st.query_params.update({
        "auth": "1" if st.session_state.authenticated else "0",
        "name": st.session_state.student_name,
        "stage": str(st.session_state.stage_index),
        "q": str(st.session_state.current_q),
        "t": str(st.session_state.start_time),
        "done": "1" if st.session_state.submitted_all else "0"
    })

# --- STAGE 1: LOGIN ENTRY FORM ---
if not st.session_state.authenticated:
    st.subheader("Student Portal Login")
    
    with st.form("login_form"):
        name_input = st.text_input("Student Name:", placeholder="Enter your full name")
        pin_input = st.text_input("Password / PIN:", type="password", placeholder="Enter test password")
        submit_login = st.form_submit_button("Start Exam Series", type="primary")

        if submit_login:
            if not name_input.strip():
                st.error("Please enter your name to proceed.")
            elif pin_input != PORTAL_PIN:
                st.error("Incorrect password. Please verify your passcode.")
            else:
                st.session_state.authenticated = True
                st.session_state.student_name = name_input.strip()
                st.session_state.stage_index = 0
                st.session_state.current_q = 0
                st.session_state.start_time = time.time()
                sync_url()
                st.rerun()

# --- STAGE 2: MULTI-SERIES EXAM INTERFACE ---
elif not st.session_state.submitted_all:
    try:
        df_full = load_questions()
        if df_full.empty:
            st.error("The question database is empty.")
            st.stop()

        cols = {c.lower().replace(" ", ""): c for c in df_full.columns}
        id_col = cols.get('id', df_full.columns[0])
        subject_col = cols.get('subject', df_full.columns[1])
        question_col = cols.get('question', df_full.columns[2])
        op_a = cols.get('optiona', df_full.columns[3])
        op_b = cols.get('optionb', df_full.columns[4])
        op_c = cols.get('optionc', df_full.columns[5])
        op_d = cols.get('optiond', df_full.columns[6])
        ans_col = cols.get('correctanswer', df_full.columns[7])
        img_col = cols.get('image', None)

        curr_stage_name = STAGE_SEQUENCE[st.session_state.stage_index]
        df_stage = df_full[df_full[subject_col].astype(str).str.strip().str.lower() == curr_stage_name.lower()].reset_index(drop=True)

        if df_stage.empty:
            if st.session_state.stage_index < len(STAGE_SEQUENCE) - 1:
                st.session_state.stage_index += 1
                st.session_state.current_q = 0
                st.session_state.start_time = time.time()
                sync_url()
                st.rerun()
            else:
                st.session_state.submitted_all = True
                sync_url()
                st.rerun()

        total_q = len(df_stage)

        if st.session_state.current_q >= total_q:
            st.session_state.current_q = max(0, total_q - 1)

        # Section Timer Calculations
        total_seconds = DEFAULT_TEST_MINUTES * 60
        elapsed_seconds = int(time.time() - st.session_state.start_time)
        remaining_seconds = total_seconds - elapsed_seconds

        if remaining_seconds <= 0:
            st.warning(f"⏰ Time expired for section: {curr_stage_name}!")
            time.sleep(1)
            if st.session_state.stage_index < len(STAGE_SEQUENCE) - 1:
                st.session_state.stage_index += 1
                st.session_state.current_q = 0
                st.session_state.marked = set()
                st.session_state.start_time = time.time()
            else:
                st.session_state.submitted_all = True
            sync_url()
            st.rerun()

        mins, secs = divmod(max(0, remaining_seconds), 60)

        # Header Details
        st.info(f"📌 **Section {st.session_state.stage_index + 1} of {len(STAGE_SEQUENCE)}:** {curr_stage_name} Test | Candidate: **{st.session_state.student_name}**")
        
        col_main, col_nav = st.columns([3, 1], gap="large")

        curr_idx = st.session_state.current_q
        row = df_stage.iloc[curr_idx]
        q_id = row[id_col]

        with col_main:
            # Question Box
            st.markdown(f"""
                <div class="question-card">
                    <span style="color: #2563EB; font-weight: bold; font-size: 14px;">QUESTION {curr_idx + 1} OF {total_q}</span>
                    <h3 class="question-title">{row[question_col]}</h3>
                </div>
            """, unsafe_allow_html=True)

            # Image Rendering
            if img_col and pd.notna(row[img_col]):
                img_name = str(row[img_col]).strip()
                if img_name and os.path.exists(img_name):
                    st.image(img_name, use_container_width=True)

            # Options Box
            options = [
                str(row[op_a]).strip(),
                str(row[op_b]).strip(),
                str(row[op_c]).strip(),
                str(row[op_d]).strip()
            ]

            saved_ans = st.session_state.all_answers.get(q_id, None)
            saved_index = options.index(saved_ans) if saved_ans in options else None

            st.markdown('<div class="options-card">', unsafe_allow_html=True)
            user_choice = st.radio(
                "Select Answer Choice:", 
                options, 
                index=saved_index, 
                key=f"radio_{q_id}_{curr_idx}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if user_choice:
                st.session_state.all_answers[q_id] = user_choice

            # Navigation Control Buttons
            btn_prev, btn_mark, btn_next = st.columns(3)

            with btn_prev:
                # Disabled only if on the first question AND there are multiple questions
                if st.button("⬅️ Previous", disabled=(curr_idx == 0)):
                    st.session_state.current_q = max(0, st.session_state.current_q - 1)
                    sync_url()
                    st.rerun()

            with btn_mark:
                is_marked = q_id in st.session_state.marked
                mark_label = "🔖 Unmark" if is_marked else "📌 Mark for Review"
                if st.button(mark_label):
                    if is_marked:
                        st.session_state.marked.remove(q_id)
                    else:
                        st.session_state.marked.add(q_id)
                    st.rerun()

            with btn_next:
                # Disabled only if on the last question of the section
                if st.button("Next ➡️", disabled=(curr_idx == total_q - 1)):
                    st.session_state.current_q = min(total_q - 1, st.session_state.current_q + 1)
                    sync_url()
                    st.rerun()

        # RIGHT-HAND PANEL
        with col_nav:
            st.metric("⏳ Section Timer", f"{mins:02d}:{secs:02d}")
            st.divider()

            answered_cnt = sum(1 for qid in df_stage[id_col] if qid in st.session_state.all_answers)
            marked_cnt = len([qid for qid in df_stage[id_col] if qid in st.session_state.marked])
            unanswered_cnt = total_q - answered_cnt

            st.markdown("**Overview:**")
            st.caption(f"🟢 Answered: **{answered_cnt}** | 🟡 Marked: **{marked_cnt}** | ⚪ Remaining: **{unanswered_cnt}**")

            st.markdown("**Question Palette:**")
            
            grid_cols = st.columns(5)
            for idx in range(total_q):
                qid = df_stage.iloc[idx][id_col]
                
                if qid in st.session_state.marked:
                    badge = f"🟡{idx+1}"
                elif qid in st.session_state.all_answers:
                    badge = f"🟢{idx+1}"
                else:
                    badge = f"{idx+1}"

                col_idx = idx % 5
                with grid_cols[col_idx]:
                    if st.button(badge, key=f"nav_btn_{idx}"):
                        st.session_state.current_q = idx
                        sync_url()
                        st.rerun()

            st.write("---")
            
            if st.session_state.stage_index < len(STAGE_SEQUENCE) - 1:
                next_stage = STAGE_SEQUENCE[st.session_state.stage_index + 1]
                submit_label = f"Submit & Next ({next_stage}) ➡️"
            else:
                submit_label = "🚨 Finish Complete Exam"

            if st.button(submit_label, type="primary"):
                st.session_state.confirm_submit = True

        if st.session_state.get("confirm_submit", False):
            st.warning(f"⚠️ **CONFIRM SUBMISSION FOR {curr_stage_name.upper()} TEST**")
            st.write(f"* **Answered:** {answered_cnt} / {total_q}")
            st.write(f"* **Unanswered:** {unanswered_cnt}")

            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("✅ Confirm & Proceed", type="primary"):
                    st.session_state.confirm_submit = False
                    if st.session_state.stage_index < len(STAGE_SEQUENCE) - 1:
                        st.session_state.stage_index += 1
                        st.session_state.current_q = 0
                        st.session_state.marked = set()
                        st.session_state.start_time = time.time()
                    else:
                        st.session_state.submitted_all = True
                    sync_url()
                    st.rerun()
            with c_no:
                if st.button("❌ Back to Test"):
                    st.session_state.confirm_submit = False
                    st.rerun()

    except Exception as e:
        st.error(f"System Error: {e}")

# --- STAGE 3: COMPREHENSIVE SCORECARD ---
else:
    st.header("📊 Final Combined Scorecard")
    st.markdown(f"**Student Name:** {st.session_state.student_name}")

    try:
        df_full = load_questions()
        cols = {c.lower().replace(" ", ""): c for c in df_full.columns}
        id_col = cols.get('id', df_full.columns[0])
        subject_col = cols.get('subject', df_full.columns[1])
        ans_col = cols.get('correctanswer', df_full.columns[7])

        total_questions_all = len(df_full)
        overall_score = 0

        st.subheader("Sectional Breakdown:")
        
        for subject_name in STAGE_SEQUENCE:
            df_sub = df_full[df_full[subject_col].astype(str).str.strip().str.lower() == subject_name.lower()]
            if not df_sub.empty:
                sub_score = 0
                sub_total = len(df_sub)
                for idx, row in df_sub.iterrows():
                    qid = row[id_col]
                    u_ans = str(st.session_state.all_answers.get(qid, "")).strip()
                    c_ans = str(row[ans_col]).strip()
                    if u_ans == c_ans:
                        sub_score += 1
                
                overall_score += sub_score
                sub_pct = (sub_score / sub_total) * 100
                st.write(f"* **{subject_name}:** {sub_score} / {sub_total} ({sub_pct:.1f}%)")

        st.divider()
        final_pct = (overall_score / total_questions_all) * 100 if total_questions_all > 0 else 0
        st.metric("Total Score", f"{overall_score} / {total_questions_all}", f"{final_pct:.1f}%")

        if final_pct >= PASSING_PERCENTAGE:
            st.balloons()
            st.success(f"🎉 Exam Series Passed! Overall Score: {final_pct:.1f}% (Required: {PASSING_PERCENTAGE}%)")
        else:
            st.warning(f"❌ Exam Series Failed. Overall Score: {final_pct:.1f}% (Required: {PASSING_PERCENTAGE}%)")

        if st.button("🔄 Logout & Exit", type="primary"):
            st.query_params.clear()
            st.session_state.authenticated = False
            st.session_state.student_name = ""
            st.session_state.stage_index = 0
            st.session_state.current_q = 0
            st.session_state.all_answers = {}
            st.session_state.marked = set()
            st.session_state.submitted_all = False
            st.rerun()

    except Exception as e:
        st.error(f"Error calculating final scores: {e}")
