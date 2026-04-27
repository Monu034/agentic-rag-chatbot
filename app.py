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

# Pixel-Perfect CSS for Premium Glassmorphism
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

    /* Top Horizontal Header */
    .header-bar {
        font-size: 1.4rem;
        font-weight: 600;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Premium Title Card (Pill Shape) */
    .title-pill {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 30px;
        padding: 18px 40px;
        display: flex;
        align-items: center;
        gap: 25px;
        margin-bottom: 40px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    .title-pill h1 {
        background: linear-gradient(90deg, #ff69b4, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 600;
        margin: 0;
    }

    /* Sidebar Section Headings */
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.5);
        margin: 30px 0 15px 0;
        letter-spacing: 2px;
    }

    /* Individual File Cards (Manual Construction) */
    .file-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        transition: transform 0.2s ease;
    }
    .file-card:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.12);
    }
    .file-card-top {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .file-name {
        font-size: 0.9rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 180px;
    }
    .progress-track {
        width: 100%;
        height: 5px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        width: 100%;
    }
    .analyzed-badge {
        font-size: 0.7rem;
        color: #4CAF50;
        text-align: right;
        font-weight: 600;
        margin-top: -5px;
    }

    /* Info Stats Cards */
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .stat-label {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00d2ff;
    }

    /* Chat Styling Enhancements */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Clean Page */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1.5rem !important; }
    
    /* Uploader Styling */
    .stFileUploader section {
        background: rgba(255,255,255,0.05) !important;
        border: 2px dashed rgba(255,255,255,0.2) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Top Header Bar
st.markdown('<div class="header-bar">Agentic RAG Chatbot for Multi-Format Document QA using MCP</div>', unsafe_allow_html=True)

# 2. Premium Pill Title
st.markdown("""
<div class="title-pill">
    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 18px;">
        <img src="https://img.icons8.com/fluency/48/artificial-intelligence.png" width="32"/>
    </div>
    <h1>🔮 Agentic RAG Chatbot</h1>
    <div style="margin-left: auto; opacity: 0.6;">
        <img src="https://img.icons8.com/material-rounded/24/ffffff/settings.png" width="24"/>
    </div>
</div>
""", unsafe_allow_html=True)

# Vector Store Logic
@st.cache_resource(show_spinner="Initializing Vector Engine...")
def load_vector_store():
    return VectorStore()

vector_store_instance = load_vector_store()

if "coordinator" not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent(IngestionAgent(), RetrievalAgent(vector_store_instance), LLMResponseAgent())
    st.session_state.messages = []

# 3. Sidebar (Document Intelligence Hub)
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">Document Upload</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drop files here", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for f in uploaded_files:
            # Match icon to file type
            icon_url = "https://img.icons8.com/color/48/pdf.png"
            if f.name.endswith(".pptx"): icon_url = "https://img.icons8.com/color/48/microsoft-powerpoint.png"
            elif f.name.endswith(".docx"): icon_url = "https://img.icons8.com/color/48/microsoft-word.png"
            elif f.name.endswith(".csv"): icon_url = "https://img.icons8.com/color/48/csv.png"
            elif f.name.endswith(".txt"): icon_url = "https://img.icons8.com/color/48/txt-file.png"
            
            st.markdown(f"""
            <div class="file-card">
                <div class="file-card-top">
                    <img src="{icon_url}" width="26"/>
                    <div class="file-name">{f.name}</div>
                </div>
                <div class="progress-track"><div class="progress-fill"></div></div>
                <div class="analyzed-badge">Analyzed</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🚀 Initialize Agents & Sync Data", use_container_width=True) and uploaded_files:
        docs = [{"name": f.name, "bytes": f.read()} for f in uploaded_files]
        
        with st.status("Agentic Orchestration in Progress...", expanded=True) as status:
            st.write("IngestionAgent: Extracting structural data...")
            success, parsed_count, indexed_count = st.session_state.coordinator.process_documents(docs)
            if success:
                st.write("RetrievalAgent: Syncing vector embeddings...")
                st.session_state.indexed_count = indexed_count
                status.update(label="System Ready!", state="complete", expanded=False)
            else:
                status.update(label="Critical System Failure", state="error")

    # Sidebar Stats
    st.markdown('<div class="sidebar-section-title">Vector Database</div>', unsafe_allow_html=True)
    db_status = "Ready" if "indexed_count" in st.session_state else "Empty"
    st.markdown(f'<div class="stat-box"><div class="stat-label">Status</div><div class="stat-value" style="color:#4CAF50">{db_status}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Knowledge Base</div>', unsafe_allow_html=True)
    count = st.session_state.get("indexed_count", 0)
    st.markdown(f'<div class="stat-box"><div class="stat-label">Total Knowledge Chunks</div><div class="stat-value">{count}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">System Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-box"><div class="stat-label">Current Version</div><div class="stat-value" style="font-size:0.9rem">v1.3.0 - High Speed</div></div>', unsafe_allow_html=True)

# 4. Main Chat Interface
st.markdown("### 💬 Agentic Collaboration Hub")

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 Inspect Deep Context"):
                for src in msg["sources"]:
                    st.caption(src)

# Query Input
user_query = st.chat_input("Ask about your documents...")

if user_query:
    st.chat_message("user").write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.spinner("Agents collaborating via MCP..."):
        response = st.session_state.coordinator.handle_query(user_query)
        
        if response["success"]:
            with st.chat_message("assistant"):
                st.write(response["answer"])
                with st.expander("🔍 Inspect Deep Context"):
                    for src in response["sources"]:
                        st.caption(src)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["answer"],
                "sources": response["sources"]
            })
        else:
            st.chat_message("assistant").write("Matrix error: Could not synthesize response.")

# 5. MCP JSON Trace Expander
st.markdown("---")
with st.expander("⚙️ Internal Agentic Transmission Logs (MCP JSON)", expanded=False):
    for log in reversed(st.session_state.coordinator.mcp_logs[-15:]):
        st.json(log)
