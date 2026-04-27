import os
import google.generativeai as genai
from agents.mcp import MCPMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

class LLMResponseAgent:
    def __init__(self):
        self.name = "LLMResponseAgent"
        if API_KEY:
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    def generate_response(self, query: str, context_list: list) -> str:
        if not self.model:
            return "Error: Gemini API key not configured. Please add GEMINI_API_KEY to your .env file."
        
        if not context_list:
            return "I cannot answer this based on the provided documents as no relevant context was found."

        context_str = "\n\n".join(context_list)
        prompt = f"""You are a helpful AI assistant answering questions based solely on the provided context.
        
Context:
{context_str}

User Question: {query}

Answer the question based only on the above context. If the answer is not in the context, say "I cannot answer this based on the provided documents."
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

    def process_message(self, message: MCPMessage) -> MCPMessage:
        if message.type == "RETRIEVAL_RESULT":
            context = message.payload.get("retrieved_context", [])
            query = message.payload.get("query", "")
            
            answer = self.generate_response(query, context)
            
            return MCPMessage(
                sender=self.name,
                receiver=message.sender,
                msg_type="FINAL_RESPONSE",
                payload={
                    "answer": answer,
                    "sources": context
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
