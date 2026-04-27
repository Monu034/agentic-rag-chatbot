import streamlit as st
import os
from agents.mcp import MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_agent import LLMResponseAgent
from agents.coordinator import CoordinatorAgent
from vector_store.store import VectorStore

# Set up page config
st.set_page_config(page_title="Nexus Agentic RAG", layout="wide", page_icon="🌌")

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
        font-size: 0.9rem;
        font-weight: 300;
        letter-spacing: 2px;
        color: var(--neon-cyan);
        text-transform: uppercase;
        border-bottom: 1px solid var(--glass-border);
        padding: 10px 0;
        margin-bottom: 30px;
        text-align: center;
        opacity: 0.8;
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
        background: rgba(5, 5, 15, 0.9) !important;
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
        transition: all 0.3s ease;
    }
    .nexus-file-tile:hover {
        background: rgba(0, 242, 255, 0.05);
        border-color: var(--neon-cyan);
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2);
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

    /* Glowing Agent Messages */
    [data-testid="stChatMessage"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 20px;
    }
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains("smart_toy")) {
        border-left: 4px solid var(--neon-magenta);
        box-shadow: -5px 0 20px rgba(255, 0, 255, 0.1);
    }
    
    /* UI Cleanup */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    
    /* Custom Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, var(--neon-cyan), #0088ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px var(--neon-cyan) !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT CONSTRUCTION ---

# Top Status Line
st.markdown('<div class="nexus-top-bar">NEXUS MULTI-AGENT PROTOCOL ACTIVE // ENCRYPTION ENABLED</div>', unsafe_allow_html=True)

# Floating Command Header
st.markdown("""
<div class="command-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: rgba(0,242,255,0.1); padding: 12px; border-radius: 20px; border: 1px solid var(--neon-cyan);">
            <img src="https://img.icons8.com/fluency/48/space-explorer.png" width="35"/>
        </div>
        <h1>Agentic RAG Chatbot</h1>
    </div>
    <div style="display: flex; gap: 15px;">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/settings.png" width="24" style="opacity:0.5"/>
        <img src="https://img.icons8.com/ios-filled/50/ffffff/menu.png" width="24" style="opacity:0.5"/>
    </div>
</div>
""", unsafe_allow_html=True)

# State & Agent Initializtion
@st.cache_resource(show_spinner="Syncing Neural Core...")
def init_core():
    return VectorStore()

core_store = init_core()

if "coordinator" not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent(IngestionAgent(), RetrievalAgent(core_store), LLMResponseAgent())
    st.session_state.messages = []

# --- INTELLIGENCE HUB (SIDEBAR) ---
with st.sidebar:
    st.markdown('<div class="hub-label">Data Ingestion Hub</div>', unsafe_allow_html=True)
    
    files = st.file_uploader(
        "Secure Upload", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if files:
        for f in files:
            ext = f.name.split('.')[-1].upper()
            st.markdown(f"""
            <div class="nexus-file-tile">
                <div class="tile-header">
                    <span style="color:var(--neon-cyan); font-weight:600;">[{ext}]</span>
                    <div class="file-name">{f.name}</div>
                </div>
                <div class="tile-status-bar"><div class="tile-status-fill"></div></div>
                <div style="font-size:0.6rem; color:var(--neon-cyan); text-align:right;">DATA SYNCED</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🚀 EXECUTE NEURAL SYNC", use_container_width=True) and files:
        docs = [{"name": f.name, "bytes": f.read()} for f in files]
        with st.status("Agents Collaborating...", expanded=True) as status:
            st.write("🌀 IngestionAgent: Decrypting structural layers...")
            success, _, count = st.session_state.coordinator.process_documents(docs)
            if success:
                st.session_state.indexed_count = count
                status.update(label="Sync Complete!", state="complete", expanded=False)
            else:
                status.update(label="Sync Failed", state="error")

    # Metrics Section
    st.markdown('<div class="hub-label">System Metrics</div>', unsafe_allow_html=True)
    
    # Vector DB Metric
    v_status = "ACTIVE" if "indexed_count" in st.session_state else "OFFLINE"
    v_color = "#00f2ff" if v_status == "ACTIVE" else "#ff3333"
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.1);">
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); margin-bottom:5px;">VECTOR ENGINE</div>
        <div style="font-size:1.1rem; color:{v_color}; font-weight:600;">{v_status}</div>
    </div>
    """, unsafe_allow_html=True)

    # Knowledge Metric
    k_count = st.session_state.get("indexed_count", 0)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.1); margin-top:15px;">
        <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); margin-bottom:5px;">KNOWLEDGE CHUNKS</div>
        <div style="font-size:1.1rem; color:var(--neon-magenta); font-weight:600;">{k_count}</div>
    </div>
    """, unsafe_allow_html=True)

    # Settings Info
    st.markdown('<div class="hub-label">System Specs</div>', unsafe_allow_html=True)
    st.caption("Protocol: MCP-v2")
    st.caption("Engine: Gemini-2.5-Flash")

# --- COLLABORATION HUB (CHAT) ---
st.markdown("### 💬 Neural Communication Interface")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("sources"):
            with st.expander("🔍 Trace Context Sources"):
                for s in m["sources"]:
                    st.caption(f"📍 {s}")

query = st.chat_input("Enter query for the Agentic Collective...")

if query:
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Agents orchestrating via MCP..."):
        resp = st.session_state.coordinator.handle_query(query)
        if resp["success"]:
            with st.chat_message("assistant"):
                st.write(resp["answer"])
                with st.expander("🔍 Trace Context Sources"):
                    for s in resp["sources"]:
                        st.caption(f"📍 {s}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": resp["answer"],
                "sources": resp["sources"]
            })
        else:
            st.error("Protocol Error: Unable to synthesize response.")

# --- MCP LOGS ---
st.markdown("---")
with st.expander("⚙️ VIEW NEURAL TRANSMISSION LOGS (MCP JSON)", expanded=False):
    for log in reversed(st.session_state.coordinator.mcp_logs[-10:]):
        st.json(log)
