import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# ------------------ SESSION ------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "uploaded_done" not in st.session_state:
    st.session_state.uploaded_done = False


# ------------------ UI ------------------
st.set_page_config(page_title="AI Document Intelligence", layout="wide")

st.title("🚀 AI Document Intelligence")


# ------------------ LOGIN ------------------
with st.sidebar:
    st.header("🔐 Login")

    if st.session_state.token:
        st.success("✅ Logged in")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.uploaded_done = False
            st.rerun()
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                res = requests.post(
                    f"{API_URL}/login",
                    json={"username": username, "password": password},
                    timeout=10
                )

                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error(res.json())  # show actual error

            except Exception as e:
                st.error(f"Login error: {e}")

    st.divider()

    # ------------------ FILE UPLOAD ------------------
    uploaded_file = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"])

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file

        if st.session_state.token and not st.session_state.uploaded_done:
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        uploaded_file.type
                    )
                }

                headers = {
                    "Authorization": f"Bearer {st.session_state.token}"
                }

                res = requests.post(
                    f"{API_URL}/upload_file/",
                    files=files,
                    headers=headers,
                    timeout=20
                )

                if res.status_code == 200:
                    st.success("File uploaded successfully")
                    st.session_state.uploaded_done = True
                else:
                    st.error(res.text)

            except Exception as e:
                st.error(f"Upload error: {e}")

        elif not st.session_state.token:
            st.warning("Please login first")


# ------------------ HEADERS ------------------
headers = {}
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}


# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["💬 Chat Assistant", "🧾 Invoice Extraction"])


# ===================== CHAT =====================
with tab1:
    st.subheader("AI Chat Assistant")

    mode = st.radio(
        "Select Mode",
        ["General Chat", "Document Q&A"]
    )

    question = st.text_input("Ask your question")

    if st.button("Get Answer"):

        if not st.session_state.token:
            st.error("Login required")
            st.stop()

        if not question:
            st.warning("Enter a question")
            st.stop()

        payload = {
            "question": question,
            "mode": "general" if mode == "General Chat" else "rag"
        }

        if mode == "Document Q&A":
            if not st.session_state.uploaded_file:
                st.error("Upload document first")
                st.stop()

            payload["file_name"] = st.session_state.uploaded_file.name

        try:
            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{API_URL}/query/",
                    json=payload,
                    headers=headers,
                    timeout=30
                )

            if res.status_code == 200:
                data = res.json()

                st.success(f"Mode: {data.get('mode')}")

                st.markdown(
                    f"""
                    <div style="padding:15px; border-radius:10px; background:#f5f5f5">
                    {data.get('answer')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.error(res.text)

        except Exception as e:
            st.error(f"Request failed: {e}")


# ===================== INVOICE =====================
with tab2:
    st.subheader("Invoice Extraction")

    invoice_question = st.text_input("Optional question")

    if st.button("Extract Invoice"):

        if not st.session_state.token:
            st.error("Login required")
            st.stop()

        if not st.session_state.uploaded_file:
            st.error("Upload file first")
            st.stop()

        try:
            with st.spinner("Extracting..."):
                res = requests.post(
                    f"{API_URL}/extract_invoice/",
                    params={
                        "file_name": st.session_state.uploaded_file.name,
                        "question": invoice_question
                    },
                    headers=headers,
                    timeout=30
                )

            if res.status_code == 200:
                data = res.json()

                st.success("Invoice extracted")

                st.write("Invoice No:", data.get("invoice_number"))
                st.write("Date:", data.get("invoice_date"))
                st.write("Vendor:", data.get("vendor_name"))
                st.write("Total:", data.get("total_amount"))

                if data.get("items"):
                    st.dataframe(pd.DataFrame(data["items"]))

            else:
                st.error(res.text)

        except Exception as e:
            st.error(f"Error: {e}")




            