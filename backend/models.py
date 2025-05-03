from pydantic import BaseModel
from typing import Optional

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