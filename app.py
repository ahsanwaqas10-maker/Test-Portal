import streamlit as st
import pandas as pd
import time

# --- CONFIGURATION & PASSWORD ---
# Change this password whenever you want to issue a new test key
PORTAL_PIN = "1234"
DEFAULT_TEST_MINUTES = 15

st.set_page_config(page_title="Exam Portal", layout="wide")

def load_questions():
    df = pd.read_excel("questions.xlsx")
    df.columns = df.columns.astype(str).str.strip()
    return df

st.title("📝 Exam Portal")

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "marked" not in st.session_state:
    st.session_state.marked = set()
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- WINDOW 1: LOGIN ENTRY FORM ---
if not st.session_state.authenticated:
    st.subheader("Student Portal Login")
    
    with st.form("login_form"):
        name_input = st.text_input("Student Name:", placeholder="Enter your full name")
        pin_input = st.text_input("Password / PIN:", type="password", placeholder="Enter test password")
        submit_login = st.form_submit_button("Start Exam")

        if submit_login:
            if not name_input.strip():
                st.error("Please enter your name to proceed.")
            elif pin_input != PORTAL_PIN:
                st.error("Incorrect password. Please verify your passcode.")
            else:
                st.session_state.authenticated = True
                st.session_state.student_name = name_input.strip()
                st.session_state.start_time = time.time()
                st.rerun()

# --- WINDOW 2: EXAM INTERFACE ---
else:
    try:
        df = load_questions()
        if df.empty:
            st.error("The question database is empty.")
            st.stop()

        cols = {c.lower().replace(" ", ""): c for c in df.columns}
        id_col = cols.get('id', df.columns[0])
        subject_col = cols.get('subject', df.columns[1])
        question_col = cols.get('question', df.columns[2])
        op_a = cols.get('optiona', df.columns[3])
        op_b = cols.get('optionb', df.columns[4])
        op_c = cols.get('optionc', df.columns[5])
        op_d = cols.get('optiond', df.columns[6])
        ans_col = cols.get('correctanswer', df.columns[7])

        total_q = len(df)

        if not st.session_state.submitted:
            # Live Reverse Timer
            total_seconds = DEFAULT_TEST_MINUTES * 60
            elapsed_seconds = int(time.time() - st.session_state.start_time)
            remaining_seconds = total_seconds - elapsed_seconds

            if remaining_seconds <= 0:
                st.session_state.submitted = True
                st.warning("⏰ Time has expired. Your test was automatically submitted.")
                st.rerun()

            mins, secs = divmod(remaining_seconds, 60)
            
            # Header Bar
            st.caption(f"Candidate: **{st.session_state.student_name}**")
            st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")
            st.divider()

            col_main, col_nav = st.columns([3, 1])

            curr_idx = st.session_state.current_q
            row = df.iloc[curr_idx]
            q_id = row[id_col]

            # Question Body
            with col_main:
                st.subheader(f"Question {curr_idx + 1} of {total_q}")
                st.markdown(f"**Subject:** {row[subject_col]}")
                st.markdown(f"### {row[question_col]}")

                options = [
                    str(row[op_a]).strip(),
                    str(row[op_b]).strip(),
                    str(row[op_c]).strip(),
                    str(row[op_d]).strip()
                ]

                saved_ans = st.session_state.answers.get(q_id, None)
                saved_index = options.index(saved_ans) if saved_ans in options else None

                user_choice = st.radio(
                    "Select Option:", 
                    options, 
                    index=saved_index, 
                    key=f"radio_{q_id}_{curr_idx}"
                )

                if user_choice:
                    st.session_state.answers[q_id] = user_choice

                st.write("---")
                
                # Navigation Controls
                btn_prev, btn_mark, btn_next = st.columns(3)

                with btn_prev:
                    if st.button("⬅️ Previous", disabled=(curr_idx == 0)):
                        st.session_state.current_q -= 1
                        st.rerun()

                with btn_mark:
                    is_marked = q_id in st.session_state.marked
                    mark_label = "🔖 Unmark Question" if is_marked else "📌 Mark for Review"
                    if st.button(mark_label):
                        if is_marked:
                            st.session_state.marked.remove(q_id)
                        else:
                            st.session_state.marked.add(q_id)
                        st.rerun()

                with btn_next:
                    if st.button("Next ➡️", disabled=(curr_idx == total_q - 1)):
                        st.session_state.current_q += 1
                        st.rerun()

            # Side Palette
            with col_nav:
                st.markdown("### Palette")
                st.caption("🟢 Answered | 🟡 Marked | ⚪ Empty")

                grid_cols = st.columns(4)
                for idx in range(total_q):
                    qid = df.iloc[idx][id_col]
                    
                    if qid in st.session_state.marked:
                        badge = f"🟡 {idx+1}"
                    elif qid in st.session_state.answers:
                        badge = f"🟢 {idx+1}"
                    else:
                        badge = f"⚪ {idx+1}"

                    col_idx = idx % 4
                    with grid_cols[col_idx]:
                        if st.button(badge, key=f"nav_btn_{idx}"):
                            st.session_state.current_q = idx
                            st.rerun()

                st.write("---")
                if st.button("🚨 Submit Exam", type="primary"):
                    st.session_state.confirm_submit = True

            # Confirmation Modal
            if st.session_state.get("confirm_submit", False):
                st.warning("⚠️ **FINAL SUBMISSION VERIFICATION**")
                
                answered_cnt = len(st.session_state.answers)
                unanswered_cnt = total_q - answered_cnt
                marked_cnt = len(st.session_state.marked)

                st.write(f"* **Candidate Name:** {st.session_state.student_name}")
                st.write(f"* **Total Questions:** {total_q}")
                st.write(f"* **Answered:** {answered_cnt}")
                st.write(f"* **Unanswered:** {unanswered_cnt}")
                st.write(f"* **Marked for Review:** {marked_cnt}")

                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("✅ Finish & Submit"):
                        st.session_state.submitted = True
                        st.session_state.confirm_submit = False
                        st.rerun()
                with c_no:
                    if st.button("❌ Return to Test"):
                        st.session_state.confirm_submit = False
                        st.rerun()

            time.sleep(1)
            st.rerun()

        # Scorecard Window
        else:
            st.header("📊 Final Scorecard")
            st.markdown(f"**Student Name:** {st.session_state.student_name}")

            score = 0
            for idx, row in df.iterrows():
                qid = row[id_col]
                u_ans = str(st.session_state.answers.get(qid, "")).strip()
                c_ans = str(row[ans_col]).strip()
                if u_ans == c_ans:
                    score += 1

            pct = (score / total_q) * 100
            st.metric("Final Result", f"{score} / {total_q}", f"{pct:.1f}%")

            if pct >= 50:
                st.balloons()
                st.success("Exam Passed.")
            else:
                st.warning("Exam Failed. Review syllabus material.")

            if st.button("🔄 Logout & Exit"):
                st.session_state.authenticated = False
                st.session_state.student_name = ""
                st.session_state.current_q = 0
                st.session_state.answers = {}
                st.session_state.marked = set()
                st.session_state.submitted = False
                st.rerun()

    except Exception as e:
        st.error(f"System Error: {e}")
