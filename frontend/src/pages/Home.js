import React, { useEffect, useState } from "react";
import { Search, MapPin, Clock, AlertCircle, CheckCircle, XCircle, Navigation } from "lucide-react";
import "./Home.css";
import PushNotificationSetup from "./PushNotificationSetup";
import { formatCheckpointTime } from "../utils/timeFormat";


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
    const [nearbyMode, setNearbyMode] = useState(true);

    const cities = [
        "نابلس", "سلفيت", "رام الله", "بيت لحم", "الخليل", 
        "جنين", "طولكرم", "قلقيلية", "اريحا(طوباس)", "القدس"
    ];

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                
                const backendUrl = process.env.REACT_APP_BACKEND_URL;
                let url = "";

                // Case 1: Nearby mode - get checkpoints near user location
                if (nearbyMode && !city && !search) {
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
                                        true // Primary data
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

                // Case 2: Search mode - query by city/search term
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

                            const rawTime = item.message_date?.$date || item.updatedAt?.$date || null;   /// why do we need updated at since when i removed it still time appeared but when removed item.messagedate the date gone 

                            const statusBlock = formatStatus({ ...item, rawTime });

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
    }, [city, search, nearbyMode]);

    // Helper: Format status with colors
    const formatStatus = (item) => {
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

    const { absolute, relative } = formatCheckpointTime(item.rawTime);
        return {
            status: item.status,
            time: relative,      
            absoluteTime: absolute,
            color: statusColor.color,
            textColor: statusColor.textColor,
        };
    };

    const getStatusIcon = (status) => {
        if (status.includes("سالك") || status.includes("مفتوح") || status.includes("فاتح")) {
            return <CheckCircle className="status-icon" />;
        } else if (status.includes("أزمة") || status.includes("مزدحم")) {
            return <AlertCircle className="status-icon" />;
        } else if (status.includes("مغلق") || status.includes("إغلاق")) {
            return <XCircle className="status-icon" />;
        }
        return <Clock className="status-icon" />;
    };

    return (
        <div className="home-container">
            {/* Header Section */}
            <div className="header-section">
                <div className="header-content">
                    <div className="title-section">
                        <h1 className="main-title">أحوال الحواجز والطرق</h1>
                        <p className="subtitle">تحديثات مباشرة لأوضاع المرور</p>
                    </div>

                    {/* Controls Section */}
                    <div className="controls-section">
                        {/* Mode Toggle */}
                        <div className="mode-toggle">
                            <button
                                  onClick={() => {
                                    setCity("");     
                                    setSearch("");   
                                    setNearbyMode(true);
                                }}
                                className={`mode-button ${nearbyMode ? 'active' : ''}`}
                            >
                                <Navigation className="mode-icon" />
                                الحواجز القريبة
                            </button>
                            <button
                                onClick={() => setNearbyMode(false)}
                                className={`mode-button ${!nearbyMode ? 'active' : ''}`}
                            >
                                <Search className="mode-icon" />
                                البحث المتقدم
                            </button>
                        </div>

                        {/* Search Controls */}
                        {!nearbyMode && (
                            <div className="search-controls">
                                {/* City Selector */}
                                <div className="input-wrapper">
                                    <MapPin className="input-icon" />
                                    <select 
                                        value={city} 
                                        onChange={(e) => setCity(e.target.value)}
                                        className="city-select"
                                    >
                                        <option value="">اختر مدينة</option>
                                        {cities.map((cityName) => (
                                            <option key={cityName} value={cityName}>
                                                {cityName}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Search Input */}
                                <div className="input-wrapper">
                                    <Search className="input-icon" />
                                    <input
                                        type="text"
                                        placeholder="ابحث في جميع الحواجز"
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                        className="search-input"
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {loading ? (
                    <div className="loading-section">
                        <div className="loading-spinner"></div>
                        <p className="loading-text">⏳ جاري تحميل البيانات...</p>
                    </div>
                ) : cards.length === 0 ? (
                    <div className="empty-section">
                        <div className="empty-card">
                            <AlertCircle className="empty-icon" />
                            <p className="empty-text">❌ لا توجد بيانات مطابقة</p>
                        </div>
                    </div>
                ) : (
                    <div className="cards-grid">
                        {cards.map((card, index) => (
                            <div key={index} className="checkpoint-card">
                                {/* Card Header */}
                                <div className="card-header">
                                    <h2 className="card-title">
                                        <MapPin className="card-icon" />
                                        {card.city} - {card.name}
                                    </h2>
                                </div>

                                {/* Status Grid */}
                                <div className="card-content">
                                    <div className="status-grid">
                                        {/* Entry Status */}
                                        <div 
                                            className="status-block"
                                            style={{
                                                backgroundColor: card.entry?.color || "#f5f5f5",
                                                color: card.entry?.textColor || "#666",
                                                borderColor: card.entry?.textColor || "#ddd"
                                            }}
                                        >
                                            <div className="status-header">
                                                <span className="status-label">الدخول</span>
                                                {card.entry && getStatusIcon(card.entry.status)}
                                            </div>
                                            <div className="status-value">
                                                {card.entry ? card.entry.status : "—"}
                                            </div>
                                            {card.entry?.time && (
                                                <div className="status-time">
                                                    <Clock className="time-icon" />
                                                    {card.entry.time}
                                                </div>
                                            )}
                                        </div>

                                        {/* Exit Status */}
                                        <div 
                                            className="status-block"
                                            style={{
                                                backgroundColor: card.exit?.color || "#f5f5f5",
                                                color: card.exit?.textColor || "#666",
                                                borderColor: card.exit?.textColor || "#ddd"
                                            }}
                                        >
                                            <div className="status-header">
                                                <span className="status-label">الخروج</span>
                                                {card.exit && getStatusIcon(card.exit.status)}
                                            </div>
                                            <div className="status-value">
                                                {card.exit ? card.exit.status : "—"}
                                            </div>
                                            {card.exit?.time && (
                                                <div className="status-time">
                                                    <Clock className="time-icon" />
                                                    {card.exit.time}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Push Notifications */}
                <div className="notifications-section">
                    <PushNotificationSetup setNotificationStatus={setNotificationStatus} />
                </div>

                {/* Footer Section */}
                <div className="footer-section">
                    <div className="footer-card">
                        <p className="footer-text">💡 تحديثات مباشرة من مصادر موثوقة</p>
                        <div className="status-legend">
                            <span className="legend-item green">مفتوح/سالك</span>
                            <span className="legend-item yellow">أزمة مرورية</span>
                            <span className="legend-item orange">حاجز/تفتيش</span>
                            <span className="legend-item red">مغلق</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;