import React, { useState } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Function to handle sending a message
  const handleSendMessage = () => {
    if (input.trim()) {
      const timestamp = new Date().toLocaleTimeString(); // Get the current time as timestamp
      const newMessages = [...messages, { text: input, sender: 'user', time: timestamp }]; // Add user message with timestamp
      setMessages(newMessages); // Update messages state with the new message
      setInput(''); // Clear input field

      // Simulate a bot response after 1 second
      setTimeout(() => {
        const botTimestamp = new Date().toLocaleTimeString(); // Get timestamp for bot response
        setMessages([...newMessages, { text: 'This is a bot response', sender: 'bot', time: botTimestamp }]); 
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
