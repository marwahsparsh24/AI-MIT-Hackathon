from pydantic import BaseModel

<<<<<<< HEAD
class ManualEntry(BaseModel):
    name: Optional[str]
    company: Optional[str]
    event_name: Optional[str]
    source_file: Optional[str]

class FileUploadResponse(BaseModel):
    name: Optional[str]
    company: Optional[str]
    event_name: Optional[str]
    source_file: str
=======
class MessageRequest(BaseModel):
    recipient_name: str
    recipient_company: str
    sender_name: str
    context: str

class SearchRequest(BaseModel):
    name: str
    company: str
    max_results: int = 5
>>>>>>> origin/Sparsh
