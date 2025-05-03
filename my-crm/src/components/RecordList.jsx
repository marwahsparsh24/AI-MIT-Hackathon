import React from 'react';

function RecordList({ records }) {
  return (
    <div>
      <h3>Uploaded Records</h3>
      {records.length === 0 && <p>No records to display</p>}
      <ul>
        {records.map((rec, idx) => (
          <li key={idx}>
            <strong>{rec.name || 'N/A'}</strong> - {rec.company || 'N/A'}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RecordList;