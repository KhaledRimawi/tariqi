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
    <button className="auth-button" onClick={activeAccount ? handleLogout : handleLogin}>
      {activeAccount ? "Sign Out" : "Sign In"}
    </button>
  );
};

export default AuthButton;
