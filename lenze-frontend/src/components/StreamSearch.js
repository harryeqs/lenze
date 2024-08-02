// src/components/StreamSearch.js
import React, { useState } from 'react';
import { webSearchStream } from '../api';

const StreamSearch = () => {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = () => {
        setLoading(true);
        setMessages([]);
        webSearchStream(query, (data) => {
            setMessages((prevMessages) => [...prevMessages, data]);
            if (!data.status) {
                setLoading(false);
            }
        });
    };

    return (
        <div>
            <h1>Stream Search</h1>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query"
            />
            <button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>
            <div>
                <h2>Streaming Messages</h2>
                <ul>
                    {messages.map((msg, index) => (
                        <li key={index}>
                            {msg.status ? (
                                <p>{msg.status}</p>
                            ) : (
                                <div>
                                    <h3>Answer</h3>
                                    <p>{msg.answer}</p>
                                    <h4>Sources</h4>
                                    <ul>
                                        {msg.sources.map((source, idx) => (
                                            <li key={idx}>
                                                <a href={source} target="_blank" rel="noopener noreferrer">{source}</a>
                                            </li>
                                        ))}
                                    </ul>
                                    <h4>Related Queries</h4>
                                    <ul>
                                        {msg.related.map((relatedQuery, idx) => (
                                            <li key={idx}>{relatedQuery}</li>
                                        ))}
                                    </ul>
                                    <p>{msg.time_taken}</p>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default StreamSearch;
