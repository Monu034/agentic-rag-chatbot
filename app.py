import streamlit as st
import os
from agents.mcp import MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_agent import LLMResponseAgent
from agents.coordinator import CoordinatorAgent
from vector_store.store import VectorStore

# Set up page config
st.set_page_config(
    page_title="Agentic RAG Intelligence", 
    layout="wide", 
    page_icon="🔮"
)

# --- ADVANCED GLASSMORPHISM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@300;600&display=swap');
    
    :root {
        --neon-cyan: #00f2ff;
        --neon-magenta: #ff00ff;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e1e4a, #050510);
        color: #ffffff;
    }

    /* Professional Banner */
    .prof-banner {
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 1px;
        color: rgba(255, 255, 255, 0.8);
        border-bottom: 1px solid var(--glass-border);
        padding: 15px 0;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* Main Title Pill */
    .title-pill {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 50px;
        padding: 15px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 40px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .title-pill h1 {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #00d2ff, #ff69b4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 600;
        margin: 0;
    }

    /* Main Area Containers */
    .main-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 30px;
    }
    
    .section-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--neon-cyan);
        margin-bottom: 15px;
        letter-spacing: 2px;
    }

    /* File Tiles */
    .file-tile {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    /* Clean UI */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 1. Professional Banner
st.markdown('<div class="prof-banner">Agentic Intelligence Platform: Advanced RAG with MCP Orchestration</div>', unsafe_allow_html=True)

# 2. Main Title
st.markdown("""
<div class="title-pill">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 15px;">
            <img src="https://img.icons8.com/fluency/48/artificial-intelligence.png" width="30"/>
        </div>
        <h1>Agentic RAG Chatbot</h1>
    </div>
    <div style="opacity: 0.5;">
        <img src="https://img.icons8.com/material-rounded/24/ffffff/settings.png" width="22"/>
    </div>
</div>
""", unsafe_allow_html=True)

# Core Logic
@st.cache_resource(show_spinner="Syncing Knowledge Core...")
def init_core():
    return VectorStore()

core_store = init_core()

if "coordinator" not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent(IngestionAgent(), RetrievalAgent(core_store), LLMResponseAgent())
    st.session_state.messages = []

# --- 3. MAIN UPLOAD SECTION (MOVING OUT OF SIDEBAR FOR VISIBILITY) ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">📥 Document Intelligence Hub</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    files = st.file_uploader(
        "Drop documents here (PDF, PPTX, CSV, DOCX, TXT)", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

with col2:
    if st.button("🚀 Initialize Sync", use_container_width=True):
        if files:
            docs = [{"name": f.name, "bytes": f.read()} for f in files]
            with st.status("Agents Collaborating...", expanded=False) as status:
                success, _, count = st.session_state.coordinator.process_documents(docs)
                if success:
                    st.session_state.indexed_count = indexed_count = count
                    status.update(label="System Synchronized!", state="complete")
                else:
                    status.update(label="Sync Failed", state="error")
        else:
            st.warning("Please upload files first.")

if files:
    file_cols = st.columns(len(files) if len(files) < 4 else 4)
    for idx, f in enumerate(files):
        with file_cols[idx % 4]:
            st.markdown(f"""
            <div class="file-tile">
                <img src="https://img.icons8.com/color/48/file.png" width="20"/>
                <div style="font-size:0.8rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{f.name}</div>
            </div>
            """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CHAT AREA ---
st.markdown('<div class="section-label">💬 Neural Collaboration Hub</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

query = st.chat_input("Enter your query for the Agentic Collective...")

if query:
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Agents coordinating via MCP..."):
        resp = st.session_state.coordinator.handle_query(query)
        if resp["success"]:
            with st.chat_message("assistant"):
                st.write(resp["answer"])
                with st.expander("🔍 Source Context"):
                    for s in resp["sources"]:
                        st.caption(s)
            st.session_state.messages.append({"role": "assistant", "content": resp["answer"], "sources": resp["sources"]})
        else:
            st.error("Agent error.")

# --- 5. STATS & LOGS ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Vector Database", "ACTIVE" if "indexed_count" in st.session_state else "OFFLINE")
with c2:
    st.metric("Knowledge Chunks", st.session_state.get("indexed_count", 0))
with c3:
    st.metric("Agent Status", "COORDINATING")

with st.expander("⚙️ View Internal MCP Transmission Logs (JSON)"):
    for log in reversed(st.session_state.coordinator.mcp_logs[-10:]):
        st.json(log)
