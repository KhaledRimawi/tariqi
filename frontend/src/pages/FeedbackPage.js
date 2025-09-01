import React, { useState, useEffect, useRef } from 'react';
import './FeedbackPage.css';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../auth/authConfig";
import SignInModal from "./SignIn";

const FeedbackPage = () => {
  const { instance } = useMsal();
  const activeAccount = instance.getActiveAccount();

  const [modalOpen, setModalOpen] = useState(false);
  const [status, setStatus] = useState('');
  const [direction, setDirection] = useState('');
  const [closestCheckpoint, setClosestCheckpoint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [locationError, setLocationError] = useState('');

  // Add refs to prevent duplicate calls
  const isLocationFetched = useRef(false);
  const isLocationFetching = useRef(false);

  const statusOptions = [
    { text: 'مفتوح', color: '#c8e6c9', textColor: '#2e7d32' }, // Green
    { text: 'أزمة', color: '#fff3cd', textColor: '#856404' },   // Yellow
    { text: 'مغلق', color: '#ffcdd2', textColor: '#c62828' }   // Red
  ];

  const directionOptions = [
    { text: 'داخل', color: '#bbdefb', textColor: '#0d47a1' },
    { text: 'خارج', color: '#d1c4e9', textColor: '#4a148c' },
    { text: 'اتجاهين', color: '#c8e6c9', textColor: '#2e7d32' },
  ];

  useEffect(() => {
    if (!activeAccount) {
      setModalOpen(true);
    } else {
      // Only fetch location if not already fetched or fetching
      setModalOpen(false);
      if (!isLocationFetched.current && !isLocationFetching.current) {
        getCurrentLocationAndCheckpoint();
      }
    }
  }, [activeAccount]); // Keep activeAccount as dependency but add controls

  const getCurrentLocationAndCheckpoint = () => {
    // Prevent duplicate calls
    if (isLocationFetching.current || isLocationFetched.current) {
      return;
    }

    if (!navigator.geolocation) {
      setLocationError("❌ Geolocation is not supported by your browser");
      return;
    }

    isLocationFetching.current = true;
    setLoading(true);
    setLocationError('');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;

        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/closest-checkpoint?lat=${latitude}&lng=${longitude}`)
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              setClosestCheckpoint({
                name: data.checkpoint,
                city: data.city,
                distance: data.distance_km,
                latitude,
                longitude
              });
              isLocationFetched.current = true;
            } else {
              setLocationError("❌ لم نتمكن من العثور على أقرب حاجز");
            }
          })
          .catch(err => {
            console.error("Error fetching closest checkpoint:", err);
            setLocationError("❌ خطأ في الحصول على معلومات الحاجز");
          })
          .finally(() => {
            setLoading(false);
            isLocationFetching.current = false;
          });
      },
      (err) => {
        console.error("Geolocation error:", err);
        setLocationError("❌ لم نتمكن من الحصول على موقعك الحالي");
        setLoading(false);
        isLocationFetching.current = false;
      }
    );
  };

  const handleSignIn = () => {
    instance.loginRedirect({ ...loginRequest , 
      redirectUri: window.location.href,
    });
  };

  const handleCloseModal = () => setModalOpen(false);

  const handleRetryLocation = () => {
    // Reset the flags to allow retry
    isLocationFetched.current = false;
    isLocationFetching.current = false;
    getCurrentLocationAndCheckpoint();
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!activeAccount) {
      setModalOpen(true);
      return;
    }

    if (!status || !direction || !closestCheckpoint) return;

    const message = `${direction} و${status}`;

    const payload = {
      message,
      status,
      direction,
      latitude: closestCheckpoint.latitude,
      longitude: closestCheckpoint.longitude,
    };
  // Acquire access token first
  instance.acquireTokenSilent({
    ...loginRequest,
    account: activeAccount,
  })
    .then((tokenResponse) => {
      console.log("Sending access token:", tokenResponse.accessToken);
      return fetch(`${process.env.REACT_APP_BACKEND_URL}/api/feedback`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${tokenResponse.accessToken}`, 
        },
      body: JSON.stringify(payload),
      });
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Inserted feedback:", data);
        alert("✅ تم إرسال الملاحظة بنجاح!");
        setStatus("");
        setDirection("");
      })
      .catch((err) => {
        console.error("Error submitting feedback:", err);
        alert("❌ حدث خطأ أثناء إرسال الملاحظة");
      });
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

      {/* Loading State */}
      {loading && (
        <div className="location-info loading">
          <p>🔄 جاري تحديد موقعك...</p>
        </div>
      )}

      {/* Location Error */}
      {locationError && (
        <div className="location-info error">
          <p>{locationError}</p>
          <button onClick={handleRetryLocation} className="retry-btn">
            🔄 إعادة المحاولة
          </button>
        </div>
      )}

      {/* Closest Checkpoint Info */}
      {closestCheckpoint && !loading && (
        <div className="location-info success">
          <h3>📍 أقرب حاجز إليك</h3>
          <p><strong>اسم الحاجز:</strong> {closestCheckpoint.name}</p>
          <p><strong>المدينة:</strong> {closestCheckpoint.city}</p>
          <p><strong>المسافة:</strong> {closestCheckpoint.distance} كم</p>
        </div>
      )}

      <form className="feedback-form" onSubmit={handleSubmit}>
        <h2>اختر الحالة</h2>
        <div className="feedback-options">
          {statusOptions.map((opt, index) => (
            <div
              key={index}
              onClick={() => { setStatus(opt.text); setDirection(''); }}
              className={`feedback-option ${status === opt.text ? 'selected' : ''}`}
              style={{ backgroundColor: opt.color, color: opt.textColor }}
            >
              {opt.text}
            </div>
          ))}
        </div>

        {status && (
          <>
            <h2>اختر الاتجاه</h2>
            <div className="feedback-options">
              {directionOptions.map((opt, index) => (
                <div
                  key={index}
                  onClick={() => setDirection(opt.text)}
                  className={`feedback-option ${direction === opt.text ? 'selected' : ''}`}
                  style={{ backgroundColor: opt.color, color: opt.textColor }}
                >
                  {opt.text}
                </div>
              ))}
            </div>
          </>
        )}

        <div className="feedback-buttons">
          <button
            type="submit"
            disabled={!status || !direction || !closestCheckpoint || loading}
            className="submit-btn"
          >
            ✅ إرسال
          </button>
          <button
            type="button"
            onClick={() => { setStatus(''); setDirection(''); }}
            className="cancel-btn"
          >
            ❌ إلغاء
          </button>
        </div>
      </form>
    </div>
  );
};

export default FeedbackPage;