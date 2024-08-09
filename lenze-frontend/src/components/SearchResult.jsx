// src/components/SearchResult.js
import React from 'react';
import ReactMarkdown from 'react-markdown';

const SearchResult = ({ result }) => {
    if (!result) {
        return null;
    }

    const { answer, related, time_taken } = result;

    return (
        <div>
            <h2>Answer</h2>
            <ReactMarkdown>{answer}</ReactMarkdown>
            <h3>Related</h3>
            <ul>
                {Array.isArray(related) ? related.map((relatedQuery, index) => (
                    <li key={index}>{relatedQuery}</li>
                )) : null}
            </ul>
            <p>{time_taken}</p>
        </div>
    );
};

export default SearchResult;
