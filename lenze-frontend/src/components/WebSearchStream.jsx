import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import SearchForm from './SearchForm';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://localhost:8000';

const useQuery = () => {
    return new URLSearchParams(useLocation().search);
};

const WebSearchStream = () => {
    const { sessionId } = useParams();
    const query = useQuery().get('query');
    const navigate = useNavigate();
    const responseRef = useRef('');
    const [response, setResponse] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [isSearching, setIsSeaching] = useState(false);
    const [hasStartedStreaming, setHasStartedStreaming] = useState(false);
    const [relatedQueries, setRelatedQueries] = useState([]);
    const [timeTaken, setTimeTaken] = useState('');
    const [sources, setSources] = useState([]);
    const abortControllerRef = useRef(null);

    const handleSearch = useCallback((query) => {
        if (!sessionId) {
            alert('No session ID available.');
            return;
        };
        setIsSeaching(true);
        setHasStartedStreaming(false);
        

        responseRef.current = '';
        setResponse('');
        setRelatedQueries([]);
        setTimeTaken('');
        setSources([]);
        abortControllerRef.current = new AbortController();

        console.log(`Connecting to ${API_URL}/web-search-stream/${sessionId}?query=${encodeURIComponent(query)}`);

        fetchEventSource(`${API_URL}/web-search-stream/${sessionId}?query=${encodeURIComponent(query)}`, {
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
                    console.log("Related queries and time taken recieved")
                } else if (event.event === 'source') {
                    const sourcesData = JSON.parse(event.data);
                    setSources(sourcesData);
                    console.log("Sources received");
                    setIsSeaching(false)
                } else if (event.data) {
                    responseRef.current += event.data;
                    setResponse(responseRef.current);
                    setIsStreaming(true);
                    setHasStartedStreaming(true);
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
    }, [sessionId]);

    useEffect(() => {
        if (query) {
            handleSearch(query);
        }

        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [query, handleSearch]);

    return (
        <div>
            <h1>Web Search Stream</h1>
            <button onClick={() => navigate('/')}>Start New Session</button>
            <SearchForm onSearch={handleSearch} />
            {isSearching ? <p>Searching...</p> : <p></p>}
            {sources.length > 0 && (
                <div>
                    <h3>Sources</h3> {/* Heading for sources */}
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
            )}
            {hasStartedStreaming && <h3>Answer</h3>}
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
