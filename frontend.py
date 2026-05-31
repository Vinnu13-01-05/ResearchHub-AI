import streamlit as st
from pypdf import PdfReader
from groq import Groq
import os

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="ResearchHub AI",
    page_icon="📚"
)

st.title("📚 ResearchHub AI")
st.write("Upload a PDF and ask questions about it.")

# -------------------------------
# GROQ API KEY
# -------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Groq API Key not found.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------
# SESSION STATE
# -------------------------------
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# -------------------------------
# PDF UPLOAD
# -------------------------------
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    st.session_state.pdf_text = text

    st.success("PDF uploaded successfully!")

# -------------------------------
# PDF SUMMARY
# -------------------------------
if st.session_state.pdf_text:

    if st.button("Generate Summary"):

        with st.spinner("Generating summary..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Summarize the following PDF content:

                        {st.session_state.pdf_text[:6000]}
                        """
                    }
                ]
            )

            summary = response.choices[0].message.content

            st.subheader("Summary")
            st.write(summary)

# -------------------------------
# ASK QUESTIONS
# -------------------------------
st.subheader("Ask Questions")

question = st.text_input(
    "Enter your question"
)

if st.button("Get Answer"):

    if not st.session_state.pdf_text:
        st.warning("Please upload a PDF first.")

    elif not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("Generating answer..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Answer only from the uploaded PDF."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        PDF Content:

                        {st.session_state.pdf_text[:6000]}

                        Question:
                        {question}
                        """
                    }
                ]
            )

            answer = response.choices[0].message.content

            st.subheader("Answer")
            st.write(answer)
