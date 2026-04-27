from agents.mcp import MCPMessage

class CoordinatorAgent:
    """
    The Orchestrator that manages the full workflow between agents using MCP-style structured messages.
    """
    def __init__(self, ingestion_agent, retrieval_agent, llm_agent):
        self.name = "CoordinatorAgent"
        self.ingestion_agent = ingestion_agent
        self.retrieval_agent = retrieval_agent
        self.llm_agent = llm_agent
        self.mcp_logs = []

    def log_mcp(self, msg: MCPMessage):
        """Keep a running log of all inter-agent communication."""
        self.mcp_logs.append(msg.to_dict())

    def process_documents(self, documents: list) -> tuple[bool, int, int]:
        """
        Orchestrates the document ingestion and indexing pipeline.
        Returns: (success_boolean, chunks_parsed, chunks_indexed)
        """
        # Step 1: Send PARSE_DOCUMENTS to IngestionAgent
        req_msg = MCPMessage(
            sender=self.name,
            receiver=self.ingestion_agent.name,
            msg_type="PARSE_DOCUMENTS",
            payload={"documents": documents}
        )
        self.log_mcp(req_msg)
        
        resp_msg = self.ingestion_agent.process_message(req_msg)
        self.log_mcp(resp_msg)
        
        if resp_msg.type == "DOCUMENTS_PARSED":
            chunks = resp_msg.payload.get("chunks", [])
            
            # Step 2: Send INDEX_CHUNKS to RetrievalAgent
            index_req = MCPMessage(
                sender=self.name,
                receiver=self.retrieval_agent.name,
                msg_type="INDEX_CHUNKS",
                payload={"chunks": chunks},
                trace_id=resp_msg.trace_id
            )
            self.log_mcp(index_req)
            
            index_resp = self.retrieval_agent.process_message(index_req)
            self.log_mcp(index_resp)
            
            if index_resp.type == "CHUNKS_INDEXED":
                return True, len(chunks), index_resp.payload.get("count", 0)
                
        return False, 0, 0

    def handle_query(self, query: str) -> dict:
        """
        Orchestrates the retrieval and generation pipeline.
        Returns a dictionary with 'success', 'answer', and 'sources'.
        """
        # Step 3: Send RETRIEVE_CONTEXT to RetrievalAgent
        retrieval_req = MCPMessage(
            sender=self.name,
            receiver=self.retrieval_agent.name,
            msg_type="RETRIEVE_CONTEXT",
            payload={"query": query, "top_k": 5}
        )
        self.log_mcp(retrieval_req)
        
        retrieval_resp = self.retrieval_agent.process_message(retrieval_req)
        self.log_mcp(retrieval_resp)
        
        if retrieval_resp.type == "RETRIEVAL_RESULT":
            # Step 4: Send the retrieved context to the LLMAgent
            llm_resp = self.llm_agent.process_message(retrieval_resp)
            self.log_mcp(llm_resp)
            
            if llm_resp.type == "FINAL_RESPONSE":
                return {
                    "success": True,
                    "answer": llm_resp.payload.get("answer", "No answer generated."),
                    "sources": llm_resp.payload.get("sources", [])
                }
                
        return {"success": False, "answer": "Matrix failure: Error generating response.", "sources": []}
