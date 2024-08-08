import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:8000';

const SearchHistory = () => {
    const [history, setHistory] = useState([]);
    const navigate = useNavigate(); // useNavigate hook from react-router-dom

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await axios.get(`${API_URL}/search-history`);
                setHistory(response.data);
            } catch (error) {
                console.error('Error fetching search history:', error);
            }
        };

        fetchHistory();
    }, []);

    const enterSession = (sessionId) => {
        navigate(`/stream/${sessionId}`);
    };

    return (
        <div>
            <h1>Search History</h1>
            {history.length === 0 ? (
                <p>No search history available.</p>
            ) : (
                <ul>
                    {history.map((session) => (
                        <li key={session.session_id}>
                            <button onClick={() => enterSession(session.session_id)}>
                                Enter Session {session.session_id} - {session.first_query}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
            <button onClick={() => navigate('/')}>Start New Session</button>
        </div>
    );
};

export default SearchHistory;
