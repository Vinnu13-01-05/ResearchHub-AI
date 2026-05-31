import streamlit as st
import requests

st.set_page_config(page_title="ResearchHub AI", page_icon="📚")

st.title("📚 ResearchHub AI")
st.write("Upload a PDF and ask questions about it.")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:

    if st.button("Upload PDF"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        response = requests.post(
            "http://127.0.0.1:8000/upload-pdf",
            files=files
        )

        if response.status_code == 200:
            st.success("PDF uploaded successfully!")
        else:
            st.error("Upload failed!")

st.subheader("Ask Questions")

question = st.text_input(
    "Enter your question"
)

if st.button("Get Answer"):

    response = requests.post(
        "http://127.0.0.1:8000/ask-pdf",
        json={
            "message": question
        }
    )

    if response.status_code == 200:

        data = response.json()

        st.subheader("Answer")

        if "answer" in data:
            st.write(data["answer"])
        else:
            st.write(data)

    else:
        st.error("Failed to get answer.")