import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px

st.set_page_config(page_title="DRDA Smart Grievance Portal", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    div[data-testid="metric-container"] { background-color: #ffffff; border-radius: 12px; padding: 15px 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); border-left: 6px solid #1f77b4; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "drda_grievance_data.csv"

# 🔄 डेटा लोड आणि अपडेट करणे (जुन्या डेटामध्ये नवीन रकाने आपोआप ॲड होतील)
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # जुन्या 'नोंदणी तारीख' ला 'पत्र पाठवल्याची तारीख' मध्ये बदलणे
        if "नोंदणी तारीख" in df.columns and "पत्र पाठवल्याची तारीख" not in df.columns:
            df.rename(columns={"नोंदणी तारीख": "पत्र पाठवल्याची तारीख"}, inplace=True)
        
        # नवीन स्मरण पत्राचे रकाने नसतील तर ॲड करणे
        for col in ["स्मरण पत्र १", "स्मरण पत्र २", "स्मरण पत्र ३"]:
            if col not in df.columns:
                df[col] = "-"
        return df
    else:
        return pd.DataFrame(columns=[
            "टोकन क्रमांक", "तक्रारदाराचे नाव", "योजना", "प्राधान्यक्रम", 
            "पंचायत समिती", "पत्र पाठवल्याची तारीख", "अंतिम तारीख", "सद्यस्थिती", 
            "स्मरण पत्र १", "स्मरण पत्र २", "स्मरण पत्र ३", "कारवाईचा शेरा"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def generate_token(df):
    year = datetime.now().year
    count = len(df) + 1
    return f"DRDA-{year}-{count:03d}"

# 🏢 हेडर
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.title("🏢 जिल्हा ग्रामीण विकास यंत्रणा (DRDA), जळगाव")
    st.subheader("स्मार्ट तक्रार निवारण व संनियंत्रण डॅशबोर्ड (Smart Portal)")
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
        
        sent_date = st.date_input("पत्र पाठवल्याची तारीख", value=datetime.now().date())
        deadline_days = st.number_input("मुदत (दिवस)", min_value=1, max_value=30, value=7)
        submit_button = st.form_submit_button("नोंद करा (Submit)")
        
        if submit_button and applicant_name:
            token_id = generate_token(df)
            deadline_date = sent_date + timedelta(days=deadline_days)
            new_data = pd.DataFrame([{
                "टोकन क्रमांक": token_id, "तक्रारदाराचे नाव": applicant_name, "योजना": scheme,
                "प्राधान्यक्रम": priority, "पंचायत समिती": panchayat_samiti, 
                "पत्र पाठवल्याची तारीख": sent_date.strftime("%Y-%m-%d"),
                "अंतिम तारीख": deadline_date.strftime("%Y-%m-%d"), "सद्यस्थिती": "Pending ⏳",
                "स्मरण पत्र १": "-", "स्मरण पत्र २": "-", "स्मरण पत्र ३": "-", "कारवाईचा शेरा": "-"
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.success(f"✅ नोंदणी यशस्वी! टोकन: {token_id}")
            st.toast('नवीन तक्रार पोर्टलवर नोंदवली गेली आहे!', icon='🎉')
            st.rerun()

if not df.empty:
    today = datetime.now().date()
    df['अंतिम तारीख'] = pd.to_datetime(df['अंतिम तारीख'], errors='coerce').dt.date
    
    tab1, tab2, tab3 = st.tabs(["📊 ॲनालिटिक्स", "📋 लाइव्ह ट्रॅकिंग व मुदत अलर्ट", "✅ कारवाई कक्ष (Action Desk)"])

    # ---------- TAB 1: Analytics ----------
    with tab1:
        total = len(df)
        resolved = len(df[df["सद्यस्थिती"] == "Resolved ✅"])
        pending = len(df[df["सद्यस्थिती"] == "Pending ⏳"])
        
        # मुदत उलटलेली पत्रे काढताना None व्हॅल्यू चेक करणे
        overdue = len(df[(df["सद्यस्थिती"] == "Pending ⏳") & (pd.notna(df['अंतिम तारीख'])) & (df['अंतिम तारीख'] < today)])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("एकूण तक्रारी", total)
        m2.metric("निकाली काढलेल्या", resolved)
        m3.metric("प्रलंबित", pending)
        m4.metric("मुदत उलटलेल्या (Overdue 🚨)", overdue)
        
        g1, g2 = st.columns(2)
        with g1:
            ps_counts = df['पंचायत समिती'].value_counts().reset_index()
            ps_counts.columns = ['पंचायत समिती', 'तक्रारींची संख्या']
            fig_bar = px.bar(ps_counts, x='पंचायत समिती', y='तक्रारींची संख्या', text='तक्रारींची संख्या', color='पंचायत समिती', template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with g2:
            status_counts = df['सद्यस्थिती'].value_counts().reset_index()
            status_counts.columns = ['सद्यस्थिती', 'संख्या']
            fig_pie = px.pie(status_counts, values='संख्या', names='सद्यस्थिती', hole=0.4, color='सद्यस्थिती', color_discrete_map={"Resolved ✅": "#2ca02c", "Pending ⏳": "#ff7f0e"}, template="plotly_white")
            st.plotly_chart(fig_pie, use_container_width=True)

    # ---------- TAB 2: Live Tracking & Reminders ----------
    with tab2:
        st.markdown("### 📋 लाइव्ह ट्रॅकिंग (पत्राच्या व स्मरण पत्रांच्या तारखांसह)")
        def highlight_rows(row):
            if row['सद्यस्थिती'] == 'Pending ⏳' and pd.notna(row['अंतिम तारीख']) and row['अंतिम तारीख'] < today:
                return ['background-color: #ffe6e6; color: #cc0000; font-weight: bold'] * len(row)
            elif row['सद्यस्थिती'] == 'Resolved ✅':
                return ['background-color: #e6ffe6; color: #006600'] * len(row)
            else:
                return ['background-color: #fffde6'] * len(row)
        
        display_df = df[["टोकन क्रमांक", "तक्रारदाराचे नाव", "पंचायत समिती", "पत्र पाठवल्याची तारीख", "अंतिम तारीख", "स्मरण पत्र १", "स्मरण पत्र २", "स्मरण पत्र ३", "सद्यस्थिती"]]
        st.dataframe(display_df.style.apply(highlight_rows, axis=1), height=400, use_container_width=True)

    # ---------- TAB 3: Action Desk (Reminders & Closing) ----------
    with tab3:
        st.markdown("### 📝 स्मरण पत्र नोंदवा किंवा फाईल निकाली काढा")
        st.info("येथून तुम्ही स्मरण पत्र पाठवल्याची तारीख अपडेट करू शकता किंवा अहवाल आल्यावर फाईल कायमची बंद करू शकता.")
        
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            pending_tokens = df[df["सद्यस्थिती"] == "Pending ⏳"]["टोकन क्रमांक"].tolist()
            selected_token = st.selectbox("टोकन क्रमांक शोधा", ["निवडा..."] + pending_tokens)
        with c2:
            action_type = st.radio("कारवाईचा प्रकार निवडा:", ["✉️ स्मरण पत्र १ पाठवले", "✉️ स्मरण पत्र २ पाठवले", "✉️ स्मरण पत्र ३ पाठवले", "✅ फाईल निकाली काढा (अहवाल प्राप्त)"])
        with c3:
            action_remark = st.text_area("कारवाईचा शेरा / अहवालाचा गोषवारा", placeholder="येथे माहिती लिहा...")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 माहिती सेव्ह करा (Update Record)"):
                if selected_token != "निवडा...":
                    action_date = datetime.now().strftime("%Y-%m-%d")
                    
                    if "स्मरण पत्र १" in action_type:
                        df.loc[df["टोकन क्रमांक"] == selected_token, "स्मरण पत्र १"] = action_date
                        st.toast(f'स्मरण पत्र १ ची नोंद झाली!', icon='✉️')
                    elif "स्मरण पत्र २" in action_type:
                        df.loc[df["टोकन क्रमांक"] == selected_token, "स्मरण पत्र २"] = action_date
                        st.toast(f'स्मरण पत्र २ ची नोंद झाली!', icon='✉️')
                    elif "स्मरण पत्र ३" in action_type:
                        df.loc[df["टोकन क्रमांक"] == selected_token, "स्मरण पत्र ३"] = action_date
                        st.toast(f'स्मरण पत्र ३ ची नोंद झाली!', icon='✉️')
                    elif "निकाली" in action_type:
                        if not action_remark:
                            st.error("फाईल बंद करण्यासाठी कारवाईचा शेरा लिहिणे अनिवार्य आहे!")
                            st.stop()
                        df.loc[df["टोकन क्रमांक"] == selected_token, "सद्यस्थिती"] = "Resolved ✅"
                        df.loc[df["टोकन क्रमांक"] == selected_token, "कारवाईचा शेरा"] = action_remark
                        st.balloons()
                        st.success(f"{selected_token} कायमस्वरूपी निकाली काढण्यात आली आहे!")
                    
                    save_data(df)
                    st.rerun()
                else:
                    st.warning("कृपया टोकन क्रमांक निवडा.")
else:
    st.info("👋 डॅशबोर्डमध्ये तुमचे स्वागत आहे! कृपया डावीकडील मेनूमधून नवीन तक्रार नोंदवा.")
