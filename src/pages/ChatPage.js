import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatPage.css';

const ChevronDownIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);

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

const RotateCcwIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
    <path d="M3 3v5h5"></path>
  </svg>
);
const SendIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);



const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const suggestions = [
    {
        title: "Admissions Information",
        items: [
            { icon: "📅", text: "What is the application deadline for first-year students?" },
            { icon: "🎓", text: "Are SAT or ACT scores required for admission?" },
            { icon: "📝", text: "How can I apply for Early Action, and when is the deadline?" }
        ]
    },
    {
        title: "Application and Fees",
        items: [
            { icon: "💵", text: "Is there an application fee, and how much is it?" },
            { icon: "🏷️", text: "Can I get a fee waiver for the application fee?" },
            { icon: "📄", text: "What documents are required for the application?" }
        ]
    },
    {
        title: "Campus Life & Housing",
        items: [
            { icon: "🏠", text: "What housing options are available for first-year students?" },
            { icon: "👥", text: "How can I get involved in campus organizations?" },
            { icon: "🍽️", text: "What dining options are available on campus?" }
        ]
    }
  ];


  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch("https://aaqilrazak-campi.hf.space/sessions");
      const data = await response.json();
      console.log('Fetched sessions:', data);

      const sessionsWithPreview = data.sessions.map(session => {
        const lastMessage = session.messages?.[0]?.MessageText || "New Chat";
        return {
          ...session,
          preview: lastMessage.length > 60 ? lastMessage.substring(0, 57) + "..." : lastMessage 
        };
      });

      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const handleSessionClick = async (sessionId) => {
    if (sessionId === currentSessionId) return;

    try {
      setIsTyping(false);
      if (currentSessionId && messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        await saveMessage(currentSessionId, lastMessage);
      }

      const response = await fetch(`https://aaqilrazak-campi.hf.space/sessions/${sessionId}/messages`);
      const data = await response.json();
      console.log('Loaded session messages:', data);

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
    }
  };

  const createNewSession = async () => {
    try {
      setMessages([]);
      setIsTyping(false);
      setCurrentSessionId(null);

      const response = await fetch("https://aaqilrazak-campi.hf.space/sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          device_type: navigator.platform,
          browser_agent: navigator.userAgent
        })
      });
      const data = await response.json();
      console.log('Created new session:', data);
      setCurrentSessionId(data.sessionId);
      await fetchSessions();
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const saveMessage = async (sessionId, message) => {
    try {
      const response = await fetch(`https://aaqilrazak-campi.hf.space/sessions/${sessionId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: message.text,
          sender: message.sender === 'user' ? 'User' : 'Bot',
          timestamp: message.timestamp
        })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Saved message:', data);
    } catch (error) {
      console.error('Error saving message:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const bottomTolerance = 100;
    setShowScrollButton(scrollHeight - scrollTop - clientHeight > bottomTolerance);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    if (!currentSessionId) {
      await createNewSession();
    }

    const userMessage = {
      id: Date.now(),
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    await saveMessage(currentSessionId, userMessage);

    try {
      const response = await fetch("https://aaqilrazak-campi.hf.space/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: input })
      });
      const data = await response.json();

      const botResponse = {
        id: Date.now(),
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botResponse]);
      await saveMessage(currentSessionId, botResponse);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now(),
        text: "Sorry, I encountered an error. Please try again.",
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      await saveMessage(currentSessionId, errorMessage);
    }
    setIsTyping(false);
    await fetchSessions();
  };

  const handleSuggestionClick = (text) => {
    setInput(text);
    handleSend();
  };

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
            <button
              key={session.SessionID}
              className={`chat-history-item ${currentSessionId === session.SessionID ? 'active' : ''}`}
              onClick={() => handleSessionClick(session.SessionID)}
            >
              <div className="chat-icon">💬</div> {/* Chat icon or placeholder */}
              <div className="chat-preview">
                {session.preview} {/* Display the preview */}
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
          ))}
        </div>

      </div>

      <div className="main-content">
        <div className="messages-container" ref={messagesContainerRef}>
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1 className="welcome-title">How can I help you today?</h1>
              {suggestions.map((section, index) => (
                <div key={index} className="suggestion-section">
                  <h2 className="suggestion-section-title">{section.title}</h2>
                  <div className="suggestions-grid">
                    {section.items.map((item, idx) => (
                      <button
                        key={idx}
                        className="suggestion-card"
                        onClick={() => handleSuggestionClick(item.text)}
                      >
                        <span className="suggestion-icon">{item.icon}</span>
                        <span>{item.text}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            messages.map((message) => (
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
                  <div className="feedback-options">
                    <button className="feedback-button">👍 Helpful</button>
                    <button className="feedback-button">👎 Not helpful</button>
                  </div>
                )}
              </div>
            ))
          )}

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
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              className="message-input"
              placeholder="Message (⌘+Enter to send)"
            />
            <div className="input-actions">
              <button className="action-button" title="Regenerate response">
                <RotateCcwIcon />
              </button>
              <button className="action-button" onClick={handleSend}>
                <ChevronDownIcon />
              </button>
              <button className="action-button" onClick={handleSend} title="Send">
                <SendIcon />
              </button>
            </div>
          </div>
        </div>

        <button
          className={`scroll-button ${showScrollButton ? 'visible' : ''}`}
          onClick={scrollToBottom}
        >
          <ChevronDownIcon />
        </button>
      </div>
    </div>
  );
};

export default ChatPage;