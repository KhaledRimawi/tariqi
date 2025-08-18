import React, { useState, useEffect, useRef } from 'react';

const ChatBotpage = () => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [userInput, setUserInput] = useState('');
  const [showInput, setShowInput] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (text, isBot = true) => {
    const newMessage = {
      id: Date.now(),
      text,
      isBot,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const showTyping = (duration = 1000) => {
    setIsTyping(true);
    return new Promise(resolve => {
      setTimeout(() => {
        setIsTyping(false);
        resolve();
      }, duration);
    });
  };

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const handleOptionClick = async (option) => {
    // Add user's choice as a message
    addMessage(option.label, false);
    setShowOptions(false);
    setOptions([]);
    
    // Continue conversation based on choice
    await sleep(800);
    await showTyping();
    
    let responseText = "";
    switch(option.value) {
      case 'info':
        responseText = "Perfect! I have access to lots of information. What topic interests you? 📚";
        break;
      case 'question':
        responseText = "Great! I'm here to answer your questions. What would you like to know? 🤔";
        break;
      case 'chat':
        responseText = "Awesome! I love casual conversations. How's your day going? ☀️";
        break;
      case 'support':
        responseText = "I'm here to help with technical issues. What seems to be the problem? 🔧";
        break;
      default:
        responseText = "Thanks for letting me know! 😊";
    }
    
    addMessage(responseText);
    
    // Show text input for follow-up
    await sleep(1000);
    setShowInput(true);
    setCurrentStep(3);
  };

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    
    // Add user's input as message
    addMessage(userInput, false);
    setUserInput('');
    setShowInput(false);
    
    // Show typing and respond
    await sleep(800);
    await showTyping();
    addMessage(`Thanks for sharing: "${userInput}". I'm always here if you need more help! 🚀`);
    
    // Show final options
    await sleep(1000);
    setOptions([
      { label: "🔄 Start Over", value: "restart" },
      { label: "👋 End Chat", value: "end" }
    ]);
    setShowOptions(true);
  };

  const startConversation = async () => {
    await sleep(1000);
    await showTyping();
    addMessage("👋 Hello! I'm your virtual assistant. How can I help you today?");
    
    await sleep(1000);
    await showTyping();
    addMessage("What's your name?");
    
    setShowInput(true);
    setCurrentStep(1);
  };

  const handleNameSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    
    const userName = userInput;
    addMessage(userName, false);
    setUserInput('');
    setShowInput(false);
    
    await sleep(800);
    await showTyping();
    addMessage(`Nice to meet you, ${userName}! 🎉`);
    
    await sleep(1000);
    setOptions([
      { label: "💡 Get Information", value: "info" },
      { label: "❓ Ask a Question", value: "question" },
      { label: "💬 Just Chatting", value: "chat" },
      { label: "🛠️ Technical Support", value: "support" }
    ]);
    setShowOptions(true);
    setCurrentStep(2);
  };

  useEffect(() => {
    startConversation();
  }, []);

  const handleSubmit = currentStep === 1 ? handleNameSubmit : handleTextSubmit;

  return (
    <div style={{ 
      maxWidth: '600px', 
      margin: '20px auto', 
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <h1 style={{ 
        textAlign: 'center', 
        marginBottom: '20px',
        color: '#333'
      }}>
        🤖 Virtual Assistant Chat
      </h1>
      
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '12px',
        height: '500px',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#fff',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        {/* Messages Container */}
        <div style={{
          flex: 1,
          padding: '20px',
          overflowY: 'auto',
          backgroundColor: '#fafafa'
        }}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: 'flex',
                marginBottom: '16px',
                justifyContent: message.isBot ? 'flex-start' : 'flex-end'
              }}
            >
              <div
                style={{
                  maxWidth: '70%',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  backgroundColor: message.isBot ? '#e3f2fd' : '#667eea',
                  color: message.isBot ? '#333' : '#fff',
                  position: 'relative',
                  animation: 'messageSlideIn 0.3s ease-out'
                }}
              >
                {message.text}
                <div
                  style={{
                    position: 'absolute',
                    [message.isBot ? 'left' : 'right']: '-8px',
                    top: '12px',
                    width: '0',
                    height: '0',
                    borderTop: '8px solid transparent',
                    borderBottom: '8px solid transparent',
                    [message.isBot ? 'borderRight' : 'borderLeft']: `8px solid ${message.isBot ? '#e3f2fd' : '#667eea'}`
                  }}
                />
              </div>
            </div>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <div style={{ display: 'flex', marginBottom: '16px' }}>
              <div style={{
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: '#f0f0f0',
                color: '#666'
              }}>
                <span style={{ animation: 'typing 1.5s infinite' }}>...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Actions Container */}
        <div style={{
          padding: '20px',
          backgroundColor: '#fff',
          borderTop: '1px solid #eee'
        }}>
          {/* Options */}
          {showOptions && (
            <div style={{ marginBottom: '10px' }}>
              {options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleOptionClick(option)}
                  style={{
                    width: '100%',
                    padding: '12px 20px',
                    margin: '4px 0',
                    backgroundColor: '#667eea',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#5a6fd8'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#667eea'}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
          
          {/* Text Input */}
          {showInput && (
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder={currentStep === 1 ? "Enter your name..." : "Type your message..."}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '2px solid #ddd',
                  borderRadius: '25px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#ddd'}
                autoFocus
              />
              <button
                type="submit"
                style={{
                  backgroundColor: '#667eea',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 20px',
                  borderRadius: '25px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  minWidth: '60px'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#5a6fd8'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#667eea'}
              >
                Send
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Add global styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes messageSlideIn {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes typing {
            0%, 60%, 100% {
              transform: initial;
            }
            30% {
              transform: translateY(-10px);
            }
          }
        `
      }} />
    </div>
  );
};

export default ChatBotpage;