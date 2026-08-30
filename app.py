# --- CUSTOM CSS WITH NIGHT MODE OVERRIDES & TARGETED NAV BUTTON STYLES ---
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
    
    /* --- OVERRIDE MOBILE NIGHT/DARK MODE FOR RADIO OPTIONS --- */
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

    /* --- TARGET ONLY PREVIOUS, NEXT, AND MARK BUTTONS --- */
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
