// src/components/StreamAnswer.js
import React, { useEffect, useState } from 'react';
import { createEventSource } from '../api';

const StreamAnswer = ({ query }) => {
  const [responses, setResponses] = useState([]);

  useEffect(() => {
    if (!query) return;

    const handleNewMessage = (message) => {
      setResponses((prevResponses) => [...prevResponses, message]);
    };

    const handleError = (error) => {
      console.error("EventSource error:", error);
    };

    const eventSource = createEventSource(query, handleNewMessage, handleError);

    return () => {
      eventSource.close();
    };
  }, [query]);

  return (
    <div>
      <h2>Streamed Responses for: {query}</h2>
      <div>
        {responses.map((response, index) => (
          <p key={index}>{response}</p>
        ))}
      </div>
    </div>
  );
};

export default StreamAnswer;
