import React, { useState } from 'react';

const FeedbackPopup = ({ onClose }) => {
  const [selectedOption, setSelectedOption] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: selectedOption }),
    })
      .then((res) => res.json())
      .then(() => {
        alert('✅ Feedback submitted!');
        onClose();
      })
      .catch((err) => {
        console.error('Error submitting feedback:', err);
      });
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.popup}>
        <h2 style={styles.title}>💬 Feedback</h2>
        <form onSubmit={handleSubmit}>
          <div style={styles.options}>
            {['داخل ومفتوح', 'داخل ومغلق', 'خارج ومفتوح', 'خارج ومغلق'].map((option, index) => (
              <label key={index} style={styles.optionLabel}>
                <input
                  type="radio"
                  name="feedbackOption"
                  value={option}
                  checked={selectedOption === option}
                  onChange={(e) => setSelectedOption(e.target.value)}
                  required
                />
                {option}
              </label>
            ))}
          </div>

          <div style={styles.buttonContainer}>
            <button type="submit" style={{ ...styles.button, ...styles.submit }}>Submit</button>
            <button type="button" onClick={onClose} style={{ ...styles.button, ...styles.cancel }}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.6)', display: 'flex',
    justifyContent: 'center', alignItems: 'center', zIndex: 1000,
  },
  popup: {
    background: 'white',
    borderRadius: '16px',
    padding: '30px 25px',
    width: '90%',
    maxWidth: '400px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
    fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
  },
  title: {
    marginBottom: '15px',
    textAlign: 'center',
    color: '#333',
  },
  options: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '20px',
  },
  optionLabel: {
    fontSize: '14px',
    color: '#444',
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '10px',
  },
  button: {
    padding: '8px 16px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'background-color 0.3s ease',
  },
  submit: {
    backgroundColor: '#4CAF50',
    color: 'white',
  },
  cancel: {
    backgroundColor: '#e0e0e0',
    color: '#333',
  },
};

export default FeedbackPopup;
