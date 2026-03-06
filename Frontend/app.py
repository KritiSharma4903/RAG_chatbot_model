import streamlit as st
import requests
import pandas as pd
import logging

API_URL = "http://127.0.0.1:8000"

# ------------------ LOGGER SETUP ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="🚀",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
.main-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #4A90E2, #8E44AD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}
.sub-text {
    text-align: center;
    color: gray;
    margin-bottom: 40px;
}
.card {
    padding: 25px;
    border-radius: 16px;
    background-color: #ffffff;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<div class="main-title">AI Document Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">RAG Search • Invoice Intelligence • Structured AI Extraction</div>', unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("⚙️ Setup")
    uploaded_file = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"])

    if uploaded_file:
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{API_URL}/upload_file/", files=files)

            if response.status_code == 200:
                st.success("File processed successfully ✅")
                logger.info(f"File uploaded successfully: {uploaded_file.name}")
            elif response.status_code == 400:
                st.error("Bad Request: Please check the file format or content ❌")
                logger.error(f"Bad Request during file upload: {uploaded_file.name}")
            elif response.status_code == 401:
                st.error("Unauthorized: Please check your API credentials ❌")
                logger.error("Unauthorized access during file upload")
            elif response.status_code == 404:
                st.error("API endpoint not found ❌")
                logger.error("Upload API endpoint not found")
            elif response.status_code == 500:
                st.error("Internal server error at backend ❌")
                logger.error("Server error during file upload")
            else:
                st.error(f"Unexpected error: {response.status_code} ❌")
                logger.error(f"Unexpected status code {response.status_code} during file upload")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
            logger.exception("Network exception during file upload")

# ------------------ MAIN TABS ------------------
tab1, tab2 = st.tabs(["📚 RAG Assistant", "🧾 Invoice Intelligence"])

# ==================== TAB 1 - RAG =========================

with tab1:
    if uploaded_file:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💬 Ask Anything From Your Document")
        question = st.text_input("Type your question", key="rag_question")

        if st.button("Generate Answer", key="rag_btn"):
            if not question:
                st.warning("Please enter a question")
            else:
                payload = {"file_name": uploaded_file.name, "question": question}
                try:
                    with st.spinner("Thinking... 🤔"):
                        response = requests.post(f"{API_URL}/query/", json=payload, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        st.success("Answer generated ✅")
                        st.markdown(f"""
                        <div style='padding:15px; border-radius:10px; background:#F4F6F7'>
                        {data.get("answer")}
                        </div>
                        """, unsafe_allow_html=True)
                        logger.info(f"RAG answer returned for file {uploaded_file.name}")
                    elif response.status_code == 404:
                        st.error("File not processed. Please upload the file first ❌")
                        logger.warning(f"Query attempted for unprocessed file: {uploaded_file.name}")
                    elif response.status_code == 500:
                        st.error("Internal server error at backend ❌")
                        logger.error(f"Server error during query for file: {uploaded_file.name}")
                    else:
                        st.error(f"Unexpected error occurred: {response.status_code} ❌")
                        logger.error(f"Unexpected status code {response.status_code} for file {uploaded_file.name}")

                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again ❌")
                    logger.exception(f"Timeout during query for file {uploaded_file.name}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend API ❌")
                    logger.exception("Connection error during RAG query")
                except requests.exceptions.RequestException as e:
                    st.error(f"An unexpected network error occurred: {e} ❌")
                    logger.exception(f"Network exception during RAG query for file {uploaded_file.name}")

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload a document to start using RAG Assistant.")

# ================= TAB 2 - INVOICE ========================

with tab2:
    if uploaded_file:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧾 Extract Structured Invoice Data")
        invoice_question = st.text_input(
            "Ask about a specific item (optional)",
            key="invoice_question"
        )

        if st.button("Extract Invoice Data", key="invoice_btn"):
            try:
                with st.spinner("Extracting structured data... 🔍"):
                    response = requests.post(
                        f"{API_URL}/extract_invoice/",
                        params={
                            "file_name": uploaded_file.name,
                            "question": invoice_question
                        },
                        timeout=30
                    )

                # ---------------- STATUS CHECK ----------------
                if response.status_code != 200:
                    st.error(f"API Error: {response.status_code} ❌")
                    logger.error(f"Invoice extraction failed: {response.text}")
                    st.stop()

                # ---------------- SAFE JSON PARSE ----------------
                try:
                    data = response.json()
                except Exception:
                    st.error("Invalid JSON response from backend ❌")
                    logger.error("Invalid JSON received from backend")
                    st.stop()

                if not data:
                    st.error("No data returned from backend ❌")
                    logger.error("Empty response from backend")
                    st.stop()

                if isinstance(data, dict) and data.get("error"):
                    st.error(data["error"])
                    logger.error(f"Backend returned error: {data['error']}")
                    st.stop()

                # ---------------- SUCCESS OUTPUT ----------------
                st.success("Invoice Extracted Successfully ✅")
                st.markdown("### 📌 Invoice Summary")

                st.write("**Invoice Number:**", data.get("invoice_number", "N/A"))
                st.write("**Invoice Date:**", data.get("invoice_date", "N/A"))
                st.write("**Vendor:**", data.get("vendor_name", "N/A"))
                st.write("**Total Amount:**", data.get("total_amount", "N/A"))

                items = data.get("items", [])

                if items:
                    df = pd.DataFrame(items)
                    st.markdown("### 🛒 Items")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No items found in invoice.")

                logger.info(f"Invoice extracted successfully: {uploaded_file.name}")

            except requests.exceptions.Timeout:
                st.error("Request timed out ❌")
                logger.exception("Timeout during invoice extraction")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend API ❌")
                logger.exception("Connection error during invoice extraction")

            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
                logger.exception("Network exception during invoice extraction")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload a document to use Invoice Intelligence.")