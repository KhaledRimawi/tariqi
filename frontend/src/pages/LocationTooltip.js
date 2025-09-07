import React from "react";
import "./LocationTooltip.css";
import { AlertTriangle } from "lucide-react";

const LocationTooltip = ({ status }) => {
    const message =
        status === "denied"
            ? "⚠️ تم رفض الوصول لموقعك. فعّل خدمة الموقع للحصول على تحديثات دقيقة."
            : "⚠️ متصفحك لا يدعم خدمة الموقع.";

    return (
        <div className="location-card">
            <div className="location-icon">
                <AlertTriangle size={28} />
            </div>
            <div className="location-message">
                {message}
            </div>
        </div>
    );
};

export default LocationTooltip;
