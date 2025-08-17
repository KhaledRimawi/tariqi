import React, { useEffect, useState } from 'react';
import Card from './Card';
import './Cards.css';

const Cards = () => {
    const [checkpoints, setCheckpoints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCheckpoints = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/data/show`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                
                setCheckpoints(data);
                setLoading(false);
            } catch (e) {
                console.error("Could not fetch checkpoint data:", e);
                setError("Could not fetch data. Please check the server connection.");
                setLoading(false);
            }
        };

        fetchCheckpoints();
    }, []);

    if (loading) {
        return <div className="cards-container">Loading...</div>;
    }

    if (error) {
        return <div className="cards-container error">{error}</div>;
    }
    
    return (
        <div className="cards-container">
            <h2>Checkpoints Status</h2>
            {checkpoints.length > 0 ? (
                checkpoints.map((checkpoint) => (
                    <Card key={checkpoint._id} checkpoint={checkpoint} />
                ))
            ) : (
                <p>No checkpoints found.</p>
            )}
        </div>
    );
};

export default Cards;