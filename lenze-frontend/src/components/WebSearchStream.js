import React, { useState, useEffect, useRef } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import SearchForm from './SearchForm';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://localhost:8000';

const WebSearchStream = () => {
  const responseRef = useRef('');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [hasStartedStreaming, setHasStartedStreaming] = useState(false); // New state to track if streaming has started
  const [relatedQueries, setRelatedQueries] = useState([]);
  const [timeTaken, setTimeTaken] = useState('');
  const abortControllerRef = useRef(null);

  const handleSearch = (query) => {
    responseRef.current = '';
    setResponse('');
    setRelatedQueries([]);
    setTimeTaken('');
    setIsStreaming(true);
    setHasStartedStreaming(true); // Set to true when streaming starts
    abortControllerRef.current = new AbortController();

    console.log(`Connecting to ${API_URL}/web-search-stream?query=${encodeURIComponent(query)}`);

    fetchEventSource(`${API_URL}/web-search-stream?query=${encodeURIComponent(query)}`, {
      method: "POST",
      headers: { Accept: "text/event-stream" },
      signal: abortControllerRef.current.signal,
      onopen(response) {
        console.log('Connection to stream opened');
        if (response.ok && response.status === 200) {
          console.log('Connected!');
        } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
          console.error(`Client side error: ${response.status}`);
          throw new Error('Client side error');
        }
      },
      onmessage(event) {
        console.log('Message received:', event.data);
        if (event.event === 'finaljson') {
          const finalData = JSON.parse(event.data);
          setRelatedQueries(finalData.related);
          setTimeTaken(finalData.time_taken);
          setIsStreaming(false);
        } else if (event.data) {
          responseRef.current += event.data;
          setResponse(responseRef.current);  // Update state to trigger re-render
        }
      },
      onclose() {
        console.log('Connection to stream closed');
        setIsStreaming(false);
      },
      onerror(err) {
        console.error('EventSource error:', err);
        abortControllerRef.current.abort();
        setIsStreaming(false);
      },
    });
  };

  useEffect(() => {
    // Cleanup EventSource on component unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div>
      <h1>Web Search Stream</h1>
      <SearchForm onSearch={handleSearch} />
      {hasStartedStreaming && <h2>Answer</h2>} 
      {isStreaming ? <p>Streaming response...</p> : <p></p>}
      <div style={{ 
        whiteSpace: 'normal', 
        wordBreak: 'break-word', 
        hyphens: 'auto',
        overflowWrap: 'break-word'
      }}>
        <ReactMarkdown>{response}</ReactMarkdown>
      </div>
      {relatedQueries.length > 0 && (
        <div>
          <h3>Related</h3>
          <ul>
            {relatedQueries.map((query, index) => (
              <li key={index}>{query}</li>
            ))}
          </ul>
        </div>
      )}
      {timeTaken && <p>{timeTaken}</p>}
    </div>
  );
};

export default WebSearchStream;
