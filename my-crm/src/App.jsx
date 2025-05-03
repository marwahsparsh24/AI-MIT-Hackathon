import React, { useState } from 'react';
import EventForm from './components/EventForm';
import RecordList from './components/RecordList';
import { ToastContainer } from 'react-toastify';
import './App.css';

function App() {
  const [records, setRecords] = useState([]);

  return (
    <div>
      <div className="navbar">
        <h1>My CRM</h1>
        <span>Event Contact Extractor</span>
      </div>
      <EventForm onRecordsFetched={(newRecords) => setRecords(newRecords)} />
      <RecordList records={records} />
      <ToastContainer position="top-center" autoClose={3000} />
    </div>
  );
}

export default App;