import { useState } from 'react';
import axios from '../../api';
import './DeployForm.css';

function DeployForm() {
    const [formData, setFormData] = useState({
        prompt: '',
        repoUrl: '',
        environment: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState('');
    const [missingFields, setMissingFields] = useState([]);

    const environments = [
        { value: 'dev', label: 'Development', color: '#10B981' },
        { value: 'qa', label: 'QA/Testing', color: '#F59E0B' },
        { value: 'beta', label: 'Beta/Staging', color: '#3B82F6' },
        { value: 'prod', label: 'Production', color: '#EF4444' }
    ];

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error when user starts typing
        if (error) setError('');
        if (missingFields.length > 0) setMissingFields([]);
    };

    const validateForm = () => {
        const missing = [];
        if (!formData.prompt.trim()) missing.push('deployment description');
        if (!formData.repoUrl.trim()) missing.push('GitHub repository URL');
        if (!formData.environment) missing.push('environment');
        
        setMissingFields(missing);
        return missing.length === 0;
    };

    const handleDeploy = async () => {
        if (!validateForm()) {
            setError(`Please provide: ${missingFields.join(', ')}`);
            return;
        }

        try {
            setIsLoading(true);
            setError('');
            setResponse(null);

            const res = await axios.post('/deploy', {
                prompt: formData.prompt,
                repo_url: formData.repoUrl,
                environment: formData.environment
            });

            setResponse(res.data);
        } catch (err) {
            if (err.response?.status === 400) {
                setError(err.response.data.detail || 'Invalid request. Please check your inputs.');
            } else {
                setError('Something went wrong. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleQuickPrompt = (template) => {
        setFormData(prev => ({ ...prev, prompt: template }));
    };

    return (
        <div className="deploy-container">
            <div className="deploy-card">
                <div className="header">
                    <h1>🚀 InfraAgent</h1>
                    <p>Deploy your applications with AI-powered infrastructure management</p>
                </div>

                <div className="form-section">
                    <label className="form-label">
                        <span className="label-text">Deployment Description</span>
                        <span className="required">*</span>
                    </label>
                    <textarea
                        className={`form-input ${missingFields.includes('deployment description') ? 'error' : ''}`}
                        placeholder="Describe what you want to deploy (e.g., 'Deploy the user authentication service to production')"
                        value={formData.prompt}
                        onChange={(e) => handleInputChange('prompt', e.target.value)}
                        rows={4}
                    />
                    
                    <div className="quick-prompts">
                        <span className="quick-label">Quick templates:</span>
                        <button 
                            className="quick-btn"
                            onClick={() => handleQuickPrompt('Deploy the main application to production')}
                        >
                            Production Deploy
                        </button>
                        <button 
                            className="quick-btn"
                            onClick={() => handleQuickPrompt('Deploy the API service to development')}
                        >
                            Dev Deploy
                        </button>
                        <button 
                            className="quick-btn"
                            onClick={() => handleQuickPrompt('Deploy the frontend to staging')}
                        >
                            Staging Deploy
                        </button>
                    </div>
                </div>

                <div className="form-section">
                    <label className="form-label">
                        <span className="label-text">GitHub Repository URL</span>
                        <span className="required">*</span>
                    </label>
                    <input
                        type="url"
                        className={`form-input ${missingFields.includes('GitHub repository URL') ? 'error' : ''}`}
                        placeholder="https://github.com/username/repository"
                        value={formData.repoUrl}
                        onChange={(e) => handleInputChange('repoUrl', e.target.value)}
                    />
                </div>

                <div className="form-section">
                    <label className="form-label">
                        <span className="label-text">Environment</span>
                        <span className="required">*</span>
                    </label>
                    <div className="environment-grid">
                        {environments.map((env) => (
                            <button
                                key={env.value}
                                className={`env-btn ${formData.environment === env.value ? 'selected' : ''} ${missingFields.includes('environment') ? 'error' : ''}`}
                                onClick={() => handleInputChange('environment', env.value)}
                                style={{ '--env-color': env.color }}
                            >
                                <div className="env-dot" style={{ backgroundColor: env.color }}></div>
                                <span>{env.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <button 
                    className={`deploy-btn ${isLoading ? 'loading' : ''}`}
                    onClick={handleDeploy}
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <div className="spinner"></div>
                            Deploying...
                        </>
                    ) : (
                        '🚀 Deploy Now'
                    )}
                </button>

                {error && (
                    <div className="error-message">
                        <span className="error-icon">⚠️</span>
                        {error}
                    </div>
                )}

                {response && (
                    <div className="response-section">
                        <h3>✅ Deployment Response</h3>
                        <pre className="response-content">
                            {JSON.stringify(response, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
}

export default DeployForm;
