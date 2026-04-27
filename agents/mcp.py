import uuid
from typing import Any, Dict, Optional

class MCPMessage:
    def __init__(self, sender: str, receiver: str, msg_type: str, payload: Dict[str, Any], trace_id: Optional[str] = None):
        self.sender = sender
        self.receiver = receiver
        self.type = msg_type
        self.payload = payload
        self.trace_id = trace_id or str(uuid.uuid4())
        
    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            sender=data.get("sender"),
            receiver=data.get("receiver"),
            msg_type=data.get("type"),
            payload=data.get("payload", {}),
            trace_id=data.get("trace_id")
        )
