# --- CUSTOM CSS FOR HIGH VISIBILITY (DESKTOP & MOBILE) ---
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
    
    /* Question Title - Forced High Contrast for Mobile & Dark Mode */
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
    
    /* Radio Option Text - Force Visibility on Mobile */
    div[data-testid="stRadio"] label p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        line-height: 1.5 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    /* Target Streamlit markdown overrides inside question cards */
    .question-card p, .question-card span, .question-card h3 {
        color: #0F172A !important;
        opacity: 1 !important;
    }

    /* Action Buttons */
    .stButton>button {
        width: 100%;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
    }
    div[data-testid="column"] .stButton>button {
        padding: 6px 2px !important;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)
