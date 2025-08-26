import React from 'react';
import './DestinationSearch.css';

const DestinationSearch = () => {
    const cards = [
        {
            name: 'دير شرف',
            entry: { status: 'أزمة ⚠️', time: 'منذ 54 دقيقة', color: '#fff6a5', textColor: '#8a6d03' },
            exit: { status: 'أزمة ⚠️', time: 'منذ 54 دقيقة', color: '#fff6a5', textColor: '#8a6d03' }
        },
        {
            name: 'بيت ايل',
            entry: { status: 'سالك ✅', time: 'منذ 10 دقائق', color: '#c8e6c9', textColor: '#2e7d32' },
            exit: { status: 'سالك ✅', time: 'منذ 15 دقيقة', color: '#c8e6c9', textColor: '#2e7d32' }
        },
        {
            name: 'بوابة كفل حارس',
            entry: { status: 'مغلق ❌', time: 'منذ ساعة', color: '#ffcdd2', textColor: '#c62828' },
            exit: { status: 'أزمة ⚠️', time: 'منذ 30 دقيقة', color: '#fff6a5', textColor: '#8a6d03' }
        },
    ];

    return (
        <div className="container">
            <h1 className="title">أحوال الحواجز والطرق</h1>

            <p className="subtitle">🚗💨 رافقتم السلامة 💙</p>

            <div className="input-group-container">
                <label htmlFor="city-select">📍</label>
                <select id="city-select" defaultValue="">
                    <option value="" disabled>اختر مدينة</option>
                    <option value={1}>نابلس</option>
                    <option value={2}>سلفيت</option>
                    <option value={3}>رام الله</option>
                    <option value={4}>بيت لحم</option>
                    <option value={5}>الخليل</option>
                    <option value={6}>جنين</option>
                    <option value={7}>طولكرم</option>
                    <option value={8}>قلقيلية</option>
                    <option value={9}>اريحا(طوباس)</option>
                    <option value={10}>القدس</option>
                </select>
            </div>

            <div className="search-container">
                <span className="search-icon">🔍</span>
                <input type="text" placeholder="ابحث في جميع الحواجز" />
            </div>

            {cards.map((card) => (
                <div className="card" key={card.name}>
                    <h2>{card.name}</h2>
                    <hr />
                    <div className="card-status">
                        <div className="status-block" style={{ backgroundColor: card.entry.color, color: card.entry.textColor }}>
                            <div className="status-title">الدخول</div>
                            <div>{card.entry.status}</div>
                            <div className="status-time">{card.entry.time}</div>
                        </div>
                        <div className="status-block" style={{ backgroundColor: card.exit.color, color: card.exit.textColor }}>
                            <div className="status-title">الخروج</div>
                            <div>{card.exit.status}</div>
                            <div className="status-time">{card.exit.time}</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default DestinationSearch;
