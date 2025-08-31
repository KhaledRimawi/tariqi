import React, { useEffect, useState } from "react";
import "./Home.css";
import PushNotificationSetup from "./PushNotificationSetup";

// Helper: Get current geolocation
const getLocation = () => {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("Geolocation not supported"));
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                resolve({
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                });
            },
            (err) => reject(err),
            { enableHighAccuracy: true }
        );
    });
};

const Home = ({ setNotificationStatus }) => {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [city, setCity] = useState("");
    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                
                const backendUrl = process.env.REACT_APP_BACKEND_URL;
                let url = "";

                // Case 1: No city → nearby checkpoints (Primary Cards)
                if (!city) {
                    try {
                        const position = await getLocation();
                        const userLat = position.latitude;
                        const userLng = position.longitude;

                        url = `${backendUrl}/api/near_location?latitude=${userLat}&longitude=${userLng}`;
                        const response = await fetch(url);
                        const data = await response.json();

                        if (data.success && data.checkpoints) {
                            const grouped = {};
                            data.checkpoints.forEach((cp) => {
                                const key = `${cp.city}-${cp.checkpoint}`;
                                if (!grouped[key]) {
                                    grouped[key] = {
                                        name: cp.checkpoint,
                                        city: cp.city,
                                        entry: null,
                                        exit: null,
                                    };
                                }

                                const rawTime = cp.updatedAt?.$date || null;

                                if (cp.status) {
                                    const statusBlock = formatStatus(
                                        { ...cp, rawTime },
                                        true // We specify that it is Primaryry
                                    );

                                    if (
                                        cp.direction === "الداخل" || cp.direction === "دخول" || cp.direction === "الدخول" || cp.direction === "داخل"
                                    ) {
                                        grouped[key].entry = { ...statusBlock, rawTime };
                                    } else if (
                                        cp.direction === "الخارج" || cp.direction === "خروج" || cp.direction === "الخروج" || cp.direction === "خارج"
                                    ) {
                                        grouped[key].exit = { ...statusBlock, rawTime };
                                    } else if (cp.direction === "الاتجاهين") {
                                        grouped[key].entry = { ...statusBlock, rawTime };
                                        grouped[key].exit = { ...statusBlock, rawTime };
                                    }
                                }
                            });

                            setCards(Object.values(grouped));
                            return;
                        }
                    } catch (geoErr) {
                        console.warn("Geolocation error:", geoErr.message);
                    }
                }

                // Case 2: With city → query (Secondary Cards)
                url = `${backendUrl}/api/checkpoints/query?top=100`;
                if (search) url += `&checkpoint=${encodeURIComponent(search)}`;
                if (city) url += `&city=${encodeURIComponent(city)}`;

                const response = await fetch(url);
                const data = await response.json();

                if (data.results) {
                    const filtered = data.results.filter((item) => {
                        const cityName = item.city_name || item.city || "";
                        const checkpointName = item.checkpoint_name || "";
                        if (!cityName || !checkpointName) return false;
                        if (cityName === "غير محدد" || checkpointName === "غير محدد") return false;
                        if (city && cityName !== city) return false;
                        return true;
                    });

                    const grouped = {};
                    filtered.forEach((item) => {
                        const checkpointName = item.checkpoint_name;
                        const cityName = item.city_name || item.city;
                        const key = `${cityName}-${checkpointName}`;

                        if (!grouped[key]) {
                            grouped[key] = {
                                name: checkpointName,
                                city: cityName,
                                entry: null,
                                exit: null,
                            };
                        }

                        const rawTime = item.message_date;

                        const statusBlock = formatStatus(
                            { ...item, rawTime },
                            false // Secondary (not Primary)
                        );

                        if (
                            item.direction === "الداخل" || item.direction === "دخول" || item.direction === "الدخول" || item.direction === "داخل"
                        ) {
                            if (
                                !grouped[key].entry ||
                                new Date(rawTime) > new Date(grouped[key].entry.rawTime)
                            ) {
                                grouped[key].entry = { ...statusBlock, rawTime };
                            }
                        } else if (
                            item.direction === "الخارج" || item.direction === "خروج" || item.direction === "الخروج" || item.direction === "خارج"
                        ) {
                            if (
                                !grouped[key].exit ||
                                new Date(rawTime) > new Date(grouped[key].exit.rawTime)
                            ) {
                                grouped[key].exit = { ...statusBlock, rawTime };
                            }
                        } else if (item.direction === "الاتجاهين") {
                            if (
                                !grouped[key].entry ||
                                new Date(rawTime) > new Date(grouped[key].entry.rawTime)
                            ) {
                                grouped[key].entry = { ...statusBlock, rawTime };
                            }
                            if (
                                !grouped[key].exit ||
                                new Date(rawTime) > new Date(grouped[key].exit.rawTime)
                            ) {
                                grouped[key].exit = { ...statusBlock, rawTime };
                            }
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

    // Helper: Format status with colors
    const formatStatus = (item, isPrimary) => {
        let statusColor = { color: "#c8e6c9", textColor: "#2e7d32" };

        if (
            item.status.includes("سالك") || item.status.includes("مفتوح") || item.status.includes("فاتح") || item.status.includes("بحري")
        ) {
            statusColor = { color: "#c8e6c9", textColor: "#2e7d32" };
        } else if (item.status.includes("أزمة") || item.status.includes("مزدحم")) {
            statusColor = { color: "#fff6a5", textColor: "#8a6d03" };
        } else if (item.status.includes("حاجز/تفتيش")) {
            statusColor = { color: "#ffe0b2", textColor: "#e65100" };
        } else if (
            item.status.includes("مغلق") || item.status.includes("إغلاق") || item.status.includes("مسكر")
        ) {
            statusColor = { color: "#ffcdd2", textColor: "#c62828" };
        }

        // Time coordination
        let formattedTime = "";
        if (item.rawTime) {
            const d = new Date(item.rawTime);
            if (!isNaN(d)) {
                if (isPrimary) { 
                    formattedTime = d.toLocaleTimeString("ar-EG", {
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: true,
                        timeZone: "UTC",
                    });
                } else {
                    formattedTime = d.toLocaleTimeString("ar-EG", {
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: true,
                    });
                }
            }
        }

        return {
            status: item.status,
            time: formattedTime,
            color: statusColor.color,
            textColor: statusColor.textColor,
        };
    };

    return (
        <div className="home-container">
            <div className="home-content container">
                <h1 className="title">أحوال الحواجز والطرق</h1>
                <p className="subtitle">🚗💨 رافقتم السلامة 💙</p>

                {/* اختيار المدينة */}
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

                {/* البحث */}
                <div className="search-container">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="ابحث في جميع الحواجز"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {/* النتائج */}
                {loading ? (
                    <p>⏳ جاري تحميل البيانات...</p>
                ) : cards.length === 0 ? (
                    <p>❌ لا توجد بيانات مطابقة</p>
                ) : (
                    cards.map((card, index) => (
                        <div className="card" key={index}>
                            <h2>
                                {card.city} - {card.name}
                            </h2>
                            <hr />
                            <div className="card-status">
                                {/* الدخول */}
                                <div
                                    className="status-block"
                                    style={{
                                        backgroundColor: card.entry?.color || "#f0f0f0",
                                        color: card.entry?.textColor || "#555",
                                    }}
                                >
                                    <div className="status-title">الدخول</div>
                                    <div>{card.entry ? card.entry.status : "—"}</div>
                                    <div className="status-time">{card.entry ? card.entry.time : ""}</div>
                                </div>

                                {/* الخروج */}
                                <div
                                    className="status-block"
                                    style={{
                                        backgroundColor: card.exit?.color || "#f0f0f0",
                                        color: card.exit?.textColor || "#555",
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

                {/* Push notifications */}
                <PushNotificationSetup setNotificationStatus={setNotificationStatus} />
            </div>
        </div>
    );
};

export default Home;
