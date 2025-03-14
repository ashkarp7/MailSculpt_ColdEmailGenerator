import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# Streamlit UI Configuration
st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("MailSculpt : Cold Mail Generator")
    st.markdown("Personalized job emails made easy and effective..")

    # UI: User Inputs
    st.subheader("🔗 Enter Job Posting URL")
    
    col1, col2 = st.columns([4, 1])

    with col1:
        job_url = st.text_input("Enter the URL of the job posting:", placeholder="https://example.com/job-posting")

    with col2:
        submit_button = st.button("🚀 Generate Email", use_container_width=True)

    st.divider()  # Visual separation

    # Processing on Submit
    if submit_button:
        if not job_url.startswith("http"):
            st.error("❌ Please enter a valid URL (starting with http or https).")
            return

        with st.spinner("Fetching job details... ⏳"):
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
