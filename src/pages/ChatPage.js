import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [sessions, setSessions] = useState([{ id: 1, messages: [] }]);
  const [currentSessionId, setCurrentSessionId] = useState(1);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [hideScrollToBottom, setHideScrollToBottom] = useState(true);
  const [theme, setTheme] = useState('default');
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const delayTimeout = useRef(null);

  const defaultUserAvatar = 'https://via.placeholder.com/40/007aff/ffffff?text=U';
  const defaultBotAvatar = 'https://via.placeholder.com/40/4e4e4e/ffffff?text=B';

  const getCurrentSession = () => sessions.find((session) => session.id === currentSessionId);

  const handleThemeChange = (e) => setTheme(e.target.value);

  const handleSendMessage = () => {
    if (input.trim()) {
      const timestamp = new Date().toLocaleTimeString();
      const currentSession = getCurrentSession();
      
      const newMessages = currentSession.messages.length === 0 
        ? [{ text: `Session started at ${timestamp}`, sender: 'system' }]
        : [];
      
      newMessages.push({ text: input, sender: 'user', time: timestamp, avatar: defaultUserAvatar });
      
      setSessions(prevSessions =>
        prevSessions.map(session =>
          session.id === currentSessionId
            ? { ...session, messages: [...session.messages, ...newMessages] }
            : session
        )
      );
      
      setInput('');
      setIsTyping(true);

      setTimeout(() => {
        const botResponse = {
          text: 'This is a bot response.',
          sender: 'bot',
          time: new Date().toLocaleTimeString(),
          avatar: defaultBotAvatar,
        };
        
        setSessions(prevSessions =>
          prevSessions.map(session =>
            session.id === currentSessionId
              ? { ...session, messages: [...session.messages, botResponse] }
              : session
          )
        );
        setIsTyping(false);
      }, 2000);
    }
  };

  const handleFeedback = (index, feedback) => {
    console.log(`Feedback for message ${index} in session ${currentSessionId}: ${feedback}`);
  };

  const startNewChat = () => {
    const newSessionId = currentSessionId + 1;
    setSessions([...sessions, { id: newSessionId, messages: [] }]);
    setCurrentSessionId(newSessionId);
  };

  const handleScroll = () => {
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;

    if (delayTimeout.current) {
      clearTimeout(delayTimeout.current);
    }

    if (!isAtBottom) {
      delayTimeout.current = setTimeout(() => {
        setHideScrollToBottom(false);
      }, 1000);
    } else {
      setHideScrollToBottom(true);
    }

    if (scrollTop === 0 && !loadingHistory) {
      setLoadingHistory(true);
      setTimeout(() => {
        setLoadingHistory(false);
      }, 1000);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setHideScrollToBottom(true);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [sessions, currentSessionId, isTyping]);

  useEffect(() => {
    return () => clearTimeout(delayTimeout.current);
  }, []);

  const currentSession = getCurrentSession();

  return (
    <div className={`chat-container`} data-theme={theme}>
      <select className="theme-selector" value={theme} onChange={handleThemeChange}>
        <option value="default">Default</option>
        <option value="university-blue">University Blue</option>
        <option value="university-red">University Red</option>
        <option value="university-green">University Green</option>
      </select>

      <div 
        className="messages-container" 
        onScroll={handleScroll} 
        ref={messagesContainerRef}
      >
        {loadingHistory && <div className="loading-history">Loading previous messages...</div>}
        {currentSession.messages.map((message, index) => (
          <div key={index} className={`${message.sender}-message-row fade-in`}>
            {message.sender !== 'system' && (
              <>
                <img src={message.avatar || defaultBotAvatar} alt={`${message.sender} avatar`} className="avatar" />
                <div className={`${message.sender}-message`} title={`Sent at ${message.time}`}>
                  <p>{message.text}</p>
                  <span className="hover-timestamp">{message.time}</span>
                  {message.sender === 'bot' && (
                    <div className="feedback-options">
                      <button onClick={() => handleFeedback(index, 'helpful')}>Helpful</button>
                      <button onClick={() => handleFeedback(index, 'not-helpful')}>Not Helpful</button>
                    </div>
                  )}
                </div>
              </>
            )}
            {message.sender === 'system' && (
              <div className="session-timestamp">{message.text}</div>
            )}
          </div>
        ))}
        {isTyping && <div className="typing-indicator">Bot is typing...</div>}
        <div ref={messagesEndRef} />
      </div>
      
      <button 
        onClick={scrollToBottom} 
        className={`scroll-to-bottom-button ${hideScrollToBottom ? 'hidden' : ''}`}
      >
        ⬇️
      </button>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="input"
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage} className="send-button">Send</button>
        <button onClick={startNewChat} className="new-session-button">New Chat</button>
      </div>
    </div>
  );
};

export default ChatPage;