import streamlit as st
import requests
import pandas as pd
import logging

API_URL = "http://127.0.0.1:8000"

# ------------------ LOGGER ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="AI Document Intelligence", page_icon="🚀", layout="wide")

# ------------------ SESSION ------------------
if "token" not in st.session_state:
    st.session_state.token = None

# ------------------ CSS ------------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
}
.sub-text {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<div class="main-title">🚀 AI Document Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">RAG + RBAC + Invoice Extraction</div>', unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = requests.post(
                f"{API_URL}/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                st.session_state.token = response.json().get("access_token")
                st.success("Login successful ✅")
                logger.info("User logged in")
            else:
                st.error("Invalid credentials ❌")
        except Exception as e:
            st.error(f"Login error: {e}")

    if st.session_state.token:
        st.success("Authenticated ✅")

    st.divider()

    uploaded_file = st.file_uploader("📂 Upload TXT or PDF", type=["txt", "pdf"])

    # ------------------ UPLOAD ------------------
    if uploaded_file:
        if not st.session_state.token:
            st.error("Login first ❌")
            st.stop()

        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

            response = requests.post(
                f"{API_URL}/upload_file/",
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                st.success("File uploaded ✅")
                logger.info(f"Uploaded: {uploaded_file.name}")
            else:
                st.error(f"Upload failed: {response.status_code}")
        except Exception as e:
            st.error(f"Upload error: {e}")

# ------------------ HEADERS ------------------
headers = {}
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["📚 RAG Assistant", "🧾 Invoice Intelligence"])

# ==================== RAG TAB ====================
with tab1:
    if uploaded_file:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💬 Ask Questions")

        question = st.text_input("Enter your question")

        if st.button("Get Answer"):
            if not st.session_state.token:
                st.error("Login first ❌")
                st.stop()

            if not question:
                st.warning("Enter a question")
            else:
                payload = {
                    "file_name": uploaded_file.name,
                    "question": question
                }

                try:
                    with st.spinner("Thinking..."):
                        response = requests.post(
                            f"{API_URL}/query/",
                            json=payload,
                            headers=headers
                        )

                    if response.status_code == 200:
                        st.success("Answer ready ✅")
                        st.write(response.json().get("answer"))
                    else:
                        st.error(f"Error: {response.status_code}")

                except Exception as e:
                    st.error(f"Query error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload file to start")

# ==================== INVOICE TAB ====================
with tab2:
    if uploaded_file:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧾 Extract Invoice")

        invoice_question = st.text_input("Optional question")

        if st.button("Extract"):
            if not st.session_state.token:
                st.error("Login first ❌")
                st.stop()

            try:
                with st.spinner("Processing..."):
                    response = requests.post(
                        f"{API_URL}/extract_invoice/",
                        params={
                            "file_name": uploaded_file.name,
                            "question": invoice_question
                        },
                        headers=headers
                    )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Extracted ✅")

                    st.write("Invoice Number:", data.get("invoice_number"))
                    st.write("Date:", data.get("invoice_date"))
                    st.write("Vendor:", data.get("vendor_name"))
                    st.write("Total:", data.get("total_amount"))

                    items = data.get("items", [])
                    if items:
                        df = pd.DataFrame(items)
                        st.dataframe(df)
                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                st.error(f"Invoice error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload file first")

        