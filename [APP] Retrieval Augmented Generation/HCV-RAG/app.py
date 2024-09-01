import streamlit as st
import openai
import os
from docx import Document

# Set page configuration
st.set_page_config(page_title="HCV-GPT", layout="wide")

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
        background: #f0f2f6;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #f8f9fa;
    }
    .stButton > button {
        background-color: #3498db;
        color: #ffffff;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #f8f9fa;
        align-self: flex-end;
    }
    .bot-message {
        background-color: #e1f5fe;
        align-self: flex-start;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("HCV-GPT: Your AI Expert Assistant on Hepatitis C Virus")

# Sidebar for additional information or settings
with st.sidebar:
    st.markdown("## About HCV-GPT")
    st.info("HCV-GPT: Your AI-Powered Hepatitis C Specialist. Imagine having instant access to a cutting-edge AI assistant that's laser-focused on Hepatitis C virus (HCV) diagnosis and management. That's exactly what HCV-GPT delivers. This revolutionary tool harnesses the power of advanced language models and retrieval augmented generation to provide you with expert-level guidance, all based on the latest gold-standard recommendations according to the 2020 Guidelines published by the European Association of The Study of The Liver (DOI: 10.1016/j.jhep.2020.08.018).")
    st.markdown("### How to use:")
    st.markdown("1. Type your question in the chat input")
    st.markdown("2. Press Enter or click 'Send'")
    st.markdown("3. Be careful not to input any personal health information!")
    st.markdown("### Disclaimer:")
    st.markdown("If using this application in your research, reference to tobeadded")

# Main chat interface
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

# Footer
st.markdown("---")
st.markdown("Developed by HAIM Lab @ Yale School of Medicine")