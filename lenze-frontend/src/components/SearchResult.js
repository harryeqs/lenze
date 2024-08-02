// src/components/SearchResult.js
import React from 'react';
import ReactMarkdown from 'react-markdown';

const SearchResult = ({ result }) => {
    if (!result) {
        return null;
    }

    const { answer, sources, related, time_taken } = result;

    return (
        <div>
            <h2>Answer</h2>
            <ReactMarkdown>{answer}</ReactMarkdown>
            <h3>Sources</h3>
            <ul>
                {sources.map((source, index) => (
                    <li key={index}>
                        <a href={source} target="_blank" rel="noopener noreferrer">{source}</a>
                    </li>
                ))}
            </ul>
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
