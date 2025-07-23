import React, { useState, useEffect } from 'react';
import './DeploymentDashboard.css';

const DeploymentDashboard = () => {
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDeployment, setSelectedDeployment] = useState(null);
  const [filter, setFilter] = useState('all'); // all, dev, qa, beta, prod

  const API_BASE = process.env.REACT_APP_API_URL || 'https://infraagent-backend.onrender.com';

  useEffect(() => {
    fetchDeployments();
  }, []);

  const fetchDeployments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/deploy/list?limit=50`);
      if (!response.ok) {
        throw new Error('Failed to fetch deployments');
      }
      const data = await response.json();
      setDeployments(data.deployments);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10B981';
      case 'in_progress': return '#F59E0B';
      case 'failed': return '#EF4444';
      case 'pending': return '#6B7280';
      case 'cancelled': return '#9CA3AF';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'failed': return '❌';
      case 'pending': return '⏳';
      case 'cancelled': return '🚫';
      default: return '❓';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getRepoName = (repoUrl) => {
    const parts = repoUrl.split('/');
    return parts[parts.length - 1];
  };

  const filteredDeployments = deployments.filter(deployment => {
    if (filter === 'all') return true;
    return deployment.environment === filter;
  });

  const refreshDeployments = () => {
    fetchDeployments();
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading deployments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">
          <h3>Error loading deployments</h3>
          <p>{error}</p>
          <button onClick={refreshDeployments} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>🚀 Deployment Dashboard</h1>
        <div className="dashboard-controls">
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Environments</option>
            <option value="dev">Development</option>
            <option value="qa">QA</option>
            <option value="beta">Beta</option>
            <option value="prod">Production</option>
          </select>
          <button onClick={refreshDeployments} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="stats-bar">
        <div className="stat-item">
          <span className="stat-number">{deployments.length}</span>
          <span className="stat-label">Total Deployments</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">
            {deployments.filter(d => d.status === 'completed').length}
          </span>
          <span className="stat-label">Successful</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">
            {deployments.filter(d => d.status === 'failed').length}
          </span>
          <span className="stat-label">Failed</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">
            {deployments.filter(d => d.status === 'in_progress').length}
          </span>
          <span className="stat-label">In Progress</span>
        </div>
      </div>

      {filteredDeployments.length === 0 ? (
        <div className="no-deployments">
          <p>No deployments found for the selected filter.</p>
        </div>
      ) : (
        <div className="deployments-grid">
          {filteredDeployments.map((deployment) => (
            <div 
              key={deployment.id} 
              className={`deployment-card ${deployment.status}`}
              onClick={() => setSelectedDeployment(deployment)}
            >
              <div className="deployment-header">
                <div className="deployment-status">
                  <span className="status-icon">{getStatusIcon(deployment.status)}</span>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(deployment.status) }}
                  >
                    {deployment.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="deployment-id">
                  {deployment.id.slice(0, 8)}...
                </div>
              </div>

              <div className="deployment-content">
                <h3 className="repo-name">{getRepoName(deployment.repo_url)}</h3>
                <p className="deployment-prompt">{deployment.prompt}</p>
                
                <div className="deployment-details">
                  <div className="detail-item">
                    <span className="detail-label">Environment:</span>
                    <span className="detail-value">{deployment.environment}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Created:</span>
                    <span className="detail-value">{formatDate(deployment.created_at)}</span>
                  </div>
                  {deployment.completed_at && (
                    <div className="detail-item">
                      <span className="detail-label">Completed:</span>
                      <span className="detail-value">{formatDate(deployment.completed_at)}</span>
                    </div>
                  )}
                </div>

                {deployment.error_message && (
                  <div className="error-details">
                    <span className="error-label">Error:</span>
                    <span className="error-message">{deployment.error_message}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Deployment Details Modal */}
      {selectedDeployment && (
        <div className="modal-overlay" onClick={() => setSelectedDeployment(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Deployment Details</h2>
              <button 
                className="close-btn"
                onClick={() => setSelectedDeployment(null)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-section">
                <h3>Basic Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Deployment ID:</span>
                    <span className="detail-value">{selectedDeployment.id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Repository:</span>
                    <span className="detail-value">{selectedDeployment.repo_url}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Environment:</span>
                    <span className="detail-value">{selectedDeployment.environment}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    <span 
                      className="detail-value status-badge"
                      style={{ backgroundColor: getStatusColor(selectedDeployment.status) }}
                    >
                      {selectedDeployment.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Deployment Description</h3>
                <p className="deployment-description">{selectedDeployment.prompt}</p>
              </div>

              <div className="detail-section">
                <h3>Timeline</h3>
                <div className="timeline">
                  <div className="timeline-item">
                    <span className="timeline-date">{formatDate(selectedDeployment.created_at)}</span>
                    <span className="timeline-event">Deployment created</span>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-date">{formatDate(selectedDeployment.updated_at)}</span>
                    <span className="timeline-event">Last updated</span>
                  </div>
                  {selectedDeployment.completed_at && (
                    <div className="timeline-item">
                      <span className="timeline-date">{formatDate(selectedDeployment.completed_at)}</span>
                      <span className="timeline-event">Deployment completed</span>
                    </div>
                  )}
                </div>
              </div>

              {selectedDeployment.error_message && (
                <div className="detail-section">
                  <h3>Error Details</h3>
                  <div className="error-box">
                    {selectedDeployment.error_message}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeploymentDashboard; 