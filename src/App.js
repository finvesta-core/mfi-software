import React, { useState, useEffect } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Button, Typography, TextField } from '@mui/material';

// अगर तुम्हारा DB file है, तो import करो (उदाहरण)
let initialData = [];
try {
  initialData = require('./database.json'); // <-- अपना DB file name डालो
} catch (e) {
  initialData = [];
}

function App() {
  const [rows, setRows] = useState(() => {
    const saved = localStorage.getItem('mfiData');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return initialData;
      }
    }
    return initialData;
  });

  const [newName, setNewName] = useState('');
  const [newAmount, setNewAmount] = useState('');

  useEffect(() => {
    localStorage.setItem('mfiData', JSON.stringify(rows));
  }, [rows]);

  const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'name', headerName: 'ग्राहक नाम', width: 220, editable: true },
    { field: 'amount', headerName: 'लोन राशि (₹)', width: 160, editable: true, type: 'number' },
    { field: 'date', headerName: 'तारीख', width: 180, editable: true },
  ];

  const addRow = () => {
    if (!newName.trim() || !newAmount) return;
    const newRow = {
      id: Date.now(),
      name: newName,
      amount: parseInt(newAmount),
      date: new Date().toISOString().split('T')[0],
    };
    setRows([...rows, newRow]);
    setNewName('');
    setNewAmount('');
  };

  const processRowUpdate = (newRow) => {
    setRows(rows.map(r => r.id === newRow.id ? newRow : r));
    return newRow;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>MFI सॉफ्टवेयर</Typography>

      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField label="नाम" value={newName} onChange={e => setNewName(e.target.value)} />
        <TextField label="राशि" type="number" value={newAmount} onChange={e => setNewAmount(e.target.value)} />
        <Button variant="contained" onClick={addRow}>जोड़ें</Button>
      </Box>

      <Box sx={{ height: 500 }}>
        <DataGrid
          rows={rows}
          columns={columns}
          editMode="row"
          processRowUpdate={processRowUpdate}
          pageSizeOptions={[5, 10]}
        />
      </Box>
    </Box>
  );
}

export default App;