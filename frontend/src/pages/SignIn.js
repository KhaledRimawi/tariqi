import React from "react";
import "./SignIn.css";
import { useNavigate } from "react-router-dom";

const SignIn = ({ isOpen, onSignIn }) => {

  const navigate = useNavigate();
  const handleCancel = () => {
    navigate("/"); // redirect to home
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-container">
        <h2>Sign In Required</h2>
        <p>Sign in first to submit your feedback.</p>

        <div className="modal-buttons">
          <button className="btn primary" onClick={onSignIn}>Sign In</button>
          <button className="btn secondary" onClick={handleCancel}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
