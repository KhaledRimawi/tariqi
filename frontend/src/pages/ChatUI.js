import React, { useState } from 'react';
import { ChatFeed, Message } from 'react-chat-ui';

function ChatUI() {
  const [messages, setMessages] = useState([
    new Message({ id: 1, message: "Hi, how can I help you?", senderName: "Bot" }),
  ]);
  const [newMsg, setNewMsg] = useState("");

  const handleSend = () => {
    if (newMsg.trim() === "") return;

    const userMessage = new Message({ id: 0, message: newMsg });
    setMessages([...messages, userMessage]);
    setNewMsg("");
  };

  return (
    <div style={{ maxWidth: 500, margin: "0 auto", padding: 20 }}>
      <ChatFeed
        messages={messages}
        hasInputField={false}
        showSenderName={true}
        bubblesCentered={false}
      />
      <input
        type="text"
        value={newMsg}
        onChange={(e) => setNewMsg(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Type a message..."
        style={{
          width: "100%",
          padding: 10,
          fontSize: 16,
          marginTop: 10,
          borderRadius: 5,
          border: "1px solid #ccc",
        }}
      />
    </div>
  );
}

export default ChatUI;
