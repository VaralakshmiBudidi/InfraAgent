import React, { useState } from 'react';
import './DeployForm.css';

const DeployForm = () => {
  const [formData, setFormData] = useState({
    prompt: ''
  });
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [missingFields, setMissingFields] = useState([]);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (error) setError(null);
    if (missingFields.includes(name)) {
      setMissingFields(prev => prev.filter(field => field !== name));
    }
  };

  const validateForm = () => {
    const missing = [];
    if (!formData.prompt.trim()) missing.push('prompt');
    setMissingFields(missing);
    return missing.length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const response = await fetch(`${API_BASE}/deploy/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: formData.prompt
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Deployment failed');
      }

      setResponse(data);
      
      // Only reset form if deployment was successful
      if (data.status === 'success') {
        setFormData({ prompt: '' });
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getResponseContainerClass = () => {
    if (response.status === 'needs_repo_url' || response.status === 'needs_environment') {
      return 'warning-container';
    }
    return 'success-container';
  };

  const renderResponseContent = () => {
    if (response.status === 'needs_repo_url') {
      return (
        <>
          <h3>🤖 AI Needs Repository URL</h3>
          <div className="response-details">
            <p><strong>Message:</strong> {response.message}</p>
            
            {response.extracted_info && (
              <div className="ai-extracted-info">
                <h4>✅ AI Extracted Information:</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Environment:</span>
                    <span className="info-value">{response.extracted_info.environment || '❌ Missing'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Type:</span>
                    <span className="info-value">{response.extracted_info.deployment_type}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Repository:</span>
                    <span className="info-value">❌ Missing - Please include GitHub URL</span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="suggestion-box">
              <h4>💡 Try these examples:</h4>
              <ul>
                <li>"Deploy my sample app from https://github.com/VaralakshmiBudidi/sample-app to dev"</li>
                <li>"Deploy the React app from https://github.com/username/my-app to production"</li>
                <li>"Deploy my API backend from https://github.com/username/api to staging"</li>
              </ul>
            </div>
          </div>
        </>
      );
    }

    if (response.status === 'needs_environment') {
      return (
        <>
          <h3>🤖 AI Needs Environment</h3>
          <div className="response-details">
            <p><strong>Message:</strong> {response.message}</p>
            
            {response.extracted_info && (
              <div className="ai-extracted-info">
                <h4>✅ AI Extracted Information:</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Repository:</span>
                    <span className="info-value">{response.extracted_info.repo_url}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Type:</span>
                    <span className="info-value">{response.extracted_info.deployment_type}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Environment:</span>
                    <span className="info-value">❌ Missing - Please specify environment</span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="suggestion-box">
              <h4>💡 Available Environments:</h4>
              <ul>
                <li><strong>dev</strong> - Development environment</li>
                <li><strong>qa</strong> - Quality Assurance/Testing</li>
                <li><strong>beta</strong> - Beta/Staging environment</li>
                <li><strong>prod</strong> - Production environment</li>
              </ul>
              <h4>💡 Try these examples:</h4>
              <ul>
                <li>"Deploy my app from https://github.com/username/repo to dev"</li>
                <li>"Deploy to production environment"</li>
                <li>"Deploy to staging for testing"</li>
              </ul>
            </div>
          </div>
        </>
      );
    }

    return (
      <>
        <h3>✅ Deployment Initiated!</h3>
        <div className="response-details">
          <p><strong>Deployment ID:</strong> {response.deployment_id}</p>
          <p><strong>Status:</strong> {response.status}</p>
          <p><strong>Message:</strong> {response.message}</p>
          
          {response.extracted_info && (
            <div className="ai-extracted-info">
              <h4>🤖 AI Extracted Information:</h4>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Repository:</span>
                  <span className="info-value">{response.extracted_info.repo_url || 'Not found'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Environment:</span>
                  <span className="info-value">{response.extracted_info.environment}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Type:</span>
                  <span className="info-value">{response.extracted_info.deployment_type}</span>
                </div>
                {response.extracted_info.requirements && (
                  <div className="info-item">
                    <span className="info-label">Requirements:</span>
                    <span className="info-value">{response.extracted_info.requirements}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <div className="deploy-container">
      <div className="deploy-card">
        <div className="deploy-header">
          <h1>🚀 AI-Powered Deployment</h1>
          <p>Just describe what you want to deploy, and AI will handle the rest!</p>
        </div>

        <form onSubmit={handleSubmit} className="deploy-form">
          <div className="form-group">
            <label htmlFor="prompt" className="form-label">
              What would you like to deploy?
            </label>
            <textarea
              id="prompt"
              name="prompt"
              value={formData.prompt}
              onChange={handleInputChange}
              placeholder="Describe your deployment request in natural language. For example: 'Deploy my React app from https://github.com/username/my-app to production'"
              className={`form-input ${missingFields.includes('prompt') ? 'error' : ''}`}
              rows={4}
              disabled={loading}
            />
            {missingFields.includes('prompt') && (
              <span className="error-message">Please describe what you want to deploy</span>
            )}
          </div>

          <button
            type="submit"
            className={`deploy-btn ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing and Deploying...
              </>
            ) : (
              '🚀 Deploy Now'
            )}
          </button>
        </form>

        {error && (
          <div className="error-container">
            <h3>❌ Deployment Failed</h3>
            <p>{error}</p>
            <button onClick={() => setError(null)} className="dismiss-btn">
              Dismiss
            </button>
          </div>
        )}

        {response && (
          <div className={getResponseContainerClass()}>
            {renderResponseContent()}
            <button onClick={() => setResponse(null)} className="dismiss-btn">
              Dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeployForm;
