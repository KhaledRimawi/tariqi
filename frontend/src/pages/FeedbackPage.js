import React, { useState , useEffect } from 'react';
import './FeedbackPage.css';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../auth/authConfig";
import SignInModal from "./SignIn";
const FeedbackPage = () => {
  const { instance } = useMsal();
  const activeAccount = instance.getActiveAccount();

  const [modalOpen, setModalOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');

  const options = [
    { text: 'داخل ومفتوح', color: '#c8e6c9', textColor: '#2e7d32' }, // Green
    { text: 'داخل ومغلق', color: '#ffcdd2', textColor: '#c62828' }, // Red
    { text: 'خارج ومفتوح', color: '#c8e6c9', textColor: '#2e7d32' }, // Green
    { text: 'خارج ومغلق', color: '#ffcdd2', textColor: '#c62828' }  // Red
  ];

  useEffect(() => {
    if (!activeAccount) {
      setModalOpen(true); 
    }
  }, [activeAccount]);

  const handleSignIn = () => {
    instance.loginRedirect({ ...loginRequest }); 
  };

  const handleCloseModal = () => setModalOpen(false);

  const handleSubmit = (e) => {
    e.preventDefault();
  
    if (!activeAccount) {
      setModalOpen(true); // force sign-in if not logged in
      return;
    }

     if (!navigator.geolocation) {
    alert("❌ Geolocation is not supported by your browser");
    return;
  }

  // Map the selected option to status and direction
  const optionMap = {
    "داخل ومفتوح": { status: "مفتوح", direction: "داخل" },
    "داخل ومغلق": { status: "مغلق", direction: "داخل" },
    "خارج ومفتوح": { status: "مفتوح", direction: "خارج" },
    "خارج ومغلق": { status: "مغلق", direction: "خارج" },
  };

  const { status, direction } = optionMap[selectedOption];

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const payload = {
        message: selectedOption,
        status,
        direction,
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      };

      fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("Inserted feedback:", data);
          alert("✅ تم إرسال الملاحظة بنجاح!");
          setSelectedOption("");
        })
        .catch((err) => {
          console.error("Error submitting feedback:", err);
          alert("❌ حدث خطأ أثناء إرسال الملاحظة");
        });
    },
    (err) => {
      console.error("Geolocation error:", err);
      alert("❌ لم نتمكن من الحصول على موقعك الحالي");
    }
  );
};



  return (
    <div className="feedback-page-container">
            {/* Sign-In Modal */}
      <SignInModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        onSignIn={handleSignIn}
      />
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
