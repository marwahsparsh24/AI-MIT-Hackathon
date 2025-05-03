import React, { useState } from 'react';
import axios from 'axios';

function SearchPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/search?q=${query}`);
      setResults(res.data || []);
    } catch (err) {
      console.error('Search failed', err);
    }
  };

  return (
    <div className="search-panel">
      <h2>Search Contacts</h2>
      <input
        type="text"
        placeholder="Search by name, company, etc."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>

      {results.length > 0 && (
        <table className="results-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Company</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {results.map((rec, i) => (
              <tr key={i}>
                <td>{rec.name || 'N/A'}</td>
                <td>{rec.company || 'N/A'}</td>
                <td>{rec.designation || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default SearchPanel;