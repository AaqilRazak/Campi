import React, { useState } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false); // New state for managing the typing indicator

  // Function to handle sending a message
  const handleSendMessage = () => {
    if (input.trim()) {
      const timestamp = new Date().toLocaleTimeString(); 
      const newMessages = [...messages, { text: input, sender: 'user', time: timestamp }]; 
      setMessages(newMessages);
      setInput('');

      setIsTyping(true); // Show typing indicator

      // Simulate a bot response after 1 second
      setTimeout(() => {
        const botTimestamp = new Date().toLocaleTimeString(); 
        setMessages([...newMessages, { text: 'This is a bot response', sender: 'bot', time: botTimestamp }]);
        setIsTyping(false); // Hide typing indicator after bot sends response
      }, 1000);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={message.sender === 'user' ? 'user-message' : 'bot-message'}
          >
            <p>{message.text}</p>
            <span className="timestamp">{message.time}</span>
          </div>
        ))}
        {isTyping && <div className="typing-indicator">Bot is typing...</div>} {/* Show typing indicator when bot is typing */}
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
