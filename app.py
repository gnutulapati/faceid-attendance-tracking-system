import streamlit as st
import cv2
import numpy as np
import os
from src.core import FaceSystem
from src.utils import log_action, get_logs

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Medoc Health IT",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ASSET LOADER ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    load_css(css_path)

# --- 3. SYSTEM INIT ---
@st.cache_resource
def get_system():
    return FaceSystem()

system = get_system()

# --- 4. HEADER UI ---
with st.container():
    col_logo, col_text = st.columns([1, 8])
    
    with col_logo:
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
        else:
            st.warning("⚠️ Logo missing")
            
    with col_text:
        st.markdown("""
            <div style="padding-top: 10px;">
                <span style="font-size: 26px; font-weight: 800; color: #2C3E50;">Medoc</span>
                <span style="font-size: 26px; font-weight: 800; color: #17A2B8;">Health IT</span>
                <br>
                <span style="font-size: 14px; color: #6c757d; font-weight: 500;">Secure Biometric Access Control System</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("#### **System Navigation**")
    
    # ADDED EMOJIS HERE
    menu = st.radio(
        "Navigate",
        ["🆔 Attendance", "📝 Registration", "📊 Access Logs"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("#### **Status**")
    st.markdown('<div class="status-badge">System Online</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("v2.4.0 | Enterprise Edition")

# --- 6. PAGE ROUTING (UPDATED TO MATCH EMOJIS) ---

# === PAGE: ATTENDANCE ===
if menu == "🆔 Attendance":
    st.subheader("Biometric Verification")
    
    col_cam, col_spacer, col_res = st.columns([1.5, 0.2, 1])
    
    with col_cam:
        st.markdown("**Live Camera Feed**")
        img_file = st.camera_input("Camera", label_visibility="collapsed")
    
    with col_res:
        st.markdown("**Identification Results**")
        
        with st.container():
            if img_file:
                bytes_data = img_file.getvalue()
                img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                name, score = system.identify(img)
                
                if name != "Unknown" and name != "No Face":
                    # SUCCESS
                    st.success("Identity Verified")
                    st.markdown(f"### 👤 {name}")
                    st.progress(min(float(score) + 0.1, 1.0))
                    st.caption(f"Confidence: {int(score*100)}%")
                    
                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Punch In", use_container_width=True):
                            success, msg = log_action(name, "IN")
                            if success: st.toast(msg, icon="✅")
                            else: st.warning(msg)
                    with b2:
                        if st.button("Punch Out", use_container_width=True):
                            success, msg = log_action(name, "OUT")
                            if success: st.toast(msg, icon="👋")
                            else: st.warning(msg)
                else:
                    st.error("Verification Failed")
                    st.markdown(f"**Status:** {name}")
            else:
                st.info("System Ready. Please align face in camera.")

# === PAGE: REGISTRATION ===
elif menu == "📝 Registration":
    st.subheader("Employee Enrollment")
    
    col_form, col_cam = st.columns([1.2, 1])
    
    with st.form("reg_form"):
        with col_form:
            st.markdown("#### 1. Employee Details")
            st.info("Please ensure the name matches the HR Database.")
            name_in = st.text_input("Full Legal Name")
        
        with col_cam:
            st.markdown("#### 2. Biometric Capture")
            img_in = st.camera_input("Register", label_visibility="collapsed")
        
        st.markdown("---")
        submit = st.form_submit_button("Save Employee Profile", type="primary")
        
        if submit:
            if not name_in or not img_in:
                st.error("Please provide both Name and Photo.")
            else:
                bytes_data = img_in.getvalue()
                img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                success, msg = system.register_user(img, name_in)
                if success: st.toast(msg, icon="✅")
                else: st.error(msg)

# === PAGE: LOGS ===
elif menu == "📊 Access Logs":
    col_head, col_btn = st.columns([4, 1])
    with col_head:
        st.subheader("System Audit Logs")
    with col_btn:
        if st.button("Refresh Data", use_container_width=True):
            st.rerun()
            
    df = get_logs()
    st.dataframe(df, use_container_width=True, hide_index=True)