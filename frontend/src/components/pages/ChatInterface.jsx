import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'https://infraagent-backend.onrender.com';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send message');
      }

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.message,
        timestamp: new Date(),
        needsInput: data.needs_input,
        inputType: data.input_type,
        suggestions: data.suggestions
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `Sorry, I'm having trouble right now: ${error.message}`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>🤖 InfraAgent AI Assistant</h1>
        <p>Chat with me to deploy your applications!</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-content">
              <h3>👋 Hello! I'm InfraAgent</h3>
              <p>I can help you deploy your applications. Just tell me what you need!</p>
              <div className="example-prompts">
                <h4>💡 Try saying:</h4>
                <ul>
                  <li>"Hi, I need help deploying my app"</li>
                  <li>"Deploy my React app to production"</li>
                  <li>"I want to deploy to the dev environment"</li>
                  <li>"Can you help me deploy from GitHub?"</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.type} ${message.isError ? 'error' : ''}`}
          >
            <div className="message-content">
              <div className="message-header">
                <span className="message-author">
                  {message.type === 'user' ? 'You' : '🤖 InfraAgent'}
                </span>
                <span className="message-time">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <div className="message-text">
                {message.content}
              </div>
              
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="suggestions">
                  <p className="suggestion-label">💡 Quick suggestions:</p>
                  <div className="suggestion-buttons">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        className="suggestion-btn"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message ai">
            <div className="message-content">
              <div className="message-header">
                <span className="message-author">🤖 InfraAgent</span>
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message here..."
            disabled={isLoading}
            className="chat-input"
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim()}
            className="send-button"
          >
            {isLoading ? (
              <span className="loading-spinner"></span>
            ) : (
              '🚀'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface; 