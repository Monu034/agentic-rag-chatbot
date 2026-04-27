import streamlit as st
import os
from agents.mcp import MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_agent import LLMResponseAgent
from agents.coordinator import CoordinatorAgent
from vector_store.store import VectorStore

# Set up page config - ENSURE SIDEBAR IS ALWAYS OPEN
st.set_page_config(
    page_title="Agentic RAG Chatbot", 
    layout="wide", 
    page_icon="🔮",
    initial_sidebar_state="expanded"
)

# --- UNIQUE CYBER-SPACE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&family=Outfit:wght@300;600&display=swap');
    
    :root {
        --neon-cyan: #00f2ff;
        --neon-magenta: #ff00ff;
        --glass-bg: rgba(10, 10, 30, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Immersive Deep Space Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a1a4b 0%, #050510 100%);
        color: #ffffff;
    }

    /* Top Horizontal Status Bar */
    .nexus-top-bar {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 30px;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Floating Command Header */
    .command-header {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 50px;
        padding: 15px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 40px;
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.1);
    }
    .command-header h1 {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 600;
        margin: 0;
    }

    /* Sidebar Intelligence Hub */
    [data-testid="stSidebar"] {
        background: rgba(5, 5, 15, 0.95) !important;
        border-right: 1px solid var(--glass-border);
    }
    .hub-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--neon-magenta);
        text-transform: uppercase;
        margin: 30px 0 15px 0;
        letter-spacing: 3px;
        border-left: 3px solid var(--neon-magenta);
        padding-left: 10px;
    }

    /* Futuristic File Tiles */
    .nexus-file-tile {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-border);
        border-left: 4px solid var(--neon-cyan);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .tile-header {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    .tile-status-bar {
        height: 3px;
        background: rgba(255,255,255,0.1);
        border-radius: 2px;
    }
    .tile-status-fill {
        height: 100%;
        background: var(--neon-cyan);
        width: 100%;
        box-shadow: 0 0 10px var(--neon-cyan);
    }

    /* UI Cleanup */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    
    .stButton>button {
        background: linear-gradient(90deg, var(--neon-cyan), #0088ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT CONSTRUCTION ---

# Top Status Line - REVERTED TO REQUESTED HEADING
st.markdown('<div class="nexus-top-bar">Agentic RAG Chatbot for Multi-Format Document QA using MCP</div>', unsafe_allow_html=True)

# Floating Command Header - REVERTED TO REQUESTED TITLE
st.markdown("""
<div class="command-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: rgba(0,242,255,0.1); padding: 12px; border-radius: 20px; border: 1px solid var(--neon-cyan);">
            <img src="https://img.icons8.com/fluency/48/artificial-intelligence.png" width="35"/>
        </div>
        <h1>Agentic RAG Chatbot</h1>
    </div>
    <div style="display: flex; gap: 15px; align-items: center;">
        <img src="https://img.icons8.com/material-rounded/24/ffffff/settings.png" width="22" style="opacity:0.6"/>
        <div style="width: 1px; height: 20px; background: rgba(255,255,255,0.1);"></div>
        <img src="https://img.icons8.com/material-rounded/24/ffffff/menu.png" width="22" style="opacity:0.6"/>
    </div>
</div>
""", unsafe_allow_html=True)

# Core Logic
@st.cache_resource(show_spinner="Syncing Agents...")
def init_core():
    return VectorStore()

core_store = init_core()

if "coordinator" not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent(IngestionAgent(), RetrievalAgent(core_store), LLMResponseAgent())
    st.session_state.messages = []

# --- INTELLIGENCE HUB (SIDEBAR) ---
# NOTE: Sidebar is where the UPLOAD option is located.
with st.sidebar:
    st.markdown('<div class="hub-label">DOCUMENT UPLOAD</div>', unsafe_allow_html=True)
    
    files = st.file_uploader(
        "Upload files", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if files:
        for f in files:
            icon_url = "https://img.icons8.com/color/48/pdf.png"
            if f.name.endswith(".pptx"): icon_url = "https://img.icons8.com/color/48/microsoft-powerpoint.png"
            elif f.name.endswith(".docx"): icon_url = "https://img.icons8.com/color/48/microsoft-word.png"
            elif f.name.endswith(".csv"): icon_url = "https://img.icons8.com/color/48/csv.png"
            
            st.markdown(f"""
            <div class="nexus-file-tile">
                <div class="tile-header">
                    <img src="{icon_url}" width="20"/>
                    <div class="file-name">{f.name}</div>
                </div>
                <div class="tile-status-bar"><div class="tile-status-fill"></div></div>
                <div style="font-size:0.65rem; color:#4CAF50; text-align:right; font-weight:600;">ANALYZED</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🚀 INITIALIZE AGENTIC SYNC", use_container_width=True) and files:
        docs = [{"name": f.name, "bytes": f.read()} for f in files]
        with st.status("Agents collaborating...", expanded=True) as status:
            success, _, count = st.session_state.coordinator.process_documents(docs)
            if success:
                st.session_state.indexed_count = count
                status.update(label="Sync Complete!", state="complete", expanded=False)
            else:
                status.update(label="Sync Failed", state="error")

    # Metrics Section
    st.markdown('<div class="hub-label">VECTOR DATABASE</div>', unsafe_allow_html=True)
    v_status = "READY" if "indexed_count" in st.session_state else "EMPTY"
    v_color = "#4CAF50" if v_status == "READY" else "#ff3333"
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.1);">
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); margin-bottom:5px;">STATUS</div>
        <div style="font-size:1.1rem; color:{v_color}; font-weight:600;">{v_status}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hub-label">KNOWLEDGE BASE</div>', unsafe_allow_html=True)
    k_count = st.session_state.get("indexed_count", 0)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.1);">
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); margin-bottom:5px;">CHUNKS INDEXED</div>
        <div style="font-size:1.1rem; color:var(--neon-magenta); font-weight:600;">{k_count}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hub-label">PROJECT SETTINGS</div>', unsafe_allow_html=True)
    st.caption("Agentic-RAG v1.4.0")

# --- MAIN CHAT AREA ---
st.markdown("### 💬 Neural Collaboration Hub")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("sources"):
            with st.expander("🔍 Inspect Source Context"):
                for s in m["sources"]:
                    st.caption(s)

query = st.chat_input("Enter your query...")

if query:
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Agents coordinating via MCP..."):
        resp = st.session_state.coordinator.handle_query(query)
        if resp["success"]:
            with st.chat_message("assistant"):
                st.write(resp["answer"])
                with st.expander("🔍 Inspect Source Context"):
                    for s in resp["sources"]:
                        st.caption(s)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": resp["answer"],
                "sources": resp["sources"]
            })
        else:
            st.error("Error: Agent synchronization failure.")

# --- MCP LOGS ---
st.markdown("---")
with st.expander("⚙️ View Internal MCP Communication Logs (JSON)", expanded=False):
    for log in reversed(st.session_state.coordinator.mcp_logs[-15:]):
        st.json(log)
