from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ManualEntry(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    company: Optional[str]
    email: Optional[EmailStr] = None
    phone: Optional[str]
    source_file: Optional[str]
    event_name: Optional[str]
    misc_info: Optional[str] = ""
    comment: Optional[str] = ""

class FileUploadResponse(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    company: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    misc_info: Optional[str]
    source_file: str
    event_name: Optional[str]
    comment: Optional[str]