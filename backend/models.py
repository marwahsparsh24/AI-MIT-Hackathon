from pydantic import BaseModel

class MessageRequest(BaseModel):
    recipient_name: str
    recipient_company: str
    sender_name: str
    context: str

class SearchRequest(BaseModel):
    name: str
    company: str
    max_results: int = 5