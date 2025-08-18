import React, { useState } from 'react';
import './FeedbackPage.css';

const FeedbackPage = () => {
  const [selectedOption, setSelectedOption] = useState('');

  const options = [
    { text: 'داخل ومفتوح', color: '#c8e6c9', textColor: '#2e7d32' }, // Green
    { text: 'داخل ومغلق', color: '#ffcdd2', textColor: '#c62828' }, // Red
    { text: 'خارج ومفتوح', color: '#c8e6c9', textColor: '#2e7d32' }, // Green
    { text: 'خارج ومغلق', color: '#ffcdd2', textColor: '#c62828' }  // Red
  ];

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch('http://localhost:5000/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: selectedOption }),
    })
      .then((res) => res.json())
      .then(() => {
        alert('✅ تم إرسال الملاحظة بنجاح!');
        setSelectedOption('');
      })
      .catch((err) => {
        console.error('Error submitting feedback:', err);
      });
  };

  return (
    <div className="feedback-page-container">
      <h1 className="feedback-page-title">💬 صفحة الملاحظات</h1>
      <p className="feedback-page-subtitle">ساهم بمعلومة تفيد الجميع 🙏</p>

      <form className="feedback-form" onSubmit={handleSubmit}>
        <h2>اختر حالتك</h2>
        <div className="feedback-options">
          {options.map((opt, index) => (
            <div
              key={index}
              onClick={() => setSelectedOption(opt.text)}
              className={`feedback-option ${selectedOption === opt.text ? 'selected' : ''}`}
              style={{ backgroundColor: opt.color, color: opt.textColor }}
            >
              {opt.text}
            </div>
          ))}
        </div>

        <div className="feedback-buttons">
          <button type="submit" disabled={!selectedOption} className="submit-btn">
            ✅ إرسال
          </button>
          <button type="button" onClick={() => setSelectedOption('')} className="cancel-btn">
            ❌ إلغاء
          </button>
        </div>
      </form>
    </div>
  );
};

export default FeedbackPage;
