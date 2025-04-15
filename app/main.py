import sys
import os

# Patch for ChromaDB's SQLite requirement
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
    os.environ["SQLITE_MODULE"] = "pysqlite3"
except ImportError:
    pass



import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# Streamlit UI Configuration
st.set_page_config(layout="wide", page_title="MailSculpt", page_icon="📧")

# Custom Styling for Dark Theme
st.markdown("""
    <style>
        body {
            background-color: #0F0F0F;
            color: #EAEAEA;
        }
        .title {
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            background: linear-gradient(to right, #A855F7, #FACC15);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #BBBBBB;
        }
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid #555;
            border-radius: 12px;
            padding: 10px;
            color: white;
        }
        .stButton>button {
            background: linear-gradient(135deg, #9333EA, #FACC15);
            color: white;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 20px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def create_streamlit_app(llm, portfolio, clean_text):
    # Title & Subtitle
    st.markdown('<h1 class="title">MailSculpt: Cold Email Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Effortlessly craft personalized job emails with AI-powered insights.</p>', unsafe_allow_html=True)
    
    # UI: User Inputs
    with st.container():
        st.subheader("🔗 Enter Job Posting URL")
        
        col1, col2 = st.columns([5, 2])

        with col1:
            job_url = st.text_input(
                "Enter the job posting URL:",
                placeholder="https://example.com/job-posting"
            )

        with col2:
            st.markdown("<div style='margin-top: 8px'></div>", unsafe_allow_html=True)
            submit_button = st.button("🚀 Generate Email")

    st.divider()  # Visual separation

    # Processing on Submit
    if submit_button:
        if not job_url.startswith("http"):
            st.error("❌ Please enter a valid URL (starting with http or https).")
            return

        with st.spinner("🔍 Fetching job details... Please wait."):
            try:
                loader = WebBaseLoader(job_url)
                data = clean_text(loader.load().pop().page_content)
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)

                for job in jobs:
                    skills = job.get("skills", [])
                    links = portfolio.query_links(skills)
                    email = llm.write_mail(job, links)

                    st.success("✅ Email Generated Successfully!")
                    st.code(email, language="markdown")

            except Exception as e:
                st.error(f"❌ An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)