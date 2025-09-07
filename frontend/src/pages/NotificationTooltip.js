import React from "react";
import "./NotificationTooltip.css";

const NotificationTooltip = ({ status }) => {
  // Determine the message based on notification status
  const message =
    status === "denied"
      ? "الإشعارات مغلقة. فعّلها للحصول على تحديثات الحواجز مباشرة"
      : "متصفحك لا يدعم الإشعارات";

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
