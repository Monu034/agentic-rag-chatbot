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
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Dynamic animated background */
    .stApp {
        background: linear-gradient(-45deg, #0a0a2a, #1a1a4b, #2a0a2a, #0a1a2a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Glassmorphism Chat Inputs & Containers */
    .stChatInputContainer {
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
    }
    
    /* Styled Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #ff00cc, #3333ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    /* Agent Message Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* User Message Bubbles */
    [data-testid="stChatMessage"]:has([data-testid="stIconMaterial"]:contains("person")) {
        background: rgba(51, 51, 255, 0.1);
        border: 1px solid rgba(51, 51, 255, 0.3);
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔮 Agentic RAG Chatbot")
st.markdown("*A next-generation Multi-Format QA system powered by Model Context Protocol.*")

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
    st.markdown("### 📥 Document Ingestion")
    uploaded_files = st.file_uploader(
        "Upload Datasets (PDF, PPTX, CSV, DOCX, TXT)", 
        type=["pdf", "pptx", "csv", "docx", "txt", "md"], 
        accept_multiple_files=True
    )
    
    if st.button("Initialize Data Processing", use_container_width=True) and uploaded_files:
        with st.spinner("Extracting Document Text..."):
            docs = []
            for f in uploaded_files:
                docs.append({
                    "name": f.name,
                    "bytes": f.read()
                })
            
            # Delegate entirely to CoordinatorAgent with a progress bar
            progress_bar = st.progress(0, text="Starting ingestion...")
            
            # Step 1: Parsing
            progress_bar.progress(25, text="Agents: Extracting text from documents...")
            success, parsed_count, indexed_count = st.session_state.coordinator.process_documents(docs)
            
            if success:
                progress_bar.progress(75, text="Agents: Creating vector embeddings...")
                progress_bar.progress(100, text="Done!")
                st.info(f"✨ Parsed {parsed_count} structural components.")
                st.success(f"🚀 Vector Store synchronized with {indexed_count} chunks!")
            else:
                progress_bar.empty()
                st.error("Matrix failure: Document processing rejected.")

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

