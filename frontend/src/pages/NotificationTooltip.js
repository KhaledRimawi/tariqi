import React from "react";
import "./NotificationTooltip.css";

const NotificationTooltip = ({ status }) => {
  // Determine the message based on notification status
  const message =
    status === "denied"
      ? "Notifications are off. Turn them on to get live checkpoint updates."
      : "Your browser does not support notifications.";

  return (
    <div className="tooltip-container">
      <div className="icon-wrapper">
        <div className="borde-back">
          <div className="icon">⚠️</div>
        </div>
      </div>
      <div className="tooltip">{message}</div>
    </div>
  );
};

export default NotificationTooltip;
