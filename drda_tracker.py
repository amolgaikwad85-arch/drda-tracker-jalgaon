import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# डॅशबोर्डचे सेटिंग
st.set_page_config(page_title="DRDA जळगाव - अहवाल ट्रॅकर", page_icon="📋", layout="wide")

# डेटा सेव्ह करण्यासाठी फाईलचे नाव (तुमच्या लॅपटॉपवर सेव्ह होईल)
DATA_FILE = "drda_complaints_data.csv"

# डेटा लोड करण्याचे फंक्शन
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["पत्र क्रमांक", "तक्रारदाराचे नाव", "पंचायत समिती", "पत्र पाठवलेली तारीख", "मुदत (दिवस)", "अंतिम तारीख", "सद्यस्थिती"])

# डेटा सेव्ह करण्याचे फंक्शन
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# मुख्य डॅशबोर्ड हेडिंग
st.title("📊 DRDA जळगाव - तक्रार व अहवाल पाठपुरावा डॅशबोर्ड")
st.markdown("*प्रकल्प संचालक, जिल्हा ग्रामीण विकास यंत्रणा, जळगाव*")
st.markdown("---")

# डेटा लोड करा
df = load_data()

# डावीकडील मेनू (नवीन पत्र जोडण्यासाठी)
st.sidebar.header("📝 नवीन पत्र नोंदवा (New Entry)")
with st.sidebar.form("new_complaint_form", clear_on_submit=True):
    letter_no = st.text_input("पत्र क्रमांक (Outward No.)")
    applicant_name = st.text_input("तक्रारदाराचे नाव")
    panchayat_samiti = st.selectbox("पंचायत समिती (BDO)", ["जळगाव", "अमळनेर", "पाचोरा", "भडगाव", "मुक्ताईनगर", "धरणगाव", "चोपडा", "बोदवड", "यावल", "इतर"])
    sent_date = st.date_input("पत्र पाठवलेली तारीख")
    deadline_days = st.number_input("मुदत (दिवस)", min_value=1, max_value=30, value=7)
    
    submit_button = st.form_submit_button("नोंद करा (Save)")
    
    if submit_button and letter_no and applicant_name:
        deadline_date = sent_date + timedelta(days=deadline_days)
        new_data = pd.DataFrame([{
            "पत्र क्रमांक": letter_no,
            "तक्रारदाराचे नाव": applicant_name,
            "पंचायत समिती": panchayat_samiti,
            "पत्र पाठवलेली तारीख": sent_date.strftime("%Y-%m-%d"),
            "मुदत (दिवस)": deadline_days,
            "अंतिम तारीख": deadline_date.strftime("%Y-%m-%d"),
            "सद्यस्थिती": "Pending ⏳"
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success("नवीन पत्राची नोंद यशस्वीरित्या झाली!")

# डॅशबोर्ड वरील आकडेवारी (Metrics)
if not df.empty:
    today = datetime.now().date()
    # तारखेनुसार फिल्टर करणे
    df['अंतिम तारीख'] = pd.to_datetime(df['अंतिम तारीख']).dt.date
    
    total_complaints = len(df)
    pending_complaints = len(df[df["सद्यस्थिती"] == "Pending ⏳"])
    overdue_complaints = len(df[(df["सद्यस्थिती"] == "Pending ⏳") & (df['अंतिम तारीख'] < today)])
    completed_complaints = len(df[df["सद्यस्थिती"] == "Received ✅"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("एकूण पत्रे (Total)", total_complaints)
    col2.metric("प्रलंबित अहवाल (Pending)", pending_complaints)
    col3.metric("मुदत उलटलेली पत्रे (Overdue 🚨)", overdue_complaints)
    col4.metric("प्राप्त अहवाल (Received)", completed_complaints)

    st.markdown("### 📋 प्रलंबित व मुदत उलटलेल्या पत्रांची यादी")
    
    # मुदत संपलेल्या पत्रांना लाल रंगात हायलाईट करण्यासाठी
    def highlight_overdue(row):
        if row['सद्यस्थिती'] == 'Pending ⏳' and row['अंतिम तारीख'] < today:
            return ['background-color: #ffcccc'] * len(row)
        elif row['सद्यस्थिती'] == 'Received ✅':
            return ['background-color: #ccffcc'] * len(row)
        else:
            return [''] * len(row)

    # डेटा दाखवणे
    st.dataframe(df.style.apply(highlight_overdue, axis=1), use_container_width=True)

    # अहवाल प्राप्त झाल्याची नोंद करणे (Update Status)
    st.markdown("### ✅ अहवाल प्राप्त (Update Status)")
    update_col1, update_col2 = st.columns([3, 1])
    with update_col1:
        selected_letter = st.selectbox("कोणत्या पत्राचा अहवाल प्राप्त झाला?", df[df["सद्यस्थिती"] == "Pending ⏳"]["पत्र क्रमांक"])
    with update_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("अहवाल प्राप्त झाला (Mark as Received)"):
            if selected_letter:
                df.loc[df["पत्र क्रमांक"] == selected_letter, "सद्यस्थिती"] = "Received ✅"
                save_data(df)
                st.success(f"{selected_letter} ची स्थिती 'Received' म्हणून अपडेट झाली!")
                st.rerun()
else:
    st.info("डॅशबोर्डमध्ये अद्याप कोणतीही नोंद नाही. डावीकडील मेनूमधून नवीन पत्र नोंदवा.")
