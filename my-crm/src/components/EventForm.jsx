import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function EventForm({ onRecordsFetched }) {
  const [eventName, setEventName] = useState('');
  const [file, setFile] = useState(null);
  const [manualEntry, setManualEntry] = useState({ name: '', company: '' });
  const [useManual, setUseManual] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (useManual) {
        const payload = {
          ...manualEntry,
          event_name: eventName,
          source_file: "manual-entry"
        };
        await axios.post("http://localhost:8000/add-manual", payload);
        onRecordsFetched([payload]);
        toast.success("Manual entry added!");
      } else {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("event_name", eventName);
        const res = await axios.post("http://localhost:8000/add-file", formData);
        onRecordsFetched(res.data.records || []);
        toast.success(`${res.data.records_added} record(s) extracted!`);
      }
    } catch (error) {
      console.error(error);
      toast.error("Upload failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form">
      <h2>Create New Event</h2>
      <input placeholder="Event Name" value={eventName} onChange={e => setEventName(e.target.value)} required />

      <label>
        <input type="checkbox" checked={useManual} onChange={() => setUseManual(!useManual)} />
        Enter Manually
      </label>

      {useManual ? (
        <>
          <input placeholder="Name" value={manualEntry.name} onChange={e => setManualEntry({ ...manualEntry, name: e.target.value })} />
          <input placeholder="Company" value={manualEntry.company} onChange={e => setManualEntry({ ...manualEntry, company: e.target.value })} />
        </>
      ) : (
        <input type="file" onChange={e => setFile(e.target.files[0])} required />
      )}

      <button type="submit" disabled={loading}>
        {loading ? "Uploading..." : "Submit"}
      </button>
    </form>
  );
}

export default EventForm;