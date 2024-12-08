import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/ChatPage.css';

// SVG Icons
const MenuIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="12" x2="21" y2="12"></line>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <line x1="3" y1="18" x2="21" y2="18"></line>
  </svg>
);

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 6h18"></path>
    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
  </svg>
);

// Template questions organized by category
const TEMPLATE_QUESTIONS = {
  "Quick Info": [
    { icon: "🔍", text: "What's happening right now?" },
    { icon: "🍽️", text: "What's going on this week?" },
  ],
  "Study & Workspace": [
    { icon: "📚", text: "What buildings are open right now that I can study in?" },
    { icon: "👥", text: "Where can I study with a group?" },
    { icon: "🔌", text: "Where is a quiet place to attend online class?" },
    { icon: "🖨️", text: "Where can I use a printer?" }
  ],
  "Social & Entertainment": [
    { icon: "🎉", text: "What fun events are happening today?" },
    { icon: "👋", text: "What sporting events are happening this weekend?" },
    { icon: "🤝", text: "What amenities does the Recreation Center offer?" },
    { icon: "📅", text: "What student organizations are active this semester?" }
  ],
  "Food & Drinks": [
    { icon: "🍳", text: "What's good for breakfast?" },
    { icon: "🥪", text: "What's good for lunch?" },
    { icon: "🍕", text: "What's good for dinner?" },
    { icon: "🌙", text: "Where can I get food late?" },
    { icon: "🆓", text: "Where can i get free drinks?" }
  ],
  "Campus Facilities": [
    { icon: "📖", text: "List all libraries and their locations" },
    { icon: "🏢", text: "List all buildings and their locations" }
  ],
  "Events & Activities": [
    { icon: "🎯", text: "What events are scheduled for this week" },
    { icon: "🎪", text: "What entertainment events are happening this weekend" }
  ]
};

const ChatPage = () => {
  const [messageCounter, setMessageCounter] = useState(0);
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Fetch sessions on component mount
  useEffect(() => {
    fetchSessions().catch(err => {
      console.error('Error fetching sessions:', err);
      setError('Failed to load chat history');
    });
  }, []);

  // Auto-scroll effect
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Scroll listener effect
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch("http://localhost:8000/sessions");
      if (!response.ok) throw new Error('Failed to fetch sessions');
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      throw error;
    }
  };

  const createNewSession = async () => {
    try {
      setMessages([]);
      setIsTyping(false);
      setCurrentSessionId(null);
      setSelectedCategory(null);

      const response = await fetch("http://localhost:8000/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device_type: navigator.platform,
          browser_agent: navigator.userAgent
        })
      });

      if (!response.ok) throw new Error('Failed to create session');
      const data = await response.json();
      setCurrentSessionId(data.sessionId);
      await fetchSessions();
    } catch (error) {
      console.error('Error creating session:', error);
      setError('Failed to start new chat');
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        throw new Error('Failed to delete session');
      }
      await fetchSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleSessionClick = async (sessionId) => {
    if (sessionId === currentSessionId) return;

    try {
      setIsTyping(false);
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/messages`);
      if (!response.ok) throw new Error('Failed to fetch session messages');
      const data = await response.json();

      if (data.messages) {
        setMessages(data.messages.map(msg => ({
          id: msg.MessageID,
          text: msg.MessageText,
          sender: msg.Sender.toLowerCase(),
          timestamp: msg.Timestamp
        })));
      } else {
        setMessages([]);
      }
      setCurrentSessionId(sessionId);
    } catch (error) {
      console.error('Error switching sessions:', error);
      setError('Failed to load chat messages');
    }
  };

  const saveMessage = async (sessionId, message) => {
    if (!sessionId) {
      console.error('Attempted to save message without valid session ID');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message.text,
          sender: message.sender === 'user' ? 'User' : 'Bot',
          timestamp: message.timestamp
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save message');
      }
    } catch (error) {
      console.error('Error saving message:', error);
      throw error;
    }
  };

  const handleQuestionClick = async (question) => {
    let sessionId = currentSessionId;

    try {
      // Make sure we have a valid session
      if (!sessionId) {
        const response = await fetch("http://localhost:8000/sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            device_type: navigator.platform,
            browser_agent: navigator.userAgent
          })
        });

        if (!response.ok) {
          throw new Error('Failed to create session');
        }

        const data = await response.json();
        sessionId = data.sessionId;
        setCurrentSessionId(sessionId);
      }

      const userMessage = {
        id: `${Date.now()}-${messageCounter}`,
        text: question,
        sender: 'user',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage]);
      setMessageCounter(prev => prev + 1);  // Increment counter after using it
      setIsTyping(true);
      setSelectedCategory(null);

      await saveMessage(sessionId, userMessage);

      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: question })
      });

      if (!response.ok) {
        throw new Error(`Failed to generate response: ${response.status}`);
      }

      const data = await response.json();

      const botResponse = {
        id: `${Date.now()}-${messageCounter}`,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botResponse]);
      setMessageCounter(prev => prev + 1);  // Increment counter after using it
      await saveMessage(sessionId, botResponse);
      await fetchSessions();

    } catch (error) {
      console.error('Error:', error);
      setIsTyping(false);

      if (error.message.includes('Failed to generate response')) {
        const errorMessage = {
          id: `${Date.now()}-${messageCounter}`,
          text: "Sorry, I encountered an error. Please try again.",
          sender: 'bot',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
        setMessageCounter(prev => prev + 1);  // Increment counter after using it

        if (sessionId) {
          await saveMessage(sessionId, errorMessage);
        }
      }
    } finally {
      setIsTyping(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    setShowScrollButton(scrollHeight - scrollTop - clientHeight > 100);
  };

  const renderWelcomeScreen = () => (
    <div className="welcome-screen">
      <h1 className="welcome-title">How can I help you today?</h1>
      {selectedCategory ? (
        <div className="question-grid">
          {TEMPLATE_QUESTIONS[selectedCategory].map((item, index) => (
            <button
              key={index}
              className="question-card"
              onClick={() => handleQuestionClick(item.text)}
            >
              <span className="question-icon">{item.icon}</span>
              <span>{item.text}</span>
            </button>
          ))}
          <button
            className="back-button"
            onClick={() => setSelectedCategory(null)}
          >
            ← Back to Categories
          </button>
        </div>
      ) : (
        <div className="categories-grid">
          {Object.entries(TEMPLATE_QUESTIONS).map(([category, questions]) => (
            <button
              key={category}
              className="category-card"
              onClick={() => setSelectedCategory(category)}
            >
              <span className="category-icon">
                {questions[0].icon}
              </span>
              <span className="category-title">{category}</span>
              <span className="category-count">
                {questions.length} questions
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );

  const renderChatMessages = () => (
    <>
      {messages.map((message) => (
        <div key={message.id} className="message-group">
          <div className="message">
            <div className={`avatar ${message.sender}-avatar`}>
              {message.sender === 'user' ? 'U' : 'A'}
            </div>
            <div className="message-content">
              {message.text}
            </div>
          </div>
          {message.sender === 'bot' && (
            <div className="message-actions">
              <button className="action-button" onClick={() => setSelectedCategory(null)}>
                Ask Another Question
              </button>
              <button className="action-button" onClick={createNewSession}>
                Start New Chat
              </button>
            </div>
          )}
        </div>
      ))}
      {isTyping && (
        <div className="message-group">
          <div className="message">
            <div className="avatar bot-avatar">A</div>
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  return (
    <div className="chat-container">
      <div className="sidebar">
        <button className="new-chat-button" onClick={createNewSession}>
          <span className="flex items-center">
            <MenuIcon className="mr-2" />
            New chat
          </span>
          <PlusIcon />
        </button>
        <div className="chat-history-list">
          {sessions.map((session) => (
            <div key={session.SessionID} className="chat-history-item-wrapper">
              <button
                className={`chat-history-item ${currentSessionId === session.SessionID ? 'active' : ''}`}
                onClick={() => handleSessionClick(session.SessionID)}
              >
                <div className="chat-icon">💬</div>
                <div className="chat-preview">
                  {session.preview}
                </div>
                <div className="chat-time">
                  {new Date(session.SessionStartTime).toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </button>
              <button
                className="delete-session-button"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteSession(session.SessionID);
                }}
                title="Delete session"
              >
                <TrashIcon />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        <div className="messages-container" ref={messagesContainerRef}>
          {error && <div className="error-message">{error}</div>}
          {messages.length === 0 ? renderWelcomeScreen() : renderChatMessages()}
          <div ref={messagesEndRef} />
        </div>
        {showScrollButton && (
          <button className="scroll-button" onClick={scrollToBottom}>
            ↓
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatPage;