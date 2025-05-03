import React, { useState } from "react";
import axios from "axios";
import "./FileUpload.css";

const FileUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [eventName, setEventName] = useState("");

  const handleSubmit = async () => {
    if (!file || !eventName) return alert("Please enter event name and file.");
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const res = await axios.post("http://localhost:8000/upload_and_extract", formData);
      onUploadComplete(res.data.contacts, eventName);
    } catch (err) {
      console.error(err.response?.data || err.message);  // ✅ better logging
      alert("Upload failed.");
    }
  };  

  return (
    <div className="card">
      <h3>Create New Event</h3>
      <input
        type="text"
        placeholder="Event Name"
        value={eventName}
        onChange={(e) => setEventName(e.target.value)}
      />
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default FileUpload;