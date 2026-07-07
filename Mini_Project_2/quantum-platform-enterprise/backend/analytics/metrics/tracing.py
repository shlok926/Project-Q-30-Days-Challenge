import uuid
from typing import Optional

class TraceContext:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        
    def get_context(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }

def start_span(name: str, context: Optional[TraceContext] = None):
    pass
