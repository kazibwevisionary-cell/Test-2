import streamlit as st
import pandas as pd
from supabase import create_client

# 1. DATABASE CONNECTION
# Hardcoded credentials for your KIU Q10 Project
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

# 2. PAGE CONFIG & STYLING
st.set_page_config(page_title="KIU Q10 Portal", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background: white; border-top: 1px solid #eee; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 10px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
</style>
""", unsafe_allow_html=True)

# 3. SESSION STATE FOR LOGIN
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 4. LOGIN PAGE
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🎓 KIU Q10 Study Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Login to Access Materials")
            user = st.text_input("Username", placeholder="Enter your ID")
            pw = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                # Simple logic: allows entry for testing
                st.session_state.logged_in = True
                st.rerun()
                
            st.markdown("---")
            if st.button("Guest Access (Browse Only)", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 5. NAVIGATION BAR
st.sidebar.title("Navigation")
role = st.sidebar.radio("Go to:", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠️ Management Console")
    tab1, tab2, tab3 = st.tabs(["Manual Entry", "Bulk Upload (Excel)", "Delete Items"])

    with tab1:
        with st.form("manual_add"):
            c_name = st.text_input("Course/Program Name")
            topic = st.text_input("Module Topic")
            wk = st.number_input("Week Number", 1, 15)
            v_url = st.text_input("YouTube/Video Link")
            n_url = st.text_input("Notes (Google Docs) Link")
            if st.form_submit_button("Add to Database"):
                data = {
                    "course_program": c_name,
                    "course_name": topic,
                    "week": wk,
                    "video_url": v_url,
                    "notes_url": n_url
                }
                supabase.table("materials").insert(data).execute()
                st.success(f"Successfully added Week {wk} for {c_name}!")

    with tab2:
        target_course = st.text_input("Enter Course Name for this file")
        uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx", "csv"])
        if uploaded_file and target_course:
            if st.button("Process & Upload"):
                df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
                for _, row in df.iterrows():
                    supabase.table("materials").insert({
                        "course_program": target_course,
                        "course_name": str(row.get('Topic Covered', 'No Title')),
                        "week": int(row.get('Week', 1)),
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('link to Google docs Document', ''))
                    }).execute()
                st.success("Bulk Upload Complete!")

    with tab3:
        items = supabase.table("materials").select("*").execute()
        for i in items.data:
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{i['course_program']}** - Wk {i['week']}: {i['course_name']}")
            if c2.button("Delete", key=f"del_{i['id']}"):
                supabase.table("materials").delete().eq("id", i['id']).execute()
                st.rerun()

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("📢 Post Announcement")
    with st.form("announcement"):
        title = st.text_input("Announcement Title")
        msg = st.text_area("Content")
        if st.form_submit_button("Publish Notice"):
            supabase.table("notices").insert({"title": title, "content": msg}).execute()
            st.success("Announcement Live!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.header("📖 Student Learning Area")
    query = st.text_input("Search for your Course (e.g., BIT, BBA, Law)").strip()
    
    if query:
        results = supabase.table("materials").select("*").ilike("course_program", f"%{query}%").order("week").execute()
        
        if results.data:
            for item in results.data:
                with st.expander(f"WEEK {item['week']} - {item['course_name']}"):
                    # Video Display logic
                    url = str(item.get('video_url', ""))
                    if "youtube" in url or "youtu.be" in url:
                        # Convert regular link to embed link
                        v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
                        st.markdown(f'<div class="video-container"><iframe src="https://www.youtube.com/embed/{v_id}"></iframe></div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Notes:** [Click to open document]({item['notes_url']})")
        else:
            st.info("No materials found for that course.")

st.markdown('<div class="footer">Developed by KMT Dynamics for KIU</div>', unsafe_allow_html=True)
