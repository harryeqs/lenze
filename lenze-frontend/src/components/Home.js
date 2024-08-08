import React from 'react';
import { useNavigate } from 'react-router-dom';
import SearchForm from './SearchForm';

const API_URL = 'http://localhost:8000';

const Home = () => {
    const navigate = useNavigate();

    const handleSearch = async (query) => {
        try {
            const res = await fetch(`${API_URL}/start-session`, { method: 'POST' });
            const data = await res.json();
            navigate(`/stream/${data.session_id}?query=${encodeURIComponent(query)}`);
        } catch (err) {
            console.error('Failed to start new session:', err);
        }
    };

    return (
        <div>
            <h1>Start a New Search</h1>
            <SearchForm onSearch={handleSearch} />
            <button onClick={() => navigate('/history')}>View Search History</button>
        </div>
    );
};

export default Home;
