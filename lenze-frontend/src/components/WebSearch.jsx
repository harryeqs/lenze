// src/components/WebSearch.js
import React, { useState } from 'react';
import { webSearch } from '../api';
import SearchForm from './SearchForm';
import SearchResult from './SearchResult';

const WebSearch = () => {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (query) => {
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const response = await webSearch(query);
            setResult(response);
        } catch (err) {
            setError('Failed to fetch search results');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Web Search</h1>
            <SearchForm onSearch={handleSearch} />
            {loading && <p>Loading...</p>}
            {error && <p>{error}</p>}
            <SearchResult result={result} />
        </div>
    );
};

export default WebSearch;
