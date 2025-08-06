import React, { useEffect, useState } from 'react';

const CheckpointCard = () => {
    const [checkpoint, setCheckpoint] = useState(null);

    useEffect(() => {
        fetch('http://localhost:5000/api/checkpoints/random')
            .then(res => res.json())
            .then(data => setCheckpoint(data))
            .catch(err => console.error('Error fetching checkpoint:', err));
    }, []);

    if (!checkpoint) return <p className="text-center mt-5">جاري التحميل...</p>;

    const redStatuses = ["مغلق", "مسكر", "مزدحم", "ازمة", "مكهرب"];
    const greenStatuses = ["سالك", "مفتوح", "بحري"];


    const headerBgColor = redStatuses.includes(checkpoint.status)
        ? '#dc3545'
        : greenStatuses.includes(checkpoint.status)
            ? '#198754'
            : '#0d6efd';

    return (
        <div
            className="card m-3 shadow"
            style={{
                width: '300px',
                height: 'auto',
                lineHeight: '2.2',
                fontWeight: 'bold',
                textAlign: 'center',
            }}
        >
            <h5
                className="card-header text-white"
                style={{
                    fontSize: '1rem',
                    padding: '0.3rem 0.6rem',
                    fontWeight: 'bold',
                    backgroundColor: headerBgColor,
                }}
            >
                حاجز {checkpoint.checkpoint}
            </h5>
            <div className="card-body p-2" style={{ fontSize: '0.85rem' }}>
                <p className="card-title mb-1">المدينة: {checkpoint.city}</p>
                <p className="card-text mb-1">الحالة: {checkpoint.status}</p>
                <p className="card-text mb-1">الاتجاه: {checkpoint.direction}</p>
                <p className="card-text mb-0">
                    آخر تحديث: {new Date(checkpoint.updatedAt).toLocaleString('ar-EG')}
                </p>
            </div>
        </div>
    );
};

export default CheckpointCard;
