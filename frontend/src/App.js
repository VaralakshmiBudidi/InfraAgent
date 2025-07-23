// src/App.js
import React, { useState } from 'react';
import DeployForm from './components/pages/DeployForm';
import DeploymentDashboard from './components/pages/DeploymentDashboard';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('deploy'); // 'deploy' or 'dashboard'

  return (
    <div className="App">
      <nav className="app-nav">
        <div className="nav-brand">
          <h1>🚀 InfraAgent</h1>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-btn ${currentView === 'deploy' ? 'active' : ''}`}
            onClick={() => setCurrentView('deploy')}
          >
            📝 Deploy
          </button>
          <button 
            className={`nav-btn ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            📊 Dashboard
          </button>
        </div>
      </nav>

      <main className="app-main">
        {currentView === 'deploy' ? (
          <DeployForm />
        ) : (
          <DeploymentDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
