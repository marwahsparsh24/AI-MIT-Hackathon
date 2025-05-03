import React from 'react';

function EventViewer({ records }) {
  const events = [...new Set(records.map(r => r.event_name || "Untitled Event"))];

  return (
    <div style={{ maxWidth: '500px', margin: '2rem auto' }}>
      <h3>Events Uploaded</h3>
      <ul>
        {events.length === 0 ? (
          <li>No events yet.</li>
        ) : (
          events.map((e, idx) => <li key={idx}>{e}</li>)
        )}
      </ul>
    </div>
  );
}

export default EventViewer;