import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import SearchForm from './SearchForm';
import ResponseDisplay from './ResponseDisplay';
import RelatedQueries from './RelatedQueries';
import SourcesList from './SourcesList';
import './WebSearchStream.css';

const API_URL = 'http://localhost:8000';

const useQuery = () => {
    return new URLSearchParams(useLocation().search);
};

const WebSearchStream = () => {
    const { sessionId } = useParams();
    const query = useQuery().get('query');
    const navigate = useNavigate();
    const responseRef = useRef('');
    const hasSearchedRef = useRef(false); // Ref to track if the search has already been triggered
    const [response, setResponse] = useState('');
    const [previousConversations, setPreviousConversations] = useState([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [isSearching, setIsSeaching] = useState(false);
    const [hasStartedStreaming, setHasStartedStreaming] = useState(false);
    const [relatedQueries, setRelatedQueries] = useState([]);
    const [timeTaken, setTimeTaken] = useState('');
    const [sources, setSources] = useState([]);
    const [currentQuery, setCurrentQuery] = useState(query || '');
    const abortControllerRef = useRef(null);

    const fetchPreviousConversations = useCallback(async () => {
        if (!sessionId) return;
        try {
            const response = await fetch(`${API_URL}/conversations/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setPreviousConversations(data);
            } else {
                console.error('Failed to fetch previous conversations');
            }
        } catch (error) {
            console.error('Error fetching previous conversations:', error);
        }
    }, [sessionId]);

    const handleSearch = useCallback(async (query) => {
        if (!sessionId) {
            alert('No session ID available.');
            return;
        }

        setCurrentQuery(query);
        setIsSeaching(true);
        setHasStartedStreaming(false);
        responseRef.current = '';
        setResponse('');
        setRelatedQueries([]);
        setTimeTaken('');
        setSources([]);
        abortControllerRef.current = new AbortController();

        await fetchPreviousConversations();

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
                    console.log("Related queries and time taken received");
                } else if (event.event === 'source') {
                    const sourcesData = JSON.parse(event.data);
                    setSources(sourcesData);
                    console.log("Sources received");
                    setIsSeaching(false);
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
    }, [sessionId, fetchPreviousConversations]);

    useEffect(() => {
        if (query && !hasSearchedRef.current) {
            handleSearch(query);
            hasSearchedRef.current = true; // Mark the search as triggered
        }

        fetchPreviousConversations();

        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [query, handleSearch, fetchPreviousConversations]);

    return (
        <div className="web-search-container">
            <h1>Web Search</h1>
            {previousConversations.length > 0 && (
                <div>
                    <ul>
                        {previousConversations.map((conv, index) => (
                            <li key={index}>
                                <h2>{conv.query}</h2>
                                <h3>Answer</h3>
                                <ResponseDisplay className="response-display" response={conv.response} />
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {currentQuery && <h2>{currentQuery}</h2>}
            {isSearching && <p style={{ color: 'grey' }}>Searching...</p>}
            <SourcesList className="sources-list" sources={sources} />
            {hasStartedStreaming && <h3>Answer</h3>}
            {isStreaming && <p style={{ color: 'grey' }}>Streaming response...</p>}
            <ResponseDisplay className="response-display" response={response} />
            <RelatedQueries className="related-queries" queries={relatedQueries} />
            {timeTaken && <p style={{ color: 'grey' }}>{timeTaken}</p>}
            <SearchForm className="search-form" onSearch={handleSearch} />
            <button onClick={() => navigate('/')}>Start New Session</button>
            <button onClick={() => navigate('/history')}>View Search History</button>
        </div>
    );
};

export default WebSearchStream;
