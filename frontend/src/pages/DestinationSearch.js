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
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            marginTop: '50px',
            gap: '20px',
            alignItems: 'center',
            padding: '0 20px',
        }}>
            <h1 style={{
                fontSize: '2rem',
                fontWeight: 'bold',
                marginBottom: '20px',
                textAlign: 'center',
                color: '#222'
            }}>
                أحوال الحواجز والطرق
            </h1>

            <p style={{
                fontSize: '1.2rem',
                color: '#555',
                fontStyle: 'italic',
                backgroundColor: '#f0f8ff',
                padding: '8px 15px',
                borderRadius: '12px',
                boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
            }}>
                🚗💨 رافقتم السلامة 💙
            </p>

            <div className="input-group mb-3" style={{ width: '600px', height: '50px' }}>
                <label className="input-group-text" htmlFor="inputGroupSelect01">
                    📍
                </label>
                <select
                    className="form-select centered-select"
                    id="inputGroupSelect01"
                    defaultValue=""
                >
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

            <div className="input-group input-group-sm mb-3" style={{ width: '400px', height: '50px' }}>
                <span className="input-group-text" id="search-icon">🔍</span>
                <input
                    type="text"
                    className="form-control centered-text"
                    placeholder="ابحث في جميع الحواجز"
                    aria-label="Sizing example input"
                    aria-describedby="search-icon"
                />
            </div>

            {cards.map((card) => (
                <div
                    key={card.name}
                    style={{
                        width: '600px',
                        padding: '20px',
                        borderRadius: '12px',
                        border: '1px solid #ddd',
                        boxShadow: '0 0 10px rgba(0,0,0,0.05)',
                        backgroundColor: '#fff',
                        textAlign: 'center',
                        fontFamily: 'Arial, sans-serif',
                        color: '#2b2b7d',
                        marginBottom: '15px'
                    }}
                >
                    <h2 style={{ marginBottom: '15px', fontWeight: 'bold' }}>{card.name}</h2>
                    <hr style={{ borderColor: '#c0c0e5' }} />

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '15px', gap: '15px' }}>
                        <div style={{
                            flex: 1,
                            backgroundColor: card.entry.color,
                            borderRadius: '10px',
                            padding: '10px',
                            fontSize: '0.9rem',
                            color: card.entry.textColor
                        }}>
                            <div style={{ fontWeight: 'bold' }}>الدخول</div>
                            <div>{card.entry.status}</div>
                            <div style={{ fontSize: '0.8rem' }}>{card.entry.time}</div>
                        </div>
                        <div style={{
                            flex: 1,
                            backgroundColor: card.exit.color,
                            borderRadius: '10px',
                            padding: '10px',
                            fontSize: '0.9rem',
                            color: card.exit.textColor
                        }}>
                            <div style={{ fontWeight: 'bold' }}>الخروج</div>
                            <div>{card.exit.status}</div>
                            <div style={{ fontSize: '0.8rem' }}>{card.exit.time}</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default DestinationSearch;
