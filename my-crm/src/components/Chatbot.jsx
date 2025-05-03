import React, { useState } from 'react';
import axios from 'axios';

function Chatbot() {
  const [query, setQuery] = useState('');
  const [chatLog, setChatLog] = useState([
    { type: 'bot', text: 'Hi! How can I help you with your contacts?' }
  ]);
  const [loading, setLoading] = useState(false);

  const sendQuery = async () => {
    if (!query.trim()) return;

    const newChatLog = [...chatLog, { type: 'user', text: query }];
    setChatLog(newChatLog);
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/chat', { query });
      const botResponse = res.data.response;

      setChatLog([...newChatLog, { type: 'bot', text: botResponse }]);
    } catch (error) {
      console.error("Chatbot error:", error);
      setChatLog([...newChatLog, { type: 'bot', text: "⚠️ Something went wrong." }]);
    }

    setQuery('');
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendQuery();
  };

  return (
    <div>
      <div className="chat-window">
        {chatLog.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={query}
        placeholder="Type your question..."
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        className="search-input"
      />
      <button onClick={sendQuery} className="search-button" disabled={loading}>
        {loading ? '...' : 'Search'}
      </button>
    </div>
  );
}

export default Chatbot;