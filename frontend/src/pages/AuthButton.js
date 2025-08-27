import React from "react";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../auth/authConfig";
import "./AuthButton.css";

const AuthButton = () => {
  const { instance } = useMsal();
  const activeAccount = instance.getActiveAccount();

  const handleLogin = () => {
    instance.loginRedirect({ ...loginRequest }).catch(e => console.error(e));
  };

  const handleLogout = () => {
    instance.logoutRedirect().catch(e => console.error(e));
  };

    return (
    <div className="auth-wrapper">
      {activeAccount && (
        <div className="user-badge">
          <span className="avatar">{activeAccount.name.charAt(0)}</span>
          <span className="username">Hello, {activeAccount.name}!</span>
        </div>
      )}
      <button
        className={`auth-button ${activeAccount ? "logout" : "login"}`}
        onClick={activeAccount ? handleLogout : handleLogin}
      >
        {activeAccount ? "Sign Out" : "Sign In"}
      </button>
    </div>
  );
};
export default AuthButton;
