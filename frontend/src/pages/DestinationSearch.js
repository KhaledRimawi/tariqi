import React, { useEffect, useState } from 'react';
import './DestinationSearch.css';

const DestinationSearch = () => {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [city, setCity] = useState("");
    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                
                const backendUrl = process.env.REACT_APP_BACKEND_URL;
                let url = `${backendUrl}/api/checkpoints/query?top=50`;

                if (search) url += `&checkpoint=${encodeURIComponent(search)}`;
                if (city) url += `&city=${encodeURIComponent(city)}`;

                const response = await fetch(url);
                const data = await response.json();

                if (data.results) {
                    const filtered = data.results
                        .filter(item => {
                            const cityName = item.city_name || item.city || "";
                            const checkpointName = item.checkpoint_name || "";
                            // Do not display if the city or checkpoin is unspecified or empty
                            if (!cityName || !checkpointName) return false;
                            if (cityName === "غير محدد" || checkpointName === "غير محدد") return false;
                            if (city && cityName !== city) return false;
                            return true;
                        });

                    // We collect the results according to the checkpoin + city
                    const grouped = {};
                    filtered.forEach(item => {
                        const checkpointName = item.checkpoint_name;
                        const cityName = item.city_name || item.city;
                        const key = `${cityName}-${checkpointName}`;

                        if (!grouped[key]) {
                            grouped[key] = {
                                name: checkpointName,
                                city: cityName,
                                entry: null,
                                exit: null
                            };
                        }

                        const statusColor = item.status.includes("مزدحم")
                            ? { color: "#fff6a5", textColor: "#8a6d03" }
                            : item.status.includes("مغلق")
                                ? { color: "#ffcdd2", textColor: "#c62828" }
                                : { color: "#c8e6c9", textColor: "#2e7d32" };

                        const statusBlock = {
                            status: item.status,
                            time: new Date(item.message_date).toLocaleTimeString("ar-EG", {
                                hour: "2-digit",
                                minute: "2-digit"
                            }),
                            color: statusColor.color,
                            textColor: statusColor.textColor
                        };

                        if (item.direction === "الداخل") {
                            grouped[key].entry = statusBlock;
                        } else if (item.direction === "الخارج") {
                            grouped[key].exit = statusBlock;
                        }
                    });

                    setCards(Object.values(grouped));
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [city, search]);

    return (
        <div className="container">
            <h1 className="title">أحوال الحواجز والطرق</h1>

            <p className="subtitle">🚗💨 رافقتم السلامة 💙</p>

            <div className="input-group-container">
                <label htmlFor="city-select">📍</label>
                <select id="city-select" value={city} onChange={(e) => setCity(e.target.value)}>
                    <option value="">اختر مدينة</option>
                    <option value="نابلس">نابلس</option>
                    <option value="سلفيت">سلفيت</option>
                    <option value="رام الله">رام الله</option>
                    <option value="بيت لحم">بيت لحم</option>
                    <option value="الخليل">الخليل</option>
                    <option value="جنين">جنين</option>
                    <option value="طولكرم">طولكرم</option>
                    <option value="قلقيلية">قلقيلية</option>
                    <option value="اريحا">اريحا(طوباس)</option>
                    <option value="القدس">القدس</option>
                </select>
            </div>

            <div className="search-container">
                <span className="search-icon">🔍</span>
                <input
                    type="text"
                    placeholder="ابحث في جميع الحواجز"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>

            {loading ? (
                <p>⏳ جاري تحميل البيانات...</p>
            ) : cards.length === 0 ? (
                <p>❌ لا توجد بيانات مطابقة</p>
            ) : (
                cards.map((card, index) => (
                    <div className="card" key={index}>
                        <h2>{card.city} - {card.name}</h2>
                        <hr />
                        <div className="card-status">
                            <div
                                className="status-block"
                                style={{
                                    backgroundColor: card.entry?.color || "#f0f0f0",
                                    color: card.entry?.textColor || "#555"
                                }}
                            >
                                <div className="status-title">الدخول</div>
                                <div>{card.entry ? card.entry.status : "—"}</div>
                                <div className="status-time">{card.entry ? card.entry.time : ""}</div>
                            </div>
                            <div
                                className="status-block"
                                style={{
                                    backgroundColor: card.exit?.color || "#f0f0f0",
                                    color: card.exit?.textColor || "#555"
                                }}
                            >
                                <div className="status-title">الخروج</div>
                                <div>{card.exit ? card.exit.status : "—"}</div>
                                <div className="status-time">{card.exit ? card.exit.time : ""}</div>
                            </div>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default DestinationSearch;
