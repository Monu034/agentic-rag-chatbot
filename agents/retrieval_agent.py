from agents.mcp import MCPMessage
from vector_store.store import VectorStore

class RetrievalAgent:
    def __init__(self, vector_store: VectorStore):
        self.name = "RetrievalAgent"
        self.vector_store = vector_store

    def process_message(self, message: MCPMessage) -> MCPMessage:
        if message.type == "INDEX_CHUNKS":
            chunks = message.payload.get("chunks", [])
            self.vector_store.add_chunks(chunks)
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                msg_type="CHUNKS_INDEXED",
                payload={"status": "success", "count": len(chunks)},
                trace_id=message.trace_id
            )
        
        elif message.type == "RETRIEVE_CONTEXT":
            query = message.payload.get("query", "")
            top_k = message.payload.get("top_k", 3)
            results = self.vector_store.search(query, top_k)
            
            context = [f"[Source: {res['source']}] {res['text']}" for res in results]
            
            return MCPMessage(
                sender=self.name,
                receiver="LLMResponseAgent", 
                msg_type="RETRIEVAL_RESULT",
                payload={
                    "retrieved_context": context,
                    "query": query
                },
                trace_id=message.trace_id
            )
            
        return MCPMessage(
            sender=self.name,
            receiver=message.sender,
            msg_type="ERROR",
            payload={"error": f"Unknown message type {message.type}"},
            trace_id=message.trace_id
        )
