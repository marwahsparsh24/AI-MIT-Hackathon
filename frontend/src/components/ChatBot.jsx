import React, { useState } from "react";
import "./ChatBot.css";

const ChatBot = () => {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hi! Ask me about any contact or networking opportunity." }
  ]);s
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    // Show user message
    const newMessages = [...messages, { from: "user", text: input }];
    setMessages(newMessages);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input })
      });

      const data = await res.json();
      setMessages([...newMessages, { from: "bot", text: data.response }]);
    } catch (error) {
      setMessages([...newMessages, { from: "bot", text: "Sorry, something went wrong." }]);
    }

    setInput("");
  };

  return (
    <div className="card chatbot">
      <h3>Ask CRM Bot</h3>
      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.from}`}>{msg.text}</div>
        ))}
      </div>
      <div className="input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about contacts..."
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatBot;