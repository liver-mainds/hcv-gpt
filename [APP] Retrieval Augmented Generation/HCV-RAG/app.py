import streamlit as st
import openai
import os
from docx import Document

# Set page configuration
st.set_page_config(page_title="HCV-GPT", layout="wide", initial_sidebar_state="expanded")

OPENAI_API_KEY = 'INSERT YOUR OPENAI API KEY HERE'
MODEL_NAME = "INSERT MODEL NAME HERE"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Function to read content from a Word document
def read_docx_content(filename):
    doc = Document(filename)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Read content from external Word documents
current_dir = os.path.dirname(os.path.abspath(__file__))
file1_path = os.path.join(current_dir, 'file1.docx')
file2_path = os.path.join(current_dir, 'file2.docx')

file1_content = read_docx_content(file1_path)
file2_content = read_docx_content(file2_path)

# Prepare the prompt engineering instructions
default_prompt = f"""In order to respond to each question, follow these instructions: {file1_content} and bind your response to the current HCV guidelines contained in: {file2_content}"""

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": default_prompt}]

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #eef2f3, #8e9eab);
        padding: 2rem;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        margin-top: -3rem;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    h1 {
        color: #34495e;
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stButton > button {
        background-color: #27ae60;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1e8449;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        background-color: #f4f6f8;
    }
    .user-message {
        background-color: #d1ecf1;
        align-self: flex-end;
        border-left: 5px solid #007bff;
    }
    .bot-message {
        background-color: #eafaf1;
        align-self: flex-start;
        border-left: 5px solid #27ae60;
    }
    .stSidebar > div {
        padding: 1rem;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f8f9fa;
        color: #34495e;
        text-align: center;
        padding: 1rem;
        box-shadow: 0px -2px 4px rgba(0, 0, 0, 0.1);
        z-index: 1000;
    }
    .main-content {
        flex: 1;
        overflow-y: auto;
        padding-bottom: 100px; /* Space for the footer */
    }
    .footer-text {
        margin: 0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("HCV-GPT: Your AI Expert Assistant on Hepatitis C Virus")

# Sidebar for additional information or settings
with st.sidebar:
    st.markdown("## About HCV-GPT")
    st.info("**HCV-GPT**: Your AI-Powered Hepatitis C Specialist. Imagine having instant access to a cutting-edge AI assistant that's laser-focused on Hepatitis C virus (HCV) diagnosis and management. That's exactly what HCV-GPT delivers. This revolutionary tool harnesses the power of advanced language models and retrieval-augmented generation to provide you with expert-level guidance, all based on the latest gold-standard recommendations according to the 2020 Guidelines published by the European Association of The Study of The Liver (DOI: 10.1016/j.jhep.2020.08.018).")
    st.markdown("### 🪪 Personal Health Information:")
    st.markdown("Healthcare professionals and patients, please do not enter any personal health information (PHI) or patient data in this chat interface. Protect privacy and maintain confidentiality.")
    st.sidebar.markdown("### ⚠️ Disclaimer:")
    st.sidebar.markdown("This tool is intended for educational and research purposes only. If using this application in your research, please reference the following research article [to be added].")
    st.sidebar.markdown("### 🚀 Developed by HAIM Lab @ Yale School of Medicine")

# Main chat interface
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.markdown("## Chat with HCV-GPT")

# Display chat messages
for message in st.session_state.messages[1:]:  # Skip the system message
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑🏻‍⚕️"):
        st.markdown(f"<div class='chat-message {'user-message' if message['role'] == 'user' else 'bot-message'}'>{message['content']}</div>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask HCV-GPT a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑🏻‍⚕️"):
        st.markdown(f"<div class='chat-message user-message'>{prompt}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            max_tokens=1000,
            temperature=0.8,
            top_p=0.0
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(f"<div class='chat-message bot-message'>{full_response}</div>", unsafe_allow_html=True)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown("</div>", unsafe_allow_html=True)
