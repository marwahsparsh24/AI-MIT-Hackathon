import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatBot from "./components/ChatBot";
import "./App.css";

function App() {
  const [uploadedContacts, setUploadedContacts] = useState([]);
  const [eventName, setEventName] = useState("");

  const handleUploadComplete = (contacts, event) => {
    setUploadedContacts(contacts);
    setEventName(event);
  };

  const handleSendRequest = async (contact) => {
    try {
      const res = await fetch("http://localhost:8000/connect_and_send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: contact.name,
          company: contact.company,
          event_name: eventName,
        }),
      });
      const data = await res.json();
      alert(data.status || "Done");
    } catch (err) {
      alert("❌ Failed to send request");
    }
  };

  return (
    <div className="container">
      <header>
        <h1>My CRM</h1>
        <p>Event Contact Extractor</p>
      </header>
      <main className="main-grid">
        <div className="left-panel">
          <FileUpload
            onUploadComplete={(contacts) =>
              handleUploadComplete(
                contacts,
                document.querySelector("input[type='text']").value
              )
            }
          />
          <div className="uploaded">
            <h4>Uploaded Records</h4>
            {uploadedContacts.length === 0 ? (
              <p>No records to display</p>
            ) : (
              uploadedContacts.map((c, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.8rem",
                  }}
                >
                  <span>
                    {c.name} – {c.company}
                  </span>
                  <button
                    onClick={() => handleSendRequest(c)}
                    title={`Send a request to ${c.name} from ${c.company} about ${eventName}`}
                  >
                    Send Request
                  </button>
                </div>
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