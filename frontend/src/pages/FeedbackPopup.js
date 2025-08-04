import React, { useState } from 'react';

const FeedbackPopup = ({ onClose }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch('http://localhost:5000/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
      .then((res) => res.json())
      .then((data) => {
        alert('Feedback submitted!');
        onClose();
      })
      .catch((err) => {
        console.error('Error submitting feedback:', err);
      });
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.popup}>
        <h3>Send Feedback</h3>
        <form onSubmit={handleSubmit}>
          <textarea
            rows="4"
            style={styles.textarea}
            placeholder="Your feedback..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
          />
          <br />
          <button type="submit" style={styles.button}>Submit</button>
          <button onClick={onClose} style={styles.button}>Cancel</button>
        </form>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center',
  },
  popup: {
    background: '#fff', padding: '20px', borderRadius: '8px', width: '300px',
  },
  textarea: {
    width: '100%', padding: '10px',
  },
  button: {
    marginTop: '10px', marginRight: '10px', padding: '5px 10px',
  },
};

export default FeedbackPopup;
