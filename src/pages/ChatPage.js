import React, { useState } from 'react';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Function to handle sending a message
  const handleSendMessage = () => {
    if (input.trim()) {
      const newMessages = [...messages, { text: input, sender: 'user' }]; // Add user message
      setMessages(newMessages); // Update messages state with the new message
      setInput(''); // Clear input field

      // Simulate a bot response after 1 second
      setTimeout(() => {
        setMessages([...newMessages, { text: 'This is a bot response', sender: 'bot' }]); 
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
