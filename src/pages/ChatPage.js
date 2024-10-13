// src/pages/ChatPage.js
import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionTimestamp] = useState(new Date().toLocaleTimeString()); // Session timestamp
  const messagesEndRef = useRef(null);

  const defaultUserAvatar = 'https://via.placeholder.com/40/007aff/ffffff?text=U';
  const defaultBotAvatar = 'https://via.placeholder.com/40/4e4e4e/ffffff?text=B';

  const handleSendMessage = () => {
    if (input.trim()) {
      const timestamp = new Date().toLocaleTimeString();
      const newMessage = {
        text: input,
        sender: 'user',
        time: timestamp,
        avatar: defaultUserAvatar,
      };
      const updatedMessages = [...messages, newMessage];
      setMessages(updatedMessages);
      setInput('');
      setIsTyping(true);

      setTimeout(() => {
        const botResponse = {
          text: 'This is a bot response',
          sender: 'bot',
          time: new Date().toLocaleTimeString(),
          avatar: defaultBotAvatar,
        };
        setMessages([...updatedMessages, botResponse]);
        setIsTyping(false);
      }, 2000);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleFeedback = (index, feedback) => {
    console.log(`Feedback for message ${index}: ${feedback}`);
  };

  return (
    <div className="chat-container">
      {/* Display session timestamp */}
      <div className="session-timestamp">
        Chat session started at {sessionTimestamp}
      </div>
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`${message.sender}-message-row fade-in`}>
            <img src={message.avatar} alt={`${message.sender} avatar`} className="avatar" />
            <div className={`${message.sender}-message`} title={`Sent at ${message.time}`}>
              <p>{message.text}</p>
              {/* Timestamp shown on hover through CSS */}
              <span className="hover-timestamp">{message.time}</span>
              {message.sender === 'bot' && (
                <div className="feedback-options">
                  <button onClick={() => handleFeedback(index, 'helpful')}>Helpful</button>
                  <button onClick={() => handleFeedback(index, 'not-helpful')}>Not Helpful</button>
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && <div className="typing-indicator">Bot is typing...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="input"
        />
        <button onClick={handleSendMessage} className="send-button">
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;