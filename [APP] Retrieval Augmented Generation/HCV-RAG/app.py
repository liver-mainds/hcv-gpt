import streamlit as st
from openai import OpenAI
import os
import numpy as np
import faiss
import pickle
from docx import Document

# --- CONFIGURAZIONE STREAMLIT ---
st.set_page_config(
    page_title="HCV-GPT",
    layout="wide",
    page_icon="🦠",
    initial_sidebar_state="expanded"
)

# --- CHIAVI E MODELLI ---
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "INSERT YOUR OPENAI API KEY HERE"
)
MODEL_NAME = "INSERT MODEL NAME HERE"
EMBEDDING_MODEL = "text-embedding-3-large"
client = OpenAI(api_key=OPENAI_API_KEY)

# --- FUNZIONI UTILI ---
def read_docx_content(filename):
    doc = Document(filename)
    return "\n".join(p.text for p in doc.paragraphs)

@st.cache_resource
def load_vector_dataset():
    base = os.path.dirname(os.path.abspath(__file__))
    vector_dir = os.path.join(base, "vector_data")
    index = faiss.read_index(os.path.join(vector_dir, "hcv_faiss_index.bin"))
    with open(os.path.join(vector_dir, "hcv_chunks.pkl"), "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def load_instructions():
    base = os.path.dirname(os.path.abspath(__file__))
    content = read_docx_content(os.path.join(base, "file1.docx"))
    return f"In order to respond to each question, follow these instructions:\n\n{content}"

def retrieve_best_chunk(query, index, chunks):
    resp = client.embeddings.create(input=query, model=EMBEDDING_MODEL)
    emb = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    _, I = index.search(emb, 1)
    return chunks[I[0][0]]

# --- CSS PERSONALIZZATO ---
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { padding: 0 !important; }
  .main { margin:1rem auto; max-width:900px; padding:2rem; }

  /* Header gradient shimmer behind text only */
  h1.subtle-header {
    font-size:2.5rem;
    font-weight:bold;
    text-align:center;
    background: linear-gradient(90deg, #1a73e8, #34A853, #1a73e8);
    background-size:200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite;
  }
  @keyframes shimmer {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
  }

  /* Chat header centered and dark grey */
  .chat-header {
    font-size:1.3rem;
    font-weight:600;
    margin-bottom:1rem;
    text-align:center;
    color:#333333;
  }

  /* Chat styling */
  [data-testid="stChatMessageContent"] { padding:0.5rem !important; }
  .st-chat-message [data-testid="stVerticalBlock"] {
    padding:0.75rem !important;
    margin-bottom:1rem !important;
    overflow-wrap:break-word !important;
    box-shadow:0 2px 10px rgba(0,0,0,0.05) !important;
  }
  .st-chat-message.user [data-testid="stVerticalBlock"] {
    background:#f0f5ff !important;
    border-radius:20px 20px 20px 4px !important;
    border-left:4px solid #1a73e8 !important;
  }
  .st-chat-message.assistant [data-testid="stVerticalBlock"] {
    background:#f0fff4 !important;
    border-radius:20px 20px 4px 20px !important;
    border-left:4px solid #34A853 !important;
  }
  [data-testid="stChatInput"] {
    background:white !important;
    border:1px solid #e0e0e0 !important;
    border-radius:10px !important;
    padding:0.5rem !important;
    box-shadow:0 2px 5px rgba(0,0,0,0.05) !important;
  }
  [data-testid="stChatInput"] > div { border:none !important; }

  /* Sidebar styling */
  [data-testid="stSidebar"] { background:#fff; border-right:1px solid rgba(0,0,0,0.1); }
  .system-status {
    display:flex;
    align-items:center;
    justify-content:center;
    background:#f8f9fa;
    padding:0.75rem;
    border-radius:8px;
    margin-bottom:1rem;
    border:1px solid rgba(0,0,0,0.05);
  }
  .feature-header {
    text-align:center;
    font-weight:bold;
    margin:1rem 0 0.5rem;
    color:#555;
  }
  .feature-card {
    display:flex;
    align-items:center;
    background:#fff;
    border:1px solid rgba(0,0,0,0.1);
    border-radius:8px;
    padding:0.8rem;
    margin-bottom:0.8rem;
    transition:transform 0.2s, box-shadow 0.2s;
  }
  .feature-card:hover {
    transform:translateY(-2px);
    box-shadow:0 4px 15px rgba(0,0,0,0.1);
  }
  .feature-card .emoji {
    margin-right:0.6rem;
    font-size:1.2rem;
  }
  .disclaimer {
    display:flex;
    align-items:center;
    background:#ffebee;
    color:#c62828;
    padding:0.75rem;
    border-left:4px solid #c62828;
    border-radius:8px;
    margin-top:1.2rem;
    margin-bottom:1.2rem;
  }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
with st.spinner("Initializing HCV-GPT…"):
    index, chunks = load_vector_dataset()
    default_prompt = load_instructions()
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"system","content":default_prompt}]

# --- SIDEBAR ---
with st.sidebar:
    # Banner HCV-GPT
    st.markdown("""
      <div style="text-align:center; margin-bottom:1rem;">
        <span style="
          font-size:2.2rem; font-weight:bold;
          background:linear-gradient(to right,#1a73e8,#34A853);
          -webkit-background-clip:text;
          -webkit-text-fill-color:transparent;
        ">HCV-GPT</span>
        <span style="
          background:rgba(52,168,83,0.1); color:#34A853;
          padding:0.2rem 0.6rem; border-radius:8px;
          font-size:0.8rem; vertical-align:middle; margin-left:0.3rem;
        ">RAG</span>
      </div>
    """, unsafe_allow_html=True)

    # System Online
    st.markdown("""
      <div class="system-status">
        <div style="
          height:10px; width:10px; background:#34A853;
          border-radius:50%; margin-right:8px;
          animation:pulse 2s infinite;
        "></div>
        <span style="font-weight:600; color:#333;">System Online</span>
      </div>
    """, unsafe_allow_html=True)

    # Info EASL
    st.markdown("""
      Hepatitis C Virus AI-Expert according to the 2020 medical guidelines by EASL:  
      <a href="https://doi.org/10.1016/j.jhep.2020.08.018">10.1016/j.jhep.2020.08.018</a>
    """, unsafe_allow_html=True)

    # Key Features
    st.markdown('<div class="feature-header">Key Features</div>', unsafe_allow_html=True)
    st.markdown("""
      <div class="feature-card"><span class="emoji">📖</span><strong>Evidence-Based Responses</strong></div>
      <div class="feature-card"><span class="emoji">🆕</span><strong>Latest Guidelines</strong></div>
      <div class="feature-card"><span class="emoji">🩺</span><strong>Diagnostic Assistance</strong></div>
      <div class="feature-card"><span class="emoji">💊</span><strong>Treatment Help</strong></div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
      <div class="disclaimer">
        <span style="font-size:1.2rem; margin-right:0.5rem;">⚠️</span>
        <span>This tool assists professionals and should not replace clinical judgment.</span>
      </div>
    """, unsafe_allow_html=True)

    # Developed by card
    st.markdown("""
      <div class="feature-card">
        <span class="emoji">🚀</span>
        <strong>Developed by <a href="https://www.humanplusaimed.com/" target="_blank">HAIM LAB</a> @ Yale School of Medicine</strong>
      </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown('<div class="main">', unsafe_allow_html=True)

# Header chat
st.markdown('<h1 class="subtle-header">HCV-GPT Assistant</h1>', unsafe_allow_html=True)
st.markdown('<div class="chat-header">Chat with HCV-GPT</div>', unsafe_allow_html=True)

# Chat history
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👨‍⚕️"):
        st.write(msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

# Input
user_query = st.chat_input("Type your message…")

# Process input
if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    with st.chat_message("user", avatar="👨‍⚕️"):
        st.write(user_query)
    with st.spinner("Generating response…"):
        chunk = retrieve_best_chunk(user_query, index, chunks)
        prompt = default_prompt + "\n\nCurrent Guidelines: " + chunk + "\n\nUser Query: " + user_query
        with st.chat_message("assistant", avatar="🤖"):
            full_response = ""
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role":"system","content":prompt},{"role":"user","content":user_query}],
                stream=True,
                max_tokens=1000,
                temperature=0.8,
                top_p=0.5
            )
            placeholder = st.empty()
            for c in stream:
                if c.choices[0].delta.content:
                    full_response += c.choices[0].delta.content
                    placeholder.markdown(full_response)
        st.session_state.messages.append({"role":"assistant","content":full_response})
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # Close main

