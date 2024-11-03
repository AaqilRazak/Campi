import React, { useState } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault(); // Prevent form submission refresh
    if (input.trim()) {
      // Add user message
      setMessages([...messages, { text: input, sender: 'user' }]);
      
      // Simulate bot response (we'll replace this with actual API call later)
      setTimeout(() => {
        setMessages(prevMessages => [...prevMessages, {
          text: "I'm here to help! What would you like to know about Texas State University?",
          sender: 'bot'
        }]);
      }, 1000);
      
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message-bubble ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
          >
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
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