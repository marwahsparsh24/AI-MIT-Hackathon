from pydantic import BaseModel

class MessageRequest(BaseModel):
    recipient_name: str
    recipient_company: str
    sender_name: str
    context: str

class SearchRequest(BaseModel):
    name: str
    company: str
    sender_name: str
    context: str
    max_results: int = 5

class SendRequest(BaseModel):
    profile_url: str
    message: str
