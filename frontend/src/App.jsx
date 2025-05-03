import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatBot from "./components/ChatBot";
import "./App.css";

function App() {
  const [uploadedContacts, setUploadedContacts] = useState([]);

  return (
    <div className="container">
      <header>
        <h1>My CRM</h1>
        <p>Event Contact Extractor</p>
      </header>
      <main className="main-grid">
        <div className="left-panel">
          <FileUpload onUploadComplete={setUploadedContacts} />
          <div className="uploaded">
            <h4>Uploaded Records</h4>
            {uploadedContacts.length === 0 ? (
              <p>No records to display</p>
            ) : (
              uploadedContacts.map((c, i) => (
                <p key={i}>
                  {c.name} – {c.company}
                </p>
              ))
            )}
          </div>
        </div>
        <div className="right-panel">
          <ChatBot />
        </div>
      </main>
    </div>
  );
}

export default App;