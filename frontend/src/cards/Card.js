import React from 'react';
import './Cards.css';

// Helper function to get status color based on the status string
const getStatusColor = (status) => {
    switch (status) {
      case 'مغلق': // Closed
      case 'مسكر': // Another term for closed
      case 'مكهرب': // Electrified/tense (often implies closed/dangerous)
        return 'red';
      case 'مفتوح': // Open
      case 'سالك': // Clear/Smooth
      case 'بحري': // Clear (colloquial)
        return 'green';
      case 'ازمة': // Traffic jam/Crisis
      case 'مزدحم': // Crowded
        return 'orange';
      default:
        return 'gray'; // Default color for unknown status
    }
};

const Card = ({ checkpoint }) => {
    if (!checkpoint) {
        return null;
    }

    // Get the color and format the date
    const statusColor = getStatusColor(checkpoint.status);
    const date = new Date(checkpoint.message_date).toLocaleString('ar-SA', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });

    return (
        <div className={`card-container ${statusColor}`}>
            <h3 className="card-title">{checkpoint.checkpoint_name || 'N/A'}</h3>
            <p className="card-info">المدينة: {checkpoint.city_name || 'N/A'}</p>
            <p className="card-info">الوضع: {checkpoint.status || 'N/A'}</p>
            <p className="card-info">الاتجاه: {checkpoint.direction || 'N/A'}</p>
            <p className="card-info card-date">تاريخ الرسالة: {date}</p>
        </div>
    );
};

export default Card;