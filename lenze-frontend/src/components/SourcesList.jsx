import React from 'react';

const SourcesList = ({ sources }) => {
    if (sources.length === 0) return null;

    return (
        <div>
            <h3>Sources</h3>
            <ol>
                {sources.map((source, index) => (
                    <li key={index}>
                        <a href={source.link} target="_blank" rel="noopener noreferrer">
                            {source.title}
                        </a>
                    </li>
                ))}
            </ol>
        </div>
    );
};

export default SourcesList;
