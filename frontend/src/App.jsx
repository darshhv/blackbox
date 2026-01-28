/**
 * BLACKBOX Frontend Application
 * Calm, minimal, narrative-focused
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import IncidentsList from './pages/IncidentsList';
import IncidentDetail from './pages/IncidentDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<IncidentsList />} />
        <Route path="/incidents/:id" element={<IncidentDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
