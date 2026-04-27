from typing import List, Dict
from agents.mcp import MCPMessage
from utils.document_parser import parse_document

class IngestionAgent:
    def __init__(self):
        self.name = "IngestionAgent"
        self.chunk_size = 500
        self.chunk_overlap = 50

    def chunk_text(self, text: str, source: str) -> List[Dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "source": source
            })
            if i + self.chunk_size >= len(words):
                break
        return chunks

    def process_message(self, message: MCPMessage) -> MCPMessage:
        if message.type == "PARSE_DOCUMENTS":
            documents = message.payload.get("documents", []) # list of dict with name and bytes
            all_chunks = []
            for doc in documents:
                text = parse_document(doc["name"], doc["bytes"])
                if text.strip():
                    chunks = self.chunk_text(text, doc["name"])
                    all_chunks.extend(chunks)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                msg_type="DOCUMENTS_PARSED",
                payload={"chunks": all_chunks},
                trace_id=message.trace_id
            )
        return MCPMessage(
            sender=self.name,
            receiver=message.sender,
            msg_type="ERROR",
            payload={"error": f"Unknown message type {message.type}"},
            trace_id=message.trace_id
        )
