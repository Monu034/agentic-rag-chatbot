import streamlit as st
import os
from agents.mcp import MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_agent import LLMResponseAgent
from agents.coordinator import CoordinatorAgent
from vector_store.store import VectorStore

# Set up page config
st.set_page_config(page_title="Agentic RAG Chatbot", layout="wide", page_icon="🔮")

# Unique Custom CSS for Glassmorphism & Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e1e4a, #0a0a1a);
        color: #ffffff;
    }

    /* Top Banner Heading */
    .top-header {
        font-size: 1.2rem;
        font-weight: 600;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        opacity: 0.8;
    }
    
    /* Main Title Glass Card */
    .title-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
    }
    .main-title {
        background: linear-gradient(90deg, #ff69b4, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
    }

    /* Sidebar Section Headings */
    .sidebar-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.6);
        margin: 20px 0 10px 0;
        letter-spacing: 1px;
    }

    /* Document Cards */
    .doc-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .doc-icon {
        font-size: 1.5rem;
    }
    .doc-info {
        flex-grow: 1;
    }
    .doc-name {
        font-size: 0.9rem;
        font-weight: 400;
    }
    .doc-status {
        font-size: 0.7rem;
        color: #4CAF50;
    }

    /* Knowledge Cards */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin-top: 15px;
    }

    /* Chat Styling */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 15px;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Top Bar Heading
st.markdown('<div class="top-header">Agentic RAG Chatbot for Multi-Format Document QA using MCP</div>', unsafe_allow_html=True)

# Main Title Card
st.markdown("""
<div class="title-card">
    <div style="background: #1e1e4a; padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
        <img src="https://img.icons8.com/fluency/48/artificial-intelligence.png" width="30"/>
    </div>
    <h1 class="main-title">🔮 Agentic RAG Chatbot</h1>
    <div style="margin-left: auto; background: rgba(255,255,255,0.1); padding: 5px; border-radius: 8px;">
        <img src="https://img.icons8.com/material-outlined/24/ffffff/settings--v1.png" width="18"/>
    </div>
</div>
""", unsafe_allow_html=True)

# CACHE THE VECTOR STORE TO PREVENT WHITE SCREEN ON LOAD
@st.cache_resource(show_spinner="Initializing Vector Embeddings Engine...")
def load_vector_store():
    return VectorStore()

vector_store_instance = load_vector_store()

# Initialize global state if not present
if "coordinator" not in st.session_state:
    ingestion = IngestionAgent()
    retrieval = RetrievalAgent(vector_store_instance)
    llm = LLMResponseAgent()
    st.session_state.coordinator = CoordinatorAgent(ingestion, retrieval, llm)
    st.session_state.messages = []

# Sidebar for file uploads
with st.sidebar:
    st.markdown('<div class="sidebar-label">Document Upload</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload New Documents", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for f in uploaded_files:
            icon = "📄"
            if f.name.endswith(".pdf"): icon = "📕"
            elif f.name.endswith(".pptx"): icon = "📙"
            elif f.name.endswith(".docx"): icon = "📘"
            elif f.name.endswith(".csv"): icon = "📗"
            
            st.markdown(f"""
            <div class="doc-card">
                <span class="doc-icon">{icon}</span>
                <div class="doc-info">
                    <div class="doc-name">{f.name}</div>
                    <div class="doc-status">Ready to analyze</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🚀 Initialize Data Processing", use_container_width=True) and uploaded_files:
        # Process files...
        docs = []
        for f in uploaded_files:
            docs.append({"name": f.name, "bytes": f.read()})
            
        progress_bar = st.progress(0, text="Starting ingestion...")
        progress_bar.progress(25, text="Agents: Extracting text...")
        success, parsed_count, indexed_count = st.session_state.coordinator.process_documents(docs)
        
        if success:
            progress_bar.progress(100, text="Done!")
            st.success(f"Synchronized {indexed_count} chunks!")
            st.session_state.indexed_count = indexed_count
        else:
            progress_bar.empty()
            st.error("Failed to process documents.")

    # Sidebar Footer Sections
    st.markdown('<div class="sidebar-label">Vector Database</div>', unsafe_allow_html=True)
    db_status = "Ready" if "indexed_count" in st.session_state else "Empty"
    st.markdown(f'<div class="info-card">Status: <span style="color:#4CAF50">{db_status}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Knowledge Base</div>', unsafe_allow_html=True)
    count = st.session_state.get("indexed_count", 0)
    st.markdown(f'<div class="info-card">Count: <span style="color:#ff69b4">{count}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Project Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card" style="font-size:0.8rem">v1.2.0 - Agentic Mode</div>', unsafe_allow_html=True)


# Main chat area
st.markdown("### 💬 Multi-Agent Chat Interface")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("🔍 Inspect Deep Context"):
                for src in msg["sources"]:
                    st.caption(src)

user_query = st.chat_input("Ask a question about your documents...")

if user_query:
    # Display user query
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("Agents collaborating via MCP..."):
        # Delegate query handling to CoordinatorAgent
        response = st.session_state.coordinator.handle_query(user_query)
        
        if response["success"]:
            answer = response["answer"]
            sources = response["sources"]
            
            with st.chat_message("assistant"):
                st.write(answer)
                with st.expander("🔍 Inspect Deep Context"):
                    for src in sources:
                        st.caption(src)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })
        else:
            with st.chat_message("assistant"):
                st.write(response["answer"])

# MCP Logs Expander
st.markdown("---")
with st.expander("⚙️ View Internal MCP Communication Protocol (JSON)", expanded=False):
    st.markdown("*Real-time transmission logs between Ingestion, Retrieval, and LLM Agents.*")
    for log in reversed(st.session_state.coordinator.mcp_logs[-15:]):
        st.json(log)

