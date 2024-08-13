import React from 'react';

const RelatedQueries = ({ queries }) => {
    if (queries.length === 0) return null;

    return (
        <div>
            <h3>Related</h3>
            <ul>
                {queries.map((query, index) => (
                    <li key={index}>{query}</li>
                ))}
            </ul>
        </div>
    );
};

export default RelatedQueries;
