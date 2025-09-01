import React, { useState, useEffect, useRef } from 'react';
import './VoiceChatBot.css'; // Import the CSS file

const VoiceChatbot = () => {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "مرحبا انا مساعدك لمعرفة احوال الطرق اسألني عن وضع الحواجز وسأجيبك", 
      sender: 'bot' 
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);
  const utterRef = useRef(null);

  useEffect(() => {
    // Check if speech recognition is supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true);
      
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'ar-SA'; // switched to Arabic

      recognitionRef.current.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputText(transcript);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setInputText('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const sendMessage = async () => {
    if (inputText.trim()) {
      const newMessage = {
        id: messages.length + 1,
        text: inputText,
        sender: 'user'
      };
      setMessages(prev => [...prev, newMessage]);

      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL;

        const res = await fetch(`${backendUrl}/api/ask-ai`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: inputText })
        });

        const data = await res.json();

        const botResponse = {
          id: messages.length + 2,
          text: data.response || "⚠️ خطأ: لم يتم الحصول على رد من الذكاء الاصطناعي",
          sender: 'bot'
        };

        setMessages(prev => [...prev, botResponse]);
      } catch (err) {
        console.error("Error communicating with AI:", err);
      }

      setInputText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
      setInputText('');
    }
  };

  const speakMessage = (text) => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "ar-SA";
      u.rate = 0.9;
      u.pitch = 1;
      u.onend = () => setIsSpeaking(false);
      u.onerror = () => setIsSpeaking(false);
      utterRef.current = u;
      setIsSpeaking(true);
      speechSynthesis.speak(u);
    }
  };

  const toggleNarration = () => {
    if (!('speechSynthesis' in window)) return;
    if (speechSynthesis.speaking || speechSynthesis.pending) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const lastBot = [...messages].reverse().find(m => m.sender === 'bot');
    if (!lastBot) return;
    speakMessage(lastBot.text);
  };

  return (
    <div className="voice-chatbot-wrapper">
      <div className="voice-chatbot-container">

        {/* Removed header */}

        <div className="voice-chatbot-messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`voice-chatbot-message ${message.sender === 'user' ? 'user' : 'bot'}`}
            >
              <div className="voice-chatbot-message-content">{message.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="voice-chatbot-input-area">
          <div className="voice-chatbot-input-container">
            <div className="voice-chatbot-text-input-wrapper">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isListening ? "جاري الاستماع..." : "اكتب رسالتك أو استخدم الصوت..."}
                className={`voice-chatbot-text-input ${isListening ? 'disabled' : ''}`}
                rows="1"
                disabled={isListening}
              />
              {isListening && (
                <div className="voice-chatbot-listening-overlay">
                  <div className="voice-chatbot-listening-indicator">
                    <div className="voice-chatbot-pulse-dot"></div>
                    جاري الاستماع...
                  </div>
                </div>
              )}
            </div>
            
            {isSupported && (
              <button
                onClick={isListening ? stopListening : startListening}
                className={`voice-chatbot-btn voice-chatbot-mic-btn ${isListening ? 'listening' : ''}`}
              >
                {isListening ? '🛑' : '🎤'}
              </button>
            )}

            <button
              onClick={toggleNarration}
              className="voice-chatbot-btn voice-chatbot-mic-btn"
              aria-pressed={isSpeaking}
              title={isSpeaking ? 'إيقاف' : 'تشغيل'}
            >
              {isSpeaking ? '⏸️' : '🔊'}
            </button>
            
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isListening}
              className="voice-chatbot-btn voice-chatbot-send-btn"
            >
              ➤
            </button>
          </div>
          
          {!isSupported && (
            <p className="voice-chatbot-not-supported">
              المتصفح لا يدعم التعرف على الصوت
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceChatbot;
