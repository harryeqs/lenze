import React from 'react';
import ReactMarkdown from 'react-markdown';

const ResponseDisplay = ({ response }) => {
    return (
        <div style={{
            whiteSpace: 'normal',
            wordBreak: 'break-word',
            hyphens: 'auto',
            overflowWrap: 'break-word'
        }}>
            <ReactMarkdown>{response}</ReactMarkdown>
        </div>
    );
};

export default ResponseDisplay;
