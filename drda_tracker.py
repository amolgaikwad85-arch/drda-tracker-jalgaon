import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px

# ⚙️ पेज कॉन्फिगरेशन (Full Width & Title)
st.set_page_config(page_title="DRDA Smart Grievance Portal", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# 🎨 Custom CSS for Advanced Graphics (Corporate Look)
st.markdown("""
    <style>
    /* पार्श्वभूमी (Background) */
    .stApp {
        background-color: #f4f6f9;
    }
    /* मेट्रिक्स कार्ड डिझाईन (3D Shadow) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #1f77b4;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    /* हेडिंग रंग (Headings) */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* बटण डिझाईन (Buttons) */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #11568c;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "drda_grievance_data.csv"

# डेटा लोड आणि सेव्ह फंक्शन्स
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "टोकन क्रमांक", "तक्रारदाराचे नाव", "योजना", "प्राधान्यक्रम", 
            "पंचायत समिती", "नोंदणी तारीख", "अंतिम तारीख", "सद्यस्थिती", "कारवाईचा शेरा"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def generate_token(df):
    year = datetime.now().year
    count = len(df) + 1
    return f"DRDA-{year}-{count:03d}"

# 🏢 हेडर सेक्शन
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.title("🏢 जिल्हा ग्रामीण विकास यंत्रणा (DRDA), जळगाव")
    st.subheader("स्मार्ट तक्रार निवारण व संनियंत्रण डॅशबोर्ड (Smart Portal 3.0)")
st.markdown("---")

df = load_data()

# 📝 डावीकडील मेनू: नवीन तक्रार
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Seal_of_Maharashtra.svg/150px-Seal_of_Maharashtra.svg.png", width=100)
    st.header("📝 नवीन नोंदणी (New Entry)")
    with st.form("grievance_form", clear_on_submit=True):
        applicant_name = st.text_input("तक्रारदाराचे नाव")
        scheme = st.selectbox("योजना / विषय", ["पंतप्रधान आवास", "रमाई आवास", "शबरी आवास", "मनरेगा", "ग्रामपंचायत", "इतर"])
        priority = st.radio("प्राधान्यक्रम", ["🔴 अतितातडीचे (VIP)", "🟡 तातडीचे", "🟢 सामान्य"])
        panchayat_samiti = st.selectbox("पंचायत समिती", ["जळगाव", "अमळनेर", "पाचोरा", "भडगाव", "मुक्ताईनगर", "धरणगाव", "चोपडा", "बोदवड", "यावल", "रावेर", "पारोळा", "चाळीसगाव", "जामनेर", "एरंडोल", "भडगाव"])
        
        # नवीन रकाना: पत्र पाठवल्याची तारीख (बाय डिफॉल्ट आजची तारीख असेल, पण बदलता येईल)
        sent_date = st.date_input("पत्र पाठवल्याची तारीख", value=datetime.now().date())
        
        deadline_days = st.number_input("मुदत (दिवस)", min_value=1, max_value=30, value=7)
        submit_button = st.form_submit_button("नोंद करा (Submit)")
        
        if submit_button and applicant_name:
            token_id = generate_token(df)
            # अंतिम तारीख आता तुम्ही निवडलेल्या तारखेवरून मोजली जाईल
            deadline_date = sent_date + timedelta(days=deadline_days)
            new_data = pd.DataFrame([{
                "टोकन क्रमांक": token_id,
                "तक्रारदाराचे नाव": applicant_name,
                "योजना": scheme,
                "प्राधान्यक्रम": priority,
                "पंचायत समिती": panchayat_samiti,
                "नोंदणी तारीख": sent_date.strftime("%Y-%m-%d"),
                "अंतिम तारीख": deadline_date.strftime("%Y-%m-%d"),
                "सद्यस्थिती": "Pending ⏳",
                "कारवाईचा शेरा": "-"
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success(f"✅ नोंदणी यशस्वी! टोकन: {token_id}")
            st.toast('नवीन तक्रार पोर्टलवर नोंदवली गेली आहे!', icon='🎉')
            st.rerun()

# 📊 डॅशबोर्ड व टॅब्स (Tab Layout for clean UI)
if not df.empty:
    today = datetime.now().date()
    df['अंतिम तारीख'] = pd.to_datetime(df['अंतिम तारीख']).dt.date
    
    total = len(df)
    resolved = len(df[df["सद्यस्थिती"] == "Resolved ✅"])
    pending = len(df[df["सद्यस्थिती"] == "Pending ⏳"])
    overdue = len(df[(df["सद्यस्थिती"] == "Pending ⏳") & (df['अंतिम तारीख'] < today)])

    # ३ सुंदर टॅब्स तयार करणे
    tab1, tab2, tab3 = st.tabs(["📊 ॲनालिटिक्स डॅशबोर्ड (Analytics)", "📋 प्रलंबित यादी (Live Tracking)", "✅ कारवाई कक्ष (Action Desk)"])

    # ---------- TAB 1: Analytics & Graphs ----------
    with tab1:
        st.markdown("### 📈 सद्यस्थिती अहवाल (Key Metrics)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("एकूण तक्रारी (Total)", total)
        m2.metric("निकाली काढलेल्या (Resolved)", resolved, f"{(resolved/total)*100:.1f}%")
        m3.metric("प्रलंबित (Pending)", pending)
        m4.metric("मुदत उलटलेल्या (Overdue 🚨)", overdue, delta="-Action Required", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactive Graphs using Plotly
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### 📍 तालुकावार तक्रारी (Panchayat Samiti wise)")
            ps_counts = df['पंचायत समिती'].value_counts().reset_index()
            ps_counts.columns = ['पंचायत समिती', 'तक्रारींची संख्या']
            fig_bar = px.bar(ps_counts, x='पंचायत समिती', y='तक्रारींची संख्या', text='तक्रारींची संख्या', color='पंचायत समिती', template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with g2:
            st.markdown("#### 🥧 तक्रारींची सद्यस्थिती (Status Overview)")
            status_counts = df['सद्यस्थिती'].value_counts().reset_index()
            status_counts.columns = ['सद्यस्थिती', 'संख्या']
            fig_pie = px.pie(status_counts, values='संख्या', names='सद्यस्थिती', hole=0.4, color='सद्यस्थिती', 
                             color_discrete_map={"Resolved ✅": "#2ca02c", "Pending ⏳": "#ff7f0e"}, template="plotly_white")
            st.plotly_chart(fig_pie, use_container_width=True)

    # ---------- TAB 2: Live Tracking List ----------
    with tab2:
        st.markdown("### 📋 लाइव्ह ट्रॅकिंग व मुदत अलर्ट")
        def highlight_rows(row):
            if row['सद्यस्थिती'] == 'Pending ⏳' and row['अंतिम तारीख'] < today:
                return ['background-color: #ffe6e6; color: #cc0000; font-weight: bold'] * len(row) # Red Overdue
            elif row['सद्यस्थिती'] == 'Resolved ✅':
                return ['background-color: #e6ffe6; color: #006600'] * len(row) # Green Resolved
            else:
                return ['background-color: #fffde6'] * len(row) # Yellow Pending
        
        display_df = df[["टोकन क्रमांक", "तक्रारदाराचे नाव", "योजना", "प्राधान्यक्रम", "पंचायत समिती", "अंतिम तारीख", "सद्यस्थिती", "कारवाईचा शेरा"]]
        st.dataframe(display_df.style.apply(highlight_rows, axis=1), height=400, use_container_width=True)

    # ---------- TAB 3: Action Desk ----------
    with tab3:
        st.markdown("### ✅ तक्रार निकाली काढा (Update Resolution)")
        st.info("BDO कडून अहवाल प्राप्त झाल्यावर येथे टोकन निवडून फाईल बंद करा.")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            pending_tokens = df[df["सद्यस्थिती"] == "Pending ⏳"]["टोकन क्रमांक"].tolist()
            selected_token = st.selectbox("टोकन क्रमांक शोधा (Search ID)", ["निवडा..."] + pending_tokens)
        with c2:
            action_remark = st.text_area("कारवाईचा शेरा / अहवालाचा गोषवारा (Action Taken Remark)", placeholder="सविस्तर शेरा लिहा...")
        with c3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("✅ फाईल बंद करा (Close File)"):
                if selected_token != "निवडा..." and action_remark:
                    df.loc[df["टोकन क्रमांक"] == selected_token, "सद्यस्थिती"] = "Resolved ✅"
                    df.loc[df["टोकन क्रमांक"] == selected_token, "कारवाईचा शेरा"] = action_remark
                    save_data(df)
                    st.balloons() # 🎈 Success Animation
                    st.success(f"{selected_token} कायमस्वरूपी निकाली काढण्यात आली आहे!")
                    st.rerun()
                else:
                    st.warning("कृपया टोकन क्रमांक निवडा आणि शेरा लिहा.")
else:
    st.info("👋 डॅशबोर्डमध्ये तुमचे स्वागत आहे! कृपया डावीकडील मेनूमधून नवीन तक्रार नोंदवा.")
